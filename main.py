import os
import shutil
import time
from io import BytesIO
from os import environ
import csv
import re

from flask import (
    Flask,
    Response,
    render_template,
    request,
    send_file,
    stream_with_context,
)
from PIL import Image, ImageOps
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", message="")


@app.route("/download/", methods=["POST"])
def download():
    os.remove("processing.txt")
    return send_file("cards.zip", as_attachment=True, download_name="cards.zip")


@app.route("/manual_download/", methods=["GET"])
def manual_download():
    if os.path.isdir("extractedImgs"):
        shutil.make_archive("cards", "zip", "extractedImgs")
    if os.path.exists("cards.zip"):
        return send_file("cards.zip", as_attachment=True, download_name="cards.zip")
    else:
        return "Whoops, something went wrong."


@app.route("/reset/", methods=["GET"])
def reset():
    if os.path.isdir("extractedImgs"):
        shutil.rmtree("extractedImgs")
    if os.path.exists("cards.zip"):
        os.remove("cards.zip")
    if os.path.exists("processing.txt"):
        os.remove("processing.txt")
    return "App has been reset."


def write_csv(header, data, path, mode):
    with open(path, mode) as f:
        writer = csv.writer(f)
        if mode == "w":
            writer.writerow(header)
        writer.writerows(data)


@app.route("/status/", methods=["POST"])
def status():
    def generate():
        msg = "<p>If you want to generate cards manually, visit <a href='https://metatags.io/' target='_blank'>metatags.io</a> or <a href='https://socialsharepreview.com' target='_blank'>socialsharepreview.com</a>.</p><p>A download button will appear at the bottom of the page when all URLs have been processed. But if you want to terminate the app and download the URLs/cards that have already been processed, click <a href='/manual_download/'>here</a>.</p>"
        text = request.form["text"]
        if not text:
            yield "Please provide URLs." + msg
            return None
        if os.path.exists("processing.txt"):
            yield "Someone else might be using the app right now. Try again later."
            return None

        yield "Initializing..." + msg

        with open("processing.txt", "w") as f:
            f.write("App is running...")

        # implicit waits and parallelization
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("enable-automation")
        driver = webdriver.Chrome(
            executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options
        )
        driver.implicitly_wait(5)
        x = 3840
        y = x / 16 * 10
        driver.set_window_size(x, y)
        driver.delete_all_cookies()
        url = "https://metatags.io/"
        driver.get(url)
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[contains(@class, 'search')]")
            )
        )
        time.sleep(5)
        driver.execute_script("document.body.style.zoom = '150%'")
        driver.execute_script(
            """
            const fbElement = document.querySelector("div.card-seo-facebook");
            fbElement.style = "border-radius:5.99998px";
            const ipElement = document.querySelector("section.nav-search");
            document.body.innerHTML = "";
            document.body.appendChild(fbElement);
            document.body.appendChild(ipElement);
            """
        )

        if os.path.isdir("extractedImgs"):
            shutil.rmtree("extractedImgs")
        if os.path.exists("cards.zip"):
            os.remove("cards.zip")
        os.mkdir("extractedImgs", 0o777)

        headlines = text.splitlines()
        headlines = list(filter(None, headlines))
        headlines = list(set(headlines))
        yield f"Processing {len(headlines)} unique urls<br><br>"
        for i, h in enumerate(headlines, start=1):
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '3600',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
                }
            req = requests.get(h, headers)
            soup = BeautifulSoup(req.content, 'html.parser')
            metadata = {
                'title': get_title(soup),
                'description': get_description(soup),
                'image': get_image(soup),
                'favicon': get_favicon(soup, h),
                'sitename': get_site_name(soup, h),
                'color': get_theme_color(soup),
                'url': h
                }
            print(metadata.title)
            print(metadata.description)
            print(metadata.sitename)
            h = h.strip().strip("/")
            print(i, h)
            yield f"Processing url {i} of {len(headlines)}: {h}<br>"
            driver.find_element(By.XPATH, "//input[contains(@class, 'search')]").clear()
            driver.find_element(
                By.XPATH, "//input[contains(@class, 'search')]"
            ).send_keys(h)
            driver.find_element(
                By.XPATH, "//input[contains(@class, 'search')]"
            ).send_keys(Keys.RETURN)
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@class = 'card-seo-facebook']")
                )
            )
            time.sleep(10)

            im = driver.get_screenshot_as_png()
            im = Image.open(BytesIO(im))
            im1 = im.crop((0, 0, x / 5.12, x / 7.524))
            im1 = ImageOps.expand(im1, border=5, fill=(255, 255, 255))

            # get image title name
            title = driver.find_element(
                By.XPATH, "/html/body/div/div[2]/div/div/div"
            ).text
            title = re.sub(r"\W+", " ", title)
            title = re.sub(r" \w ", " ", title).strip()
            title = title.replace(" ", "-")[:100].lower()

            if len(title) < 3:  # in case there are problems with the title text
                name = (h.split("?")[0].split("/")[-1]).replace(".html", "")
                filename = name + ".png"
            else:
                filename = title + ".png"
            im1.save("extractedImgs/" + filename, "png")

            yield f"Output: {filename}<br><br>"

            if i == len(headlines):
                yield "<br>Done. cards.zip is ready for download. See <strong>_cards_.csv</strong> in the zipped folder for details.<br>"
            else:
                time.sleep(1)

            mode = "w" if i == 1 else "a"
            write_csv(
                header=["url", "filename"],
                data=zip([h], [filename]),
                path=os.path.join("extractedImgs", "_cards_.csv"),
                mode=mode,
            )

        driver.quit()
        shutil.make_archive("cards", "zip", "extractedImgs")
        shutil.rmtree("extractedImgs")
        yield render_template("index2.html")

    return Response(stream_with_context(generate()))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=environ.get("PORT", 5000))


