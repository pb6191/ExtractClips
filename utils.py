import csv

# reference - https://hackersandslackers.com/scraping-urls-with-beautifulsoup/
def get_title(html):
    """Scrape page title."""
    title = "None"
    if html.find("meta", property="og:title"):
        title = html.find("meta", property="og:title").get("content")
        print("title path 1")
    elif html.title.string:
        title = html.title.string
        print("title path 2")
    elif html.find("meta", property="twitter:title"):
        title = html.find("meta", property="twitter:title").get("content")
        print("title path 3")
    elif html.find("h1"):
        title = html.find("h1").string
        print("title path 4")
    return title


def get_description(html):
    """Scrape page description."""
    description = "None"
    if html.find("meta", property="og:description"):
        description = html.find("meta", property="og:description").get("content")
        print("desc path 1")
    elif html.find("meta", property="description"):
        description = html.find("meta", property="description").get("content")
        print("desc path 2")
    elif html.find("meta", property="twitter:description"):
        description = html.find("meta", property="twitter:description").get("content")
        print("desc path 3")
    elif html.find("p"):
        description = html.find("p").contents
        print("desc path 4")
    return description


def get_image(html, url):
    """Scrape share image."""
    image = "None"
    if "realrawnews" in url:
        print("init img path 5")
        image = (
            url.split("//")[0]
            + "//"
            + url.split("//")[1].split("/")[0]
            + html.find("figure").img.get("src")
        )
        print("img path 5")
    elif html.find("meta", property="og:image"):
        image = html.find("meta", property="og:image").get("content")
        print("img path 1")
    elif html.find("meta", property="image"):
        image = html.find("meta", property="image").get("content")
        print("img path 2")
    elif html.find("meta", property="twitter:image"):
        image = html.find("meta", property="twitter:image").get("content")
        print("img path 3")
    elif html.find("img", src=True):
        image = html.find_all("img").get("src")
        print("img path 4")
    return image


def get_site_name(html, url):
    """Scrape site name."""
    if html.find("meta", property="og:site_name"):
        site_name = html.find("meta", property="og:site_name").get("content")
    elif html.find("meta", property="twitter:title"):
        site_name = html.find("meta", property="twitter:title").get("content")
    else:
        site_name = url.split("//")[1]
        return site_name.split("/")[0].rsplit(".")[1].capitalize()
    return site_name


def get_favicon(html, url):
    """Scrape favicon."""
    if html.find("link", attrs={"rel": "icon"}):
        return html.find("link", attrs={"rel": "icon"}).get("href")
    elif html.find("link", attrs={"rel": "shortcut icon"}):
        return html.find("link", attrs={"rel": "shortcut icon"}).get("href")
    else:
        return f'{url.rstrip("/")}/favicon.ico'


def get_theme_color(html):
    """Scrape brand color."""
    if html.find("meta", property="theme-color"):
        return html.find("meta", property="theme-color").get("content")
    return "None"


def write_csv(header, data, path, mode):
    with open(path, mode, encoding="utf-8") as f:
        writer = csv.writer(f)
        if mode == "w":
            writer.writerow(header)
        writer.writerows(data)
