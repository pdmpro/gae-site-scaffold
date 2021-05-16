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
from google.appengine.ext import db, ndb
import yaml
import abspath
from utils import gflog
from sitedata import settings
# from articleDB import ArticleArbiter, ArticleDatabaseError, ArticleNotFoundError


# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
# shared datastore models
# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
class ReferralSpamSite(ndb.Model):
    site = ndb.StringProperty(required=True)
    createDate = ndb.DateTimeProperty(auto_now=True)


# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
# abstractions and shared functions
# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
class AbstractRequestHandler(webapp2.RequestHandler):
    # convenience class for very common operations needed in RequestHandler responses
    def initialize(self, request, response):
        # extends the usual initializer to do common tasks (at least one)
        super(AbstractRequestHandler, self).initialize(request, response)
        #set up the baseline context object for Django, including global site settings
        self.context = settings.django_context
        self.context["hostname"] = self.request.host
        self.context["onDevEnv"] = not self.request.host.lower().startswith(settings.django_context["prod_domain"])

    def get(self):
        # self.log("IN AbstractRequestHandler.get()")
        # check every visit for referrer spam
        referrer = self.request.referer # will be None if it's direct traffic; test with "rb-str.ru"
        if referrer:
            # massage the referrer to match what we save in the lookup table -- this leaves the port number as part of the domain, but I think that's fine
            referring_domain = referrer.lower().replace("https://", "").replace("http://", "").split('/')[0]
            if self.visitor_is_spammer(referring_domain):
                self.log("SENDING A 403: rejecting %s (spamming domain)" % (referrer))
                self.abort(403)

    def visitor_is_spammer(self, referring_domain):
        # this is to block referrer spam -- returns True if the domain is in our blacklist
        try:
            query = ReferralSpamSite.query(ReferralSpamSite.site == referring_domain)
            entity = query.get()
        except StandardError as e:
            self.log("ran into a fatal problem when querying the referral spam DB; does the correct entity exist? I have to allow the page load to proceed.\nError: %s" % e)
            entity = None
        return entity is not None

    def log(self, msg):
        gflog(msg)

    def log_and_write(self, msg):
        self.log(msg)
        self.response.out.write(msg)

    def get_path(self, filename):
        if ("." not in filename):
            # if the filename has no dots, it has no extension; therefore, append a default
            filename = "{fn}{ext}".format(fn=filename, ext=".django.html")
        filepath = os.path.join(abspath.root, filename)
        return filepath

    def get_page_data(self, sef_path):
        # get the corresponding page config YAML

        self.context["article"] = None
        # this ^^^ is to clear what seems to sometimes get stuck in memory as a module variable or something Django hangs on to. to repro: visit a post page, load the lbog list page or home page, observe that the OG meta tags are sill showing the previous context info from the article-specific view. yikes.

        with open("{}{}.yaml".format(settings.content_path, sef_path), "r") as f:
            page_specific_config = yaml.load(f)

        # build the context from the yaml
        self.context["pageSettings"] = page_specific_config
        self.context["title"] = page_specific_config["title"]
        self.context["abstract"] = page_specific_config["abstract"]

        # special setting for use in the meta tags
        if sef_path == "home":
            page_specific_config["sefPathForMeta"] = ""
        self.context["sefPathForMeta"] = page_specific_config["sefPathForMeta"]

        # hero background
        try:
            self.context["headerBackgroundUrl"] = "{root}/{path}".format(root=settings.paths["images"], path=page_specific_config["headerBackgroundUrl"])
        except KeyError:
            self.context["headerBackgroundUrl"] = "{root}/science-kit-1200w.jpg".format(root=settings.paths["images"])
        return page_specific_config

    def respond(self, partial_filename, filename_prefix=settings.content_path):
        # partial_filename is the page ID
        # this actually writes out the HTML, so it should generally be the last thing called
        self.context["sefPath"] = partial_filename
        if "title" not in self.context:
            self.context["title"] = self.context["sefPath"].capitalize()
        content = template.render(self.get_path("{prefix}{fn}".format(fn=partial_filename, prefix=filename_prefix)), self.context)
        self.response.out.write(content)


# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
# handlers for the usual web content
# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
class HomePage(AbstractRequestHandler):
    def get(self):
        super(HomePage, self).get()
        # self.context["testimonials"] = testimonials.quotations
        self.context["title"] = "Home"
        self.get_page_data("home")
        self.respond("home")

class SubPage(AbstractRequestHandler):
    def get(self):
        super(SubPage, self).get()
        self.get_page_data("YOUR_PAGE_ID")
        self.respond("YOUR_PAGE_ID")

class BlogListPage(AbstractRequestHandler):
    def get(self):
        super(BlogListPage, self).get()
        self.context["articles"] = ArticleArbiter.get_all()
        self.get_page_data("blog-list")  # this is not totes DRY
        self.respond("blog-list")

class BlogPostPage(AbstractRequestHandler):
    def get(self, path):
        super(BlogPostPage, self).get()
        path = path.lower()
        try:
            article = ArticleArbiter.get_one(path)
        except ArticleNotFoundError:
            # the article doesn't exist, so 404 it
            gflog("SENDING A 404: no article found for key %s" % (path))
            FourOhFour(self.request, self.response).get(path)
            return None
        self.context["article"] = article
        self.context["title"] = article["title"]  # duplicated because it needs to be in the <head>
        self.respond("blog-post")

class FourOhFour(AbstractRequestHandler):
    def get(self, path):
        super(FourOhFour, self).get()
        # logging.error("{marker}404 for path {p}".format(marker=">>>>> " * 3, p=path))
        self.context["title"] = "Oops"
        self.context["headerBackgroundUrl"] =  "{root}/science-kit-1200w.jpg".format(root=settings.paths["images"])
        self.error(404)
        self.respond("404")

class CSSFile(AbstractRequestHandler):
    # allows me to use variables in the CSS file without preprocessers like SASS or LESS, because I don't wanna
    def get(self, path):
        super(CSSFile, self).get()
        self.response.headers["Content-Type"] = "text/css"
        self.respond("{}.django.css".format(path), filename_prefix="css-")


# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
# specials
# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
class ReferrerSpamListUpdate(webapp2.RequestHandler):
    # updates the referral spammer list. meant to be called every 24 hours or so via cron.
    # Not checking permissions, though this can be an expensive procedure.
    def get(self):
        uriForReferrerList = "https://raw.githubusercontent.com/piwik/referrer-spam-blacklist/master/spammers.txt"
        gflog("referrer spam updater is requesting %s" % uriForReferrerList)
        result = urlfetch.fetch(uriForReferrerList)
        resultStatus = result.status_code
        if resultStatus == 200:
            referrers = result.content.splitlines()
            gflog("I got {count} items in its result, and will now delete all the entities and re-populate from this result".format(count=len(referrers)))
            ndb.delete_multi(
                ReferralSpamSite.query().fetch(keys_only=True)
            )
            for referrer in referrers:
                referrer = referrer.lower()
                thisEntity = ReferralSpamSite(site=referrer)
                thisEntity.put()
            #if we get here, we've presumably succeeded
            self.response.out.write("Apparently, I've successfully (re)populated the referrer spam site list.")
        else:
            gflog("Bad HTTP response ({code}) when asking for {u}".format(code=resultStatus, u=uriForReferrerList))
            self.response.out.write(self, "I failed to populate the referrer spam site list. Please check the logs.")


# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
# ROUTING TABLE
# #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
app = webapp2.WSGIApplication([
    # "top-level" pages (should be limited in number)
    (r"/?", HomePage),
    (r"/YOUR_PATH_HERE/?", SubPage),

    # the blog/other resources
    (r'/blog/?', BlogListPage),  # blog list page
    (r'/blog/(.+)', BlogPostPage),  # a blog post/other resource article, using the blog subsystem

    # non-HTML
    (r"/css/([\w_-]+).css", CSSFile),

    # refreshes the referral spam list; to be called by cron for the most part
    (r'/util/updatereferrerspamlist', ReferrerSpamListUpdate),

    # if we get here, it's a 404
    (r"(.*)", FourOhFour),
], debug=True)
