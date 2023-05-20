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


columns = ["Наименование товара",
           "Цена розничная",
           "Минимальная партия, шт",
           "Количество в упаковке",
           "Изображение",
           "Производитель",
           "Поставщик"]

url = "https://opt.unistore.by/catalog/item_612000.html"

headers = {"Cache-Control": "no-store, no-cache, must-revalidate",
           "Content-Type": "text/html; charset=utf-8",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"}

#--------LOCATORS
min_quantity_XPATH = "//strong/span"   # Use this XPATH for searching quntity in box
price_XPATH = "//div[@class='price']"
item_description_button_XPATH = "//a[@id='ui-id-2']"
item_description_XPATH = "//td[@class='value']"
photo_item_link_XPATH = "//img[@role='presentation']"


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


with open(r"C:\Users\ART\PycharmProjects\pythonProjects2023\Work\UnistoreParser\UnistoreParser\UnistoreItems.csv", "a",
          encoding="utf-8-sig", newline="") as file:

    writer = csv.writer(file, delimiter=";")
    #writer.writerow(columns)


    browser = browser_getter(url)
    soup = soup_getter(url)

    item_name = soup.find("h1").text
    price_info = browser.find_element(By.XPATH, price_XPATH).text.split(".")
    price_container = list(filter(lambda x: x.isdigit() == True, [i.strip("рк") for i in price_info]))
    actual_price = int(price_container[0]) + int(price_container[1]) / 100
    quantity_con = browser.find_elements(By.XPATH, min_quantity_XPATH)
    filtered_quantity = [i.text.split()[-1] for i in quantity_con]
    min_quantity = filtered_quantity[0]
    quantity_in_box = filtered_quantity[1]




    try:
        browser.find_element(By.XPATH, item_description_button_XPATH).click()
        item_description = browser.find_elements(By.XPATH, item_description_XPATH)
        if item_description:
            try:
                photo_item_link = browser.find_element(By.XPATH, photo_item_link_XPATH).get_attribute("src")
                if photo_item_link:
                    if len(item_description) == 1:
                        creator = item_description[0].text
                        lst = [item_name, actual_price, min_quantity, quantity_in_box, photo_item_link, creator]
                        writer.writerow(lst)
                        browser.quit()

            except:
                photo_item_link = "-"
                if len(item_description) == 1:
                    creator = item_description[0].text
                    lst = [item_name, actual_price, min_quantity, quantity_in_box, photo_item_link, creator]
                    writer.writerow(lst)
                    browser.quit()

        else:
            try:
                photo_item_link = browser.find_element(By.XPATH, photo_item_link_XPATH).get_attribute("src")
                if photo_item_link:
                    creator = "-"
                    lst = [item_name, actual_price, min_quantity, quantity_in_box, photo_item_link, creator]
                    writer.writerow(lst)
                    browser.quit()
            except:
                creator = "-"
                photo_item_link = "-"
                lst = [item_name, actual_price, min_quantity, quantity_in_box, photo_item_link, creator]
                writer.writerow(lst)
    except Exception as e:
        print(e)