def get_title(html):
    """Scrape page title."""
    title = None
    if html.title.string:
        title = html.title.string
    elif html.find("meta", property="og:title"):
        title = html.find("meta", property="og:title").get('content')
    elif html.find("meta", property="twitter:title"):
        title = html.find("meta", property="twitter:title").get('content')
    elif html.find("h1"):
        title = html.find("h1").string
    return title


def get_description(html):
    """Scrape page description."""
    description = None
    if html.find("meta", property="description"):
        description = html.find("meta", property="description").get('content')
    elif html.find("meta", property="og:description"):
        description = html.find("meta", property="og:description").get('content')
    elif html.find("meta", property="twitter:description"):
        description = html.find("meta", property="twitter:description").get('content')
    elif html.find("p"):
        description = html.find("p").contents
    return description


def get_image(html):
    """Scrape share image."""
    image = None
    if html.find("meta", property="image"):
        image = html.find("meta", property="image").get('content')
    elif html.find("meta", property="og:image"):
        image = html.find("meta", property="og:image").get('content')
    elif html.find("meta", property="twitter:image"):
        image = html.find("meta", property="twitter:image").get('content')
    elif html.find("img", src=True):
        image = html.find_all("img").get('src')
    return image


def get_site_name(html, url):
    """Scrape site name."""
    if html.find("meta", property="og:site_name"):
        site_name = html.find("meta", property="og:site_name").get('content')
    elif html.find("meta", property='twitter:title'):
        site_name = html.find("meta", property="twitter:title").get('content')
    else:
        site_name = url.split('//')[1]
        return site_name.split('/')[0].rsplit('.')[1].capitalize()
    return sitename


def get_favicon(html, url):
    """Scrape favicon."""
    if html.find("link", attrs={"rel": "icon"}):
        favicon = html.find("link", attrs={"rel": "icon"}).get('href')
    elif html.find("link", attrs={"rel": "shortcut icon"}):
        favicon = html.find("link", attrs={"rel": "shortcut icon"}).get('href')
    else:
        favicon = f'{url.rstrip("/")}/favicon.ico'
    return favicon


def get_theme_color(html):
    """Scrape brand color."""
    if html.find("meta", property="theme-color"):
        color = html.find("meta", property="theme-color").get('content')
        return color
    return None