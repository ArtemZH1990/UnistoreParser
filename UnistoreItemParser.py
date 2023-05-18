import csv
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

# -----Locators--------#
every_item_XPATH = "//div[@class='title']//a[@class='fancy_ajax']"
esc_button_XPATH = "//button[@class='mfp-close']"
scroll_container_XPATH = "//div[@class ='products_block__wrapper products_4_columns vertical']"
footer_title_XPATH = "//div[@class='footer__title']"
items_quantity_XPATH = "//button[@id='filter_submit']"
next_page_link_XPATH = "//a[@class='next_page_link']"

columns = ["Наименование товара",
           "Цена розничная",
           "Минимальная партия, шт",
           "Количество в упаковке",
           "Фото товара",
           "Производитель"]

url = "https://opt.unistore.by/"
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


with open(r"/Work/UnistoreParser/UnistoreItems.csv", "a",
          encoding="utf-8-sig", newline="") as file:
    # writer = csv.writer(file, delimiter=";")
    # writer.writerow(columns)

    # Needed header in request
    soup = soup_getter(url)

    catalog_items_menu = soup.find("ul", class_="catalog_menu catalog_menu_visible")
    items_links_container = [i["href"] for i in catalog_items_menu.find_all("a")]

    # First cicle. We need to check every link, cause some pages is empty, without any product.
    # If you can't find someone, just skip it. Price is point!!
    data_container = []
    link_data_container = []
    for i in items_links_container:
        soup_i = soup_getter(i)
        products_block = soup_i.find("div", class_="products_block__wrapper products_4_columns vertical")

        if products_block:
            # I don't find the better way, than use Selenium this moment
            browser = browser_getter(i)
            items_quantity = browser.find_element(By.XPATH, items_quantity_XPATH).text
            item_count = int(items_quantity.split()[1])

            if item_count < 144:  # 144 max items on full load page
                while True:
                    try:
                        container = browser.find_elements(By.XPATH, every_item_XPATH)

                        if len(container) - 1 == item_count:  # -1 cause there is one odd element in top bar of the site
                            data_container.append(container[1:])
                            browser.quit()
                            break
                        else:
                            raise Exception
                    except:
                        action = ActionChains(browser)
                        action.scroll_by_amount(0, 3000)
                        action.scroll_by_amount(0, 500)
                        action.perform()

            elif item_count > 144:
                sub_container = []
                item_summator = []
                container_count = 0

                # Work with it if page pagen exists
                while True:
                    try:
                        container = browser.find_elements(By.XPATH, every_item_XPATH)
                        container_count += len(container) - 1
                        if len(container) - 1 == 144:
                            item_summator.append(container_count)
                            sub_container.append(container)
                            container_count = 0
                            next_page = browser.find_element(By.XPATH, next_page_link_XPATH)
                            next_page.click()
                            raise Exception

                        elif sum(item_summator) + container_count == item_count:
                            # sub_container unpacking
                            sub_container = [i for j in sub_container for i in j]
                            data_container.append(sub_container)
                            browser.quit()
                            break
                        else:
                            raise Exception
                    except:
                        container_count = 0
                        action = ActionChains(browser)
                        action.scroll_by_amount(0, 3000)
                        action.scroll_by_amount(0, 500)
                        action.perform()




    data_container = [i for j in data_container for i in j]   #All products here!!!

    print(data_container)





