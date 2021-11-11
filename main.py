from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
import PIL
from PIL import Image
from selenium.webdriver.chrome.options import Options
from io import BytesIO
import os
from os import environ
from flask import Flask,render_template,flash,request,redirect,send_file
import shutil

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/my-link/', methods=['POST'])
def my_link():
  text = request.form['text']

  chrome_options = webdriver.ChromeOptions()
  chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
  chrome_options.add_argument("--headless")
  chrome_options.add_argument("--disable-dev-shm-usage")
  chrome_options.add_argument("--no-sandbox")
  driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)

  x = 3840
  y = x/16*10
  driver.set_window_size(x, y)
  driver.delete_all_cookies()
  url = "https://metatags.io/"
  driver.get(url)
  driver.execute_script("document.body.style.zoom = '150%'")
  time.sleep(5)
  if (os.path.isdir('extractedImgs')):
    shutil.rmtree("extractedImgs")
  headlines = text.split('\n')

  for i, h in enumerate(headlines):
      driver.find_element(By.XPATH, "/html/body/section[1]/input").clear()
      driver.find_element(By.XPATH, "/html/body/section[1]/input").send_keys(h)

      time.sleep(2)

      im = driver.get_screenshot_as_png()
      im = Image.open(BytesIO(im))
      im1 = im.crop((x/3.71, y/2.2, x/2.105, y/1.444))
      os.mkdir("extractedImgs", 0o777)
      im1.save('extractedImgs/'+(h.split('/')[-1]).replace(".html", "")+'.png')

  driver.quit()
  shutil.make_archive("clipsArchive", 'zip', "extractedImgs")
  shutil.rmtree("extractedImgs")
  return send_file('clipsArchive.zip', as_attachment=True, download_name='clipsArchive.zip')

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=environ.get("PORT", 5000))
