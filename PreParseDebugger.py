import csv
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import lxml
import requests
import html
import time


#------LOCATORS-------
every_item_XPATH = "//div[@class='img']//a[@class='fancy_ajax']"
items_quantity_XPATH = "//button[@id='filter_submit']"
scroll_container_XPATH = "//div[@class ='products_block__wrapper products_4_columns vertical']"
next_page_link_XPATH = "//a[@class='next_page_link']"

url = "https://opt.unistore.by/catalog/400000143.html"
headers = {"Cache-Control": "no-store, no-cache, must-revalidate",
           "Content-Type": "text/html; charset=utf-8",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"}


def browser_getter(url):
    browser = webdriver.Chrome()
    browser.maximize_window()
    browser.get(url)
    browser.implicitly_wait(10)
    return browser

def soup_getter(url):
    res = requests.get(url=url, headers=headers)
    res.encoding = 'utf-8'
    return BeautifulSoup(res.text, "lxml")


soup = soup_getter(url)

browser = browser_getter(url)
container = browser.find_element(By.XPATH, scroll_container_XPATH)
items_quantity = browser.find_element(By.XPATH, items_quantity_XPATH).text
items_page_count = int(items_quantity.split()[1])

sub_container = []
summator = []
counter = 0
while True:
    try:
        items_container = browser.find_elements(By.XPATH, every_item_XPATH)
        counter += len(items_container)

        if counter == 144:
            summator.append(counter)
            for i in items_container:
                link = i.get_attribute("href")
                sub_container.append(link)
            next_page = browser.find_element(By.XPATH, next_page_link_XPATH).click()
            raise Exception

        elif sum(summator) + counter == items_page_count:
            for i in items_container:
                link = i.get_attribute("href")
                sub_container.append(link)
            break
        else:
            raise Exception
    except:
        counter = 0
        action = ActionChains(browser)
        action.scroll_by_amount(0, 3000)
        action.scroll_by_amount(0, 500)
        action.perform()


#sub_container = [i for j in sub_container for i in j]

print(sub_container)
print(len(sub_container))


