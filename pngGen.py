import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install("selenium")

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
from PIL import Image
from selenium.webdriver.chrome.options import Options
from io import BytesIO

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)
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
