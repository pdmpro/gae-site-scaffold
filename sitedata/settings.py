# global site settings

from datetime import datetime, date

content_path = "content/"
prod_domain = "YOUR_SITE.org"

paths = {  # note to self: no trailing slashes here please
    "blog": "/blog",
    "whatever": "/something-else",
    "images": "/images",
    "articleImages": "/images/article-images"
}

brand_colors = {
    "somecolor": "#666",
    "yourcolor": "#333",
    "yourothercolor": "#9c9c9c"
}

django_context = {
    "prod_domain": prod_domain,
    "prodUrl": "https://{}".format(prod_domain),
    "ga_id": "G-SOME_GOOG_ANALYTICS_ID",
    "cachebuster": "commerce,tx",
    "siteTitle": "AustinProduct.Pro",
    "copyrightStart": "2020",
    "copyrightEnd": datetime.now().year,
    "accentColor_1": brand_colors["yourcolor"],
    "accentColor_2": brand_colors["yourothercolor"],
    "accentColor_3": brand_colors["somecolor"],
    "linkColor_main": brand_colors["yourothercolor"],
    "linkColor_hover": brand_colors["yourcolor"],
    "bodyFont": "Merriweather",
    "bodyFontAlt": "'New York', 'Times New Roman', serif",
    "headingFont": "'Helvetica Neue'",
    "headingFontAlt": "Roboto, sans-serif",
    "monoFont": "Consolas", \
    "paths": paths,
}
