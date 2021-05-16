# gae-site-scaffold

A starter kit for websites using Google AppEngine in Python.

I've been using GAE to host a dozen sites since 2014 and haven't paid a cent,
so that's kinda nice. (Granted, they're *very* low-traffic.)

This scaffold will give you an especially quick start if you want a simple
static website. It's also a springboard to making full-blown web apps on GAE.

## Built with
  * Bootstrap 3
  * jQuery 1.12
  * Python 2.7
  * GAE's built-in version of Django

Yes, **some of these versions are rather old**. I'm considering that a known
issue to possibly be fixed in a future update.

### Not built with
This is free of LESS or SASS or CoffeeScript or preprocessors or transpilers.
I have nothing against those things, apart from the fact that I haven't learned them.
My approach to modularity is to take advantage of Django
-- see the explanation of dynamic CSS below.

## Getting started
As a prerequisite, you'll need to understand Google AppEngine development
basics, including use of the `gcloud` CLI tool. Use their Python tutorials
to get Hello World going, and the rest of this will be easy peasy.

## Directory structure

`app.yaml` is the granddaddy that sets up the scaffolding's directory structure and annoints `content.py` as the file that generates the site content.

### Static directories
I like to keep my static assets in folders (but not deeply nested):
* `/icons` -- fancy site icons (like Apple Touch)
* `/images` -- anything that goes in an `<img>` tag
* `/js` -- static JavaScript
* `/media` -- downloadable stuff (like PDFs)

### Dynamic CSS
So where's the CSS directory? As mentioned above, I'm not using preprocessors despite
the fact that I cherish modularity and the DRY concept. Instead, I leverage GAE's
template engine. Because of how my scaffolding assembles content, it's a little easier
to put the CSS in the root directory, where the HTML content is.

(You can easily tweak `app.yaml` if you want to have your CSS elsewhere -- I just
didn't bother with it.)

Note that this same approach can be taken with JavaScript files, as a substitute for
transpilation.

## How pages get assembled
The files that contain HTML content are in the root directory following this
convention: `page-*-django.html`

> **IMPORTANT NOTE:** just because the HTML files are in the root directory doesn't mean the URLs to your pages can't have any directory structure. URL patterns are controlled by the routing table in `content.py` and are decoupled from the directory structure in GAE's webapp2 framework.

However, these pages incorporate common stuff like headers and footers using the
`{% include %}` template tag.
I keep those wrap pieces in the `/pieces` directory, but you can put them anywhere.

### In `pieces`
The wrap pieces are named logically, but I prepend them with numbers to force them to sort nicely. So, each `page-*-django.html` will load some or all of the wrap in this order:
* `1-head` -- the `<head>` tag, but also the **opening** `<body>` tag
* `2-navbar` -- site navigation
* `3-page-header` --  the visible page header
* `5-footer` -- the visible footer
* `6-bottom` -- JavaScript includes and other bottom bits, including `</body>`

(`4-NOTHING` isn't in use, but I wanted a placeholder there for some reason.)

You can put anything you want in the `pieces` directory, or you can move all that
stuff to the root by changing the `{% include %}` tags. But, keeping the wrap
components separate from the real content files makes editing the interesting stuff
easier.

#### Injections
This scaffolding also demonstrates how to inject data-driven content into this basic template structure. In this case, `data.py` acts as a database; `content.py` reads it into the Django context; the `page-*-django.html` includes `/content/content-injections.html`; and that file displays the dynamic content.

## Keeping going
From there, it's all just basic Bootstrap-powered web development.
Or, throw the Bootstrap away and use whatever you like.

## Known issues/enhancement wishlist
You may find various FIXMEs and TODOs in the source code. Additionally:
* **Referrer spam** is a major problem for site administrators using Google Analytics and the like to analyze traffic. An older version of my scaffolding largely solves that, and I plan to port that here in the future.
* **Python 3:** It should be pretty easy to switch this all to 3. So, that's on my list too.
* **Client-side updates:** as long as these versions of Bootstrap and jQuery work in my tests.
* **Accessibility:** I haven't tested this for accessibility in a while, but I hope to do so again in the near term.
* **Downlevel browser support:** I've made absolutely no attempt to have my sites render nicely in IE 8 or any other prehistoric stone tablet viewer. I still have too many scars from coding through the 90s/2000s browser wars to care a lot. Backwards compatibility is left as an exercise to the reader.

## License

Released under the MIT license.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
