import os
import shutil
import time
from io import BytesIO
from os import environ
import csv

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
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", message="")


@app.route("/download/", methods=["POST"])
def download():
    return send_file("cards.zip", as_attachment=True, download_name="cards.zip")


def write_csv(header, data, path):
    with open(path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)


@app.route("/status/", methods=["POST"])
def status():
    def generate():
        msg = '<p>If you want to generate cards manually, visit <a href="https://metatags.io/">metatags.io</a> or <a href="https://socialsharepreview.com">socialsharepreview.com</a>.</p>'
        text = request.form["text"]
        if not text:
            yield "Please provide URLs." + msg
            return None
        yield "Initializing..." + msg

        # implicit waits and parallelization
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
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
        os.mkdir("extractedImgs", 0o777)

        headlines = text.splitlines()
        headlines = list(filter(None, headlines))
        headlines = list(set(headlines))
        filenames = []
        urls = []
        yield f"Processing {len(headlines)} unique urls<br><br>"
        for i, h in enumerate(headlines, start=1):
            h = h.strip().strip("/")
            print(i, h)
            yield f"Processing url {i} of {len(headlines)}: {h}<br>"
            driver.find_element(By.XPATH, "//input[contains(@class, 'search')]").clear()
            driver.find_element(
                By.XPATH, "//input[contains(@class, 'search')]"
            ).send_keys(h)
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@class = 'card-seo-facebook']")
                )
            )
            time.sleep(2)
            im = driver.get_screenshot_as_png()
            im = Image.open(BytesIO(im))
            im1 = im.crop((0, 0, x / 5.12, x / 7.524))
            im1 = ImageOps.expand(im1, border=5, fill=(255, 255, 255))
            filename = (h.split("/")[-1]).replace(".html", "") + ".png"
            im1.save("extractedImgs/" + filename, "png")

            filenames.append(filename)
            urls.append(h)

            yield f"Output: {filename}<br><br>"

            if i == len(headlines):
                yield "<br>Done. cards.zip is ready for download. See <strong>_cards_.csv</strong> in the zipped folder for details.<br>"
            else:
                time.sleep(1)

        write_csv(
            header=["url", "filename"],
            data=zip(urls, filenames),
            path=os.path.join("extractedImgs", "_cards_.csv"),
        )

        driver.quit()
        shutil.make_archive("cards", "zip", "extractedImgs")
        shutil.rmtree("extractedImgs")
        yield render_template("index2.html")

    return Response(stream_with_context(generate()))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=environ.get("PORT", 5000))


# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# from selenium.webdriver.common.by import By
# import PIL
# from PIL import Image
# from selenium.webdriver.chrome.options import Options
# from io import BytesIO
# import os
# from os import environ
# from flask import Flask,render_template,flash,request,redirect,send_file,copy_current_request_context
# import shutil
# from threading import Thread

# global text
# app = Flask(__name__)

# class Compute(Thread):
#   def __init__(self, request):
#     Thread.__init__(self)
#     self.request = request

#   def run(self):
#     global text
#     print("start")
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--no-sandbox")
#     driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
#     driver.implicitly_wait(5)
#     x = 3840
#     y = x/16*10
#     driver.set_window_size(x, y)
#     driver.delete_all_cookies()
#     url = "https://metatags.io/"
#     driver.get(url)
#     WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "/html/body/section[1]/input")))
#     time.sleep(5)
#     driver.execute_script("document.body.style.zoom = '150%'")
#     if (os.path.isdir('extractedImgs')):
#       shutil.rmtree("extractedImgs")
#     os.mkdir("extractedImgs", 0o777)
#     headlines = text.splitlines()
#     headlines = list(filter(None, headlines))
#     headlines = list(set(headlines))
#     for i, h in enumerate(headlines):
#         driver.find_element(By.XPATH, "/html/body/section[1]/input").clear()
#         driver.find_element(By.XPATH, "/html/body/section[1]/input").send_keys(h)
#         WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[@class = 'card-seo-twitter']")))
#         time.sleep(2)
#         im = driver.get_screenshot_as_png()
#         im = Image.open(BytesIO(im))
#         im1 = im.crop((x/3.71, y/2.2, x/2.105, y/1.444))
#         im1.save('extractedImgs/'+(h.split('/')[-1]).replace(".html", "")+'.png')

#     driver.quit()
#     shutil.make_archive("clipsArchive", 'zip', "extractedImgs")
#     shutil.rmtree("extractedImgs")
#     #return send_file('clipsArchive.zip', as_attachment=True, download_name='clipsArchive.zip'), render_template('index.html', message="Idle.")
#     with app.app_context(), app.test_request_context():
#       print("gg5445g")
#       def events():
#         return send_file('clipsArchive.zip', as_attachment=True, download_name='clipsArchive.zip'), render_template('index.html', message="Idle.")
#       print("4334grere")

# @app.route('/')
# def index():
#   return render_template('index.html', message="Idle.")

# @app.route('/my-link/', methods=['POST'])
# def my_link():
#   global text
#   text = request.form['text']
#   thread_a = Compute(request.__copy__())
#   thread_a.start()
#   return "Processing in background", 200

# if __name__ == '__main__':
#   app.run(debug=True, threaded=True, host='0.0.0.0', port=environ.get("PORT", 5000))
