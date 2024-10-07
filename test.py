import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageFilter
import time

# Setup the Chrome driver
driver = webdriver.Chrome()

# Navigate to the Goodreads page
driver.get("https://www.goodreads.com/book/popular_by_date/2024/4")
driver.implicitly_wait(5)

button = driver.find_element(By.XPATH, "//*[@id='__next']/div[2]/main/div[2]/div[1]/div[3]/div/div/button")

button.click()
time.sleep(10000)
