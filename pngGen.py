import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install("webdriver_manager")
install("selenium")
install("seleniumbase")

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
from PIL import Image
from selenium.webdriver.chrome.options import Options
from io import BytesIO
import os
from seleniumbase import BaseCase

class ComponentsTest(BaseCase):
    def test_basic(self):

        # open the app and take a screenshot
        self.open("https://google.com")


chrome_options = Options()
chrome_options.add_argument("--headless")

chrome_path = "./chromedriverLINUX"
os.chmod(chrome_path, 0o755)
#os.system('apt-get install -y libglib2.0-0=2.50.3-2 \
#    libnss3=2:3.26.2-1.1+deb9u1 \
#    libgconf-2-4=3.2.6-4+b1 \
#    libfontconfig1=2.11.0-6.7+b1 \
#    libgtk2.0-0:i386 \
#    libsm6:i386')
os.system('apt-get update')
os.system('apt-get install wget')
os.system('apt-get install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils default-jdk')
os.system('wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb')
os.system('dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install')
#subprocess.Popen([r"./chromedriverLINUX"])
#executable_path=chrome_path, 
driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)
x = 5120
y = x/16*10
driver.set_window_size(x, y)
driver.delete_all_cookies()
url = "https://metatags.io/"
driver.get(url)
driver.execute_script("document.body.style.zoom = '200%'")
time.sleep(5)

headlines = [
    "https://www.nytimes.com/2021/11/06/opinion/biden-infrastructure-deal.html",
    "https://www.nytimes.com/2021/11/06/us/politics/infrastructure-black-caucus-vote.html",

"https://www.nytimes.com/2021/11/06/us/dark-sky-parks-us.html"
]

for i, h in enumerate(headlines):
    driver.find_element(By.XPATH, "/html/body/section[1]/input").clear()
    driver.find_element(By.XPATH, "/html/body/section[1]/input").send_keys(h)

    time.sleep(2)

    im = driver.get_screenshot_as_png()
    im = Image.open(BytesIO(im))
    im1 = im.crop((x/3.71, y/2.2, x/2.105, y/1.444))
    im1.save('extractedImgs/'+h.split('/')[-1]+'.png')

driver.quit()
