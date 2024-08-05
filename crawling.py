from selenium import webdriver
from selenium.webdriver import Keys, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from datetime import datetime
from util import parse_date, parse_time_for_korea
import time
import traceback


class WebCrawler:
    def __init__(self, eml: str, id: str, password: str, url: str, base_date: str | datetime = datetime.today()):
        options = ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        self.__session = None
        self.__response = None
        self.__cookies = []

        self.__login_url = "https://x.com/i/flow/login"
        self.__url = url
        self.__driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.__year, self.__month = tuple(map(int, base_date.split("-")))
        # 날짜
        # 내용
        # 하트
        # 리포스트
        # 조회수
        self.__data = {}

        self.login(eml, id, password)

    def login(self, eml, id, password):
        self.__driver.get(self.__login_url)
        self.__driver.implicitly_wait(10)
        first = self.__driver.session_id

        id_input = WebDriverWait(self.__driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]')))
        id_input.send_keys(id)
        id_input.send_keys(Keys.ENTER)

        try:
            check_input = WebDriverWait(self.__driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="on"]')))
            check_input.send_keys(eml)
            check_input.send_keys(Keys.ENTER)
        except:
            pass

        pw_input = WebDriverWait(self.__driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="current-password"]')))
        pw_input.send_keys(password)
        pw_input.send_keys(Keys.ENTER)

        time.sleep(3)
        self.__driver.execute_script('window.open("' + self.__url + '");')
        self.__driver.implicitly_wait(10)
        self.__driver.close()
        self.__driver.switch_to.window(self.__driver.window_handles[0])

        self.page_crawl()

    def page_crawl(self):
        action = ActionChains(self.__driver)

        while True:
            try:
                articles = self.__driver.find_elements(By.CSS_SELECTOR, "article[data-testid=tweet]")

                for article in articles:
                    key, date, content, heart, repost, view = None, None, None, None, None, None

                    key = article.find_element(By.XPATH,
                                               './/div/div/div[2]/div[2]/div[1]/div/div[1]/div/div/div[2]/div/div[3]/a').get_attribute(
                        "href")
                    if key in self.__data.keys():
                        continue

                    date = parse_time_for_korea(article.find_element(By.XPATH,
                                                                     './/div/div/div[2]/div[2]/div[1]/div/div[1]/div/div/div[2]/div/div[3]/a/time').get_attribute(
                        "datetime"))
                    if date.year == self.__year:
                        if date.month == self.__month:
                            pass
                        elif date.month > self.__month:
                            continue
                        else:
                            return
                    elif date.year > self.__year:
                        continue
                    else:
                        return

                    if len(article.find_elements(By.XPATH, './/div/div/div[2]/div[2]/div[2]/div/*')) == 0:
                        content = ""
                    else:
                        content = ""
                        contents = article.find_elements(By.XPATH, './/div/div/div[2]/div[2]/div[2]/div/*')

                        for c in contents:
                            if c.tag_name == "span":
                                content += c.text
                            elif c.tag_name == "img":
                                content += c.get_attribute("alt")
                            elif c.tag_name == "a":
                                content += c.get_attribute("href")

                    if len(article.find_elements(By.XPATH,
                                                 './/div/div/div[2]/div[2]/div[4]/div/div/div[3]/button/div/div[2]/span/span/span')) == 0:
                        heart = ""
                    else:
                        heart = article.find_element(By.XPATH,
                                                     './/div/div/div[2]/div[2]/div[4]/div/div/div[3]/button/div/div[2]/span/span/span').text

                    if len(article.find_elements(By.XPATH,
                                                 './/div/div/div[2]/div[2]/div[4]/div/div/div[2]/button/div/div[2]/span/span/span')) == 0:
                        repost = ""
                    else:
                        repost = article.find_element(By.XPATH,
                                                      './/div/div/div[2]/div[2]/div[4]/div/div/div[2]/button/div/div[2]/span/span/span').text

                    if len(article.find_elements(By.XPATH,
                                                 './/div/div/div[2]/div[2]/div[4]/div/div/div[4]/a/div/div[2]/span/span/span')) == 0:
                        view = ""
                    else:
                        view = article.find_element(By.XPATH,
                                                    './/div/div/div[2]/div[2]/div[4]/div/div/div[4]/a/div/div[2]/span/span/span').text

                    print(key, date, content, heart, repost, view)

                    self.__data[key] = {"날짜": date.strftime("%Y.%m.%d"), "내용": content, "리포스트": repost, "좋아요": heart,
                                        "조회수": view}

                action.move_to_element(articles[-1]).perform()
                self.__driver.implicitly_wait(3)
            except Exception as e:
                print("오류 발생 : " + traceback.format_exc())
                return

    def get_data(self):
        print(self.__data)
        return self.__data

    def close_crawling(self):
        self.__driver.close()
