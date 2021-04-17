#!/usr/bin/python
# -*- coding: latin-1 -*-

"""
Concrete request handlers and stuff to support them.
"""

import os
import logging
import webapp2
import json
from datetime import datetime, date
from google.appengine.ext.webapp import template, util
from google.appengine.api import urlfetch
import abspath
import data


# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
# abstractions and shared functions
# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####

class AbstractRequestHandler(webapp2.RequestHandler):
    # convenience class for very common operations needed in RequestHandler responses
    def initialize(self, request, response):
        # extends the usual initializer to do common tasks (at least one)
        super(AbstractRequestHandler, self).initialize(request, response)
        prod_domain = "YOUR.FQDN"
        self.context = {
            "hostname": self.request.host,
            "prod_domain": prod_domain,
            "prodUrl": "https://{}".format(prod_domain),
            "onDevEnv": not self.request.host.lower().startswith(prod_domain),
            "copyrightStart": "1066",
            "copyrightEnd": datetime.now().year,  # look, you never need to update your copyright notices!
            "accentColor_1": "#fedcba",
            "accentColor_2": "#012345",
            "linkColor_main": "#6789a",
            "linkColor_hover": "#aabbcc",
            "danger_color": "#ff7001",
            "success_color": "#75c181",
            "bodyFont": "Roboto",
            "headingFont": "Merriweather",
            "monoFont": "Consolas",
            "googleAnalyticsId": "UA-91676111-2",
            "googleTagManagerId": "GTM-KZV564T",
            "cachebuster": "001"  # tricky little doodad that busts an overaggressive mobile device cache of static assets
        }

    def log_and_write(self, msg):
        logging.info(msg)
        self.response.out.write(msg)

    def get_path(self, filename):
        if ("." not in filename):
            # if the filename has no dots, it has no extension; therefore, append a default
            filename = "{fn}{ext}".format(fn=filename, ext=".django.html")
        filepath = os.path.join(abspath.root, filename)
        return filepath

    def respond(self, partial_filename):
        # partial_filename is the page ID
        # this writes out the HTML, so it should generally be the last thing called
        self.context["pageId"] = partial_filename
        if "pageName" not in self.context:
            self.context["pageName"] = self.context["pageId"].capitalize()
        content = template.render(self.get_path("page-{}".format(partial_filename)), self.context)
        self.response.out.write(content)

def do_http_get(url):
    # grabs a remote URL using GAE's urlfetch; only supports GET in this incarnation
    ret = {
        "url": url,
        "content": None,
        "status_code": -1,  # magic numbers are fun!!!
        "err": None
    }
    try:
        result = urlfetch.fetch(url)
        ret["status_code"] = result.status_code
        if result.status_code == 200:
            ret["content"] = result.content
        else:
            pass  # we don't care, but you can maybe log something if you like
    except urlfetch.Error:
        ret["content"] = "error (often an unreachable host): {0}".format(urlfetch.Error)
        ret["err"] = urlfetch.Error
    return ret


# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
# handlers for the usual web content
# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####

class HomePage(AbstractRequestHandler):
    def get(self):
        # injectedContent: an option to demonstrate injecting additional data/content into a given page
        self.context["injectedContent"] = data.injections
        self.respond("home")

class SubPage(AbstractRequestHandler):
    def get(self, path):
        self.respond(path)

class SomeSpecialPage(SubPage):
    def get(self, path):
        self.context["pageName"] = "I'm special, but really just a subpage"
        self.respond(path)

class FourOhFour(AbstractRequestHandler):
    def get(self, path):
        logging.error("{marker}404 for path {p}".format(marker=">>>>> " * 3, p=path))
        self.context["pageName"] = "Oops"
        self.error(404)
        self.respond("404")

class CSSFile(AbstractRequestHandler):
    # allows us to use variables in the CSS file without preprocessers like SASS or LESS, because I don't wanna.
    # please note that I'm not sure whether files created this way get cached. use at your own risk.
    def get(self, path):
        self.response.headers["Content-Type"] = "text/css"
        self.respond("css-{}.django.css".format(path))


# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
# specials
# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####

class PingThing(AbstractRequestHandler):
    # a little tool I wrote to request a URL (of my very low-trafficked sites) in order to keep them awake.
    # meant to be called by cron.
    def get(self):
        # here's the keep-alive
        # note that is simply writes text to the output for debugging.
        urls = [
            "YOUR_FULL_URL_1",
            "YOUR_FULL_URL_2",  # and so on... but don't go nuts or you'll speed past your account limits
        ]
        self.response.headers["Content-Type"] = "text/plain"
        self.log_and_write("starting URL pings\n-----\n\n")
        for url in urls:
            self.log_and_write("trying %s\n" % url)
            result = do_http_get(url)
            if result["err"]:
                self.log_and_write("    OOPS: {0}\n\n".format(result["content"]))
            else:
                self.log_and_write("    status code:{0}, length:{1}\n\n".format(result["status_code"], len(result["content"])))
        self.log_and_write("-----\ndone with URL pings")



# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
# ROUTING TABLE
# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####

app = webapp2.WSGIApplication([
    (r"/?", HomePage),
    (r"/([\w_-]+)/?", SubPage), # this demonstrates how to host a wide variety of pages without
                                # having a routing table entry for each one. the SubPage class will
                                # be passed the URL path and act accordingly. This regex pattern would
                                # prevent "folders" under the root (or any nested file structure), so
                                # adapt it accordingly.

    # non-HTML
    (r"/css/([\w_-]+).css", CSSFile),

    # specials
    (r"/sitepinger", PingThing),
    (r"/temporary/(FOOtest)/?", SubPage),   # let's say you want a temporary test page to be served
                                            # from /temporary/FOOtest. This passes 'FOOtest' to the handler.
                                            # you can always choose a different, more specialized handler.

    # if we get here, it's a 404
    (r"(.*)", FourOhFour),
], debug=True)
