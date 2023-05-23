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
import datetime

# -----Locators--------#
every_item_XPATH = "//div[@class='img']//a[@class='fancy_ajax']"
esc_button_XPATH = "//button[@class='mfp-close']"
scroll_container_XPATH = "//div[@class ='products_block__wrapper products_4_columns vertical']"
footer_title_XPATH = "//div[@class='footer__title']"
items_quantity_XPATH = "//button[@id='filter_submit']"
next_page_link_XPATH = "//a[@class='next_page_link']"
min_quantity_XPATH = "//strong/span"  # Use this XPATH for searching quntity in box
price_XPATH = "//div[@class='price']"
item_description_button_XPATH = "//a[@id='ui-id-2']"
item_description_XPATH = "//td[@class='value']"
photo_item_link_XPATH = "//img[@role='presentation']"

columns = ["Наименование товара",
           "Цена розничная",
           "Минимальная партия, шт",
           "Количество в упаковке",
           "Изображение",
           "Производитель"
           ]

url = "https://opt.unistore.by/"
headers = {"Cache-Control": "no-store, no-cache, must-revalidate",
           "Content-Type": "text/html; charset=utf-8",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"}


def browser_getter(url):
    browser = webdriver.Chrome()
    browser.maximize_window()
    browser.get(url)
    browser.implicitly_wait(8)
    return browser


def soup_getter(url):
    res = requests.get(url=url, headers=headers)
    res.encoding = 'utf-8'
    return BeautifulSoup(res.text, "lxml")

start = time.time()
data = datetime.date.today()
with open(rf"C:\Users\ART\PycharmProjects\pythonProjects2023\Work\UnistoreParser\UnistoreParser\CSV_Files\UnistoreItemParser{data}.csv",
          "a",
          encoding="utf-8-sig", newline="") as file, open(rf"C:\Users\ART\PycharmProjects\pythonProjects2023\Work\UnistoreParser\UnistoreParser\CSV_Files\UnistoreBugLinks{data}.csv",
                                                          "a",
                                                          encoding="utf-8-sig", newline="") as bug_link_file:

    writer = csv.writer(file, delimiter=";")
    bug_writer = csv.writer(bug_link_file, delimiter=";")
    writer.writerow(columns)

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

            if item_count <= 144:  # 144 max items on full load page
                while True:
                    try:
                        container = browser.find_elements(By.XPATH, every_item_XPATH)

                        if len(container) == item_count:  # -1 cause there is one odd element in top bar of the site
                            for li in container:
                                link = li.get_attribute("href")
                                data_container.append(link)
                            browser.quit()
                            break
                        else:
                            raise Exception
                    except:
                        action = ActionChains(browser)
                        action.scroll_by_amount(0, 3000)
                        action.scroll_by_amount(0, 500)
                        action.perform()
            # ---------------------------------------------------------------------------------IMPROVE THIS SHIT!!!!
            elif item_count > 144:
                item_summator = []
                container_count = 0

                # Work with it if page pagen exists
                while True:
                    try:
                        container = browser.find_elements(By.XPATH, every_item_XPATH)
                        container_count += len(container)
                        if len(container) == 144:
                            item_summator.append(container_count)
                            for li in container:
                                link = li.get_attribute("href")
                                data_container.append(link)
                            next_page = browser.find_element(By.XPATH, next_page_link_XPATH)
                            next_page.click()
                            raise Exception

                        elif sum(item_summator) + container_count == item_count:
                            # sub_container unpacking
                            for li in container:
                                link = li.get_attribute("href")
                                data_container.append(link)
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

    # -----------------------------------------------------------------------------------------------------

    for i in data_container:
        browser = browser_getter(i)
        soup = soup_getter(i)

        try:
            item_name = soup.find("h1").text
            price_info = browser.find_element(By.XPATH, price_XPATH).text.split(".")
            price_container = list(filter(lambda x: x.isdigit() == True, [i.strip("рк") for i in price_info]))
            actual_price = int(price_container[0]) + int(price_container[1]) / 100
            quantity_con = browser.find_elements(By.XPATH, min_quantity_XPATH)
            filtered_quantity = [i.text.split()[-1] for i in quantity_con]
            min_quantity = filtered_quantity[0]
            quantity_in_box = filtered_quantity[1]
            browser.find_element(By.XPATH, item_description_button_XPATH).click()
            item_description = browser.find_elements(By.XPATH, item_description_XPATH)

            if item_description:
                creator = item_description[0].text
                try:
                    photo_item_link = browser.find_element(By.XPATH, photo_item_link_XPATH).get_attribute("src")
                    if photo_item_link:
                        lst = [item_name, actual_price, min_quantity, quantity_in_box, photo_item_link, creator]
                        writer.writerow(lst)
                        browser.quit()
                except:
                    photo_item_link = "-"
                    lst = [item_name, actual_price, min_quantity, quantity_in_box, photo_item_link, creator]
                    writer.writerow(lst)
                    browser.quit()
        except:
            try:
                creator = "-"
                photo_item_link = "-"
                lst = [item_name, actual_price, min_quantity, quantity_in_box, photo_item_link, creator]
                writer.writerow(lst)
                browser.quit()
            except:
                bug_writer.writerow(i)
                continue


end = time.time()
print(end - start)
