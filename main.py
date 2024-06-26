import os
import random
import re
import shutil
import time
from io import BytesIO
from os import environ
from datetime import datetime
import requests
import urlexpander
import validators
from bs4 import BeautifulSoup
from flask import (
    Flask,
    Response,
    render_template,
    request,
    send_file,
    stream_with_context,
)
from PIL import Image
from selenium import webdriver

from htmlcss import cssContent, htmlContent
from utils import (
    get_description,
    get_favicon,
    get_image,
    get_site_name,
    get_theme_color,
    get_title,
    write_csv,
)

from pathlib import Path

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", message="")


@app.route("/download/", methods=["POST"])
def download():
    os.environ["http_proxy"] = ""
    os.environ["HTTP_PROXY"] = ""
    os.environ["https_proxy"] = ""
    os.environ["HTTPS_PROXY"] = ""
    del os.environ["http_proxy"]
    del os.environ["https_proxy"]
    del os.environ["HTTP_PROXY"]
    del os.environ["HTTPS_PROXY"]
    return send_file("cards.zip", as_attachment=True, download_name="cards.zip")


@app.route("/manual_download/", methods=["GET"])
def manual_download():
    if os.path.isdir("extractedImgs"):
        shutil.make_archive("cards", "zip", "extractedImgs")
    if not os.path.exists("cards.zip"):
        return "Whoops, something went wrong."
    if os.path.exists("processing.txt"):
        os.remove("processing.txt")
    os.environ["http_proxy"] = ""
    os.environ["HTTP_PROXY"] = ""
    os.environ["https_proxy"] = ""
    os.environ["HTTPS_PROXY"] = ""
    del os.environ["http_proxy"]
    del os.environ["https_proxy"]
    del os.environ["HTTP_PROXY"]
    del os.environ["HTTPS_PROXY"]
    return send_file("cards.zip", as_attachment=True, download_name="cards.zip")


@app.route("/reset/", methods=["GET"])
def reset():
    if os.path.isdir("extractedImgs"):
        shutil.rmtree("extractedImgs")
    if os.path.exists("cards.zip"):
        os.remove("cards.zip")
    os.environ["http_proxy"] = ""
    os.environ["HTTP_PROXY"] = ""
    os.environ["https_proxy"] = ""
    os.environ["HTTPS_PROXY"] = ""
    del os.environ["http_proxy"]
    del os.environ["https_proxy"]
    del os.environ["HTTP_PROXY"]
    del os.environ["HTTPS_PROXY"]
    return "App has been reset."


@app.route("/status/", methods=["POST"])
def status():
    def generate():
        msg = "<p>If you want to generate cards manually, visit <a href='https://metatags.io/' target='_blank'>metatags.io</a> or <a href='https://socialsharepreview.com' target='_blank'>socialsharepreview.com</a>.</p><p>A download button will appear at the bottom of the page when all URLs have been processed. But if you want to terminate the app and download the URLs/cards that have already been processed, click <a href='/manual_download/'>here</a>.</p>"
        text = request.form["text"]
        putInDifferentHeadline = 1 if request.form.get("replaceHeadline") else 0
        deleteTheSource = 1 if request.form.get("removeSource") else 0
        redcFontSize = 1 if request.form.get("reduceFont") else 0
        putDiffImg = 1 if request.form.get("replaceImages") else 0
        if not text:
            yield f"Please provide URLs.{msg}"
            return None
        if os.path.exists("processing.txt"):
            yield "Someone else might be using the app right now. Try again later."
            return None

        yield "Initializing..." + msg

        with open("processing.txt", "w") as f:
            f.write("App is running...")

        # implicit waits and parallelization
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = (
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        )
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("enable-automation")
        driver = webdriver.Chrome(options=chrome_options)
        resp = requests.get(
            "https://proxy.webshare.io/api/proxy/list/",
            headers={"Authorization": "b85sk4kdfdsf"},
        )
        proxies = resp.json()["results"]
        driver.implicitly_wait(5)
        x = 3840
        y = x / 16 * 10
        cssContent3 = cssContent
        if redcFontSize == 1:
            cssContent2 = cssContent.replace(
                "facebook__title{font-size:14px;line-height:20px}",
                "facebook__title{font-size:10px;line-height:20px}",
            )
            cssContent3 = cssContent2.replace(
                "facebook__description{border-collapse:separate;color:#606770;direction:ltr;display:-webkit-box;font-family:Helvetica, Arial, sans-serif;font-size:12px;height:16px;line-height:20px;",
                "facebook__description{border-collapse:separate;color:#606770;direction:ltr;display:-webkit-box;font-family:Helvetica, Arial, sans-serif;font-size:8px;height:12px;line-height:20px;",
            )
        with open("blankCSS.css", "w") as outF:
            outF.write(cssContent3)
        driver.set_window_size(x, y)
        driver.delete_all_cookies()

        if os.path.isdir("extractedImgs"):
            shutil.rmtree("extractedImgs")
        if os.path.exists("cards.zip"):
            os.remove("cards.zip")
        os.mkdir("extractedImgs", 0o777)

        headlines = text.splitlines()
        headlines = list(filter(None, headlines))
        headlines = list(set(headlines))
        headlines_new = [hl for hl in headlines if validators.url(hl.split("\t")[0])]
        headlines = headlines_new
        if not headlines:
            yield "<br>Please provide valid URLs.<br>"
            return None
        random.shuffle(headlines)
        yield f"Processing {len(headlines)} unique urls<br><br>"
        for i, h in enumerate(headlines, start=1):
            if len(h.split("\t")) == 0:
                substituteH = ""
                substituteImg = ""
            elif len(h.split("\t")) == 1:
                substituteH = ""
                substituteImg = ""
            elif len(h.split("\t")) == 2:
                if putInDifferentHeadline == 1:
                    substituteH = h.split("\t")[-1]
                    substituteImg = ""
                if putDiffImg == 1:
                    substituteH = ""
                    substituteImg = h.split("\t")[-1]
            elif len(h.split("\t")) >= 3:
                substituteH = h.split("\t")[1]
                substituteImg = h.split("\t")[2]
            h = h.split("\t")[0].strip().strip("/")  # clean up url
            yield f"Processing url {i} of {len(headlines)}: {h}<br>"
            print(i, h)

            for _ in range(1):
                time.sleep(2)
                yield "."
            # set proxy
            k = random.randint(0, len(proxies) - 1)
            p = proxies[k]
            print(f"{k}, {p['proxy_address']}")
            prox = f"http://{p['username']}:{p['password']}@{p['proxy_address']}:{p['ports']['http']}"
            os.environ["http_proxy"] = prox
            os.environ["HTTP_PROXY"] = prox
            os.environ["https_proxy"] = prox
            os.environ["HTTPS_PROXY"] = prox

            headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Max-Age": "3600",
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
            }
            req = requests.get(h, headers)
            for _ in range(1):
                time.sleep(2)
                yield "."
            print(req.status_code)
            if req.status_code == 200:
                soup = BeautifulSoup(req.content, "html.parser")
            else:
                driver.get(h)
                for _ in range(5):
                    time.sleep(1)
                    yield "."
                req = driver.page_source
                soup = BeautifulSoup(req, "html.parser")
            try:
                metadata = {
                    "title": get_title(soup),
                    "description": get_description(soup),
                    "image": get_image(soup, h),
                    "favicon": get_favicon(soup, h),
                    "sitename": get_site_name(soup, h),
                    "color": get_theme_color(soup),
                    "url": h,
                }
            except:
                metadata = {
                    "title": "EXCEPTION",
                    "description": "EXCEPTION",
                    "image": "EXCEPTION",
                    "favicon": "EXCEPTION",
                    "sitename": "EXCEPTION",
                    "color": "EXCEPTION",
                    "url": h,
                }
            print(metadata["title"])
            print(metadata["description"])
            print(metadata["image"])
            if putInDifferentHeadline == 0:
                htmlContent2 = htmlContent.replace("REPLACE_TITLE", metadata["title"])
            else:
                htmlContent2 = htmlContent.replace("REPLACE_TITLE", substituteH)

            if putDiffImg == 1:
                metadata["image"] = substituteImg
            if isinstance(metadata["description"], list):
                if len(metadata["description"]) >= 1:
                    htmlContent2 = htmlContent2.replace(
                        "REPLACE_DESC", metadata["description"][0]
                    )
                else:
                    htmlContent2 = htmlContent2.replace("REPLACE_DESC", " ")
            else:
                htmlContent2 = htmlContent2.replace(
                    "REPLACE_DESC", metadata["description"]
                )
            if deleteTheSource == 0:
                htmlContent2 = htmlContent2.replace(
                    "REPLACE_SITE", urlexpander.get_domain(h)
                )
            else:
                htmlContent2 = htmlContent2.replace("REPLACE_SITE", " ")
            if os.path.exists("tempImage.png"):
                os.remove("tempImage.png")
            if validators.url(metadata["image"]):
                Picture_request = requests.get(metadata["image"])
                with open("tempImage.png", "wb") as f3:
                    f3.write(Picture_request.content)
                if putDiffImg == 1:
                    tempContent = Image.open("tempImage.png")
                    tempContent2 = tempContent.crop(
                        (0, 0, tempContent.width, 0.7 * tempContent.height)
                    )
                    tempContent2.save("tempImage.png", "png")
                htmlContent2 = htmlContent2.replace(
                    "REPLACE_IMAGE", "file:///" + os.getcwd() + "//tempImage.png"
                )
            else:
                htmlContent2 = htmlContent2.replace("REPLACE_IMAGE", metadata["image"])
            with open("blank.html", "w") as outF2:
                outF2.write(htmlContent2)
            driver.get("file:///" + os.getcwd() + "//blank.html")
            driver.execute_script("document.body.style.zoom = '150%'")
            for _ in range(5):
                time.sleep(1)
                yield "."

            im = driver.get_screenshot_as_png()
            im = Image.open(BytesIO(im))
            # im1 = im.crop((0, 0, x * 0.20235, x * 0.1377))
            area = (10, 10, 1490, 1000)
            im1 = im.crop(area)
            # im1 = ImageOps.expand(im1, border=5, fill=(255, 255, 255))

            # get image title name
            title = metadata["title"]
            title = re.sub(r"\W+", " ", title)
            title = re.sub(r" \w ", " ", title).strip()
            title = title.replace(" ", "-")[:100].lower()

            if len(title) < 3:  # in case there are problems with the title text
                name = (h.split("?")[0].split("/")[-1]).replace(".html", "")
                filename = name + ".jpg"
            else:
                filename = title + ".jpg"
            if putInDifferentHeadline == 1:
                filename = substituteH + ".jpg"
            rgb_im = im1.convert("RGB")
            new_width = int(rgb_im.width // 2)
            new_height = int(rgb_im.height // 2)
            rgb_im = rgb_im.resize((new_width, new_height), Image.LANCZOS)
            rgb_im.save("extractedImgs/" + filename, optimize=True, quality=60)

            yield f"<br>Output: {filename}<br><br>"

            if i == len(headlines):
                yield "<br>Done. cards.zip is ready for download. See <strong>_cards_.csv</strong> in the zipped folder for details.<br>"

            mode = "w" if i == 1 else "a"
            write_csv(
                header=["source_url", "filename", "retrieve_date", "headline"],
                data=zip(
                    [h],
                    [filename],
                    [datetime.now().strftime("%Y-%m-%d")],
                    [metadata["title"]],
                ),
                path=os.path.join("extractedImgs", "_cards_.csv"),
                mode=mode,
            )

        driver.quit()
        shutil.make_archive("cards", "zip", "extractedImgs")
        shutil.rmtree("extractedImgs")
        yield render_template("index2.html")

    return Response(stream_with_context(generate()))


if __name__ == "__main__":
    p = Path("processing.txt")
    if p.exists():
        p.unlink()
    app.run(debug=True, host="0.0.0.0", port=environ.get("PORT", 1313))
