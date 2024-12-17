from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import datetime as dt
import re
from urllib.parse import urlparse

class NewsScraper:
    def __init__(self):
        # 初始化瀏覽器
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('detach', True)
        
        # 設置其他參數
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.139 Safari/537.36'
        )

        self.driver = webdriver.Chrome(options=options)

    @staticmethod
    def extract_date(raw_text):
        """
        從文字中提取日期
        如：[PA一線 ｜2024-12-15 13:23] 提取為 2024-12-15
        """
        match = re.search(r'\d{4}-\d{2}-\d{2}', raw_text)
        return match.group(0) if match else raw_text

    @staticmethod
    def process_date(raw_date):
        """
        處理抓取到的日期文字：
        - 如果抓取到的是「多少時間前」，轉換為當天日期。
        - 如果抓取到的是完整的日期，則保持不變。
        """
        now = dt.datetime.now()
        raw_date = raw_date.lower()

        if "hours ago" in raw_date or "小時前" in raw_date:
            return now.strftime("%Y-%m-%d")
        elif "minutes ago" in raw_date or "分鐘前" in raw_date:
            return now.strftime("%Y-%m-%d")
        elif "day ago" in raw_date:
            return (now - dt.timedelta(days=1)).strftime("%Y-%m-%d")
        elif "days ago" in raw_date:
            days_ago = int(raw_date.split(" ")[0])
            return (now - dt.timedelta(days=days_ago)).strftime("%Y-%m-%d")
        else:
            # 如果都不是直接返回原值
            return raw_date

    def Followin_Flash_News(self):
        '''
        https://followin.io/zh-Hant/news
        抓取Followin的快訊資訊
        '''
        all_news = []
        driver = self.driver
        try:
            # 主頁網址
            driver.get("https://followin.io/zh-Hant/news")

            # 滑動網頁到最底
            for i in range(0, 6):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

            # 計算有幾篇新聞
            table = driver.find_element(By.CLASS_NAME, 'infinite-scroll-component')
            links = table.find_elements(By.TAG_NAME, "a")
            news_urls = [link.get_attribute('href') for link in links]

            for url in news_urls:
                driver.get(url)
                try:
                    title = driver.find_element(By.CSS_SELECTOR, 'h1.css-1rynq56').text
                except:
                    title = ''

                try:
                    date = driver.find_element(By.CLASS_NAME, 'css-1rynq56.r-1loqt21').text
                except:
                    date = ''

                try:
                    content = driver.find_element(By.ID, 'article-content').text
                except:
                    content = ''

                try:
                    tags_element = driver.find_element(By.CLASS_NAME, 'css-175oi2r.r-150rngu.r-18u37iz')
                    tags = tags_element.find_elements(By.TAG_NAME, 'a')
                    tag_texts = [tag.text for tag in tags]
                    tags_combined = ','.join(tag_texts)
                except:
                    tags_combined = ''

                # 儲存資料
                new_information = {
                    'Date': date,
                    'Title': title,
                    'Url': url,
                    'Content': content,
                    'tags_combined': tags_combined,
                    'Domain': 'Cryptocurrency'
                }
                all_news.append(new_information)

                # 返回頁面
                driver.back()

            return all_news
        
        except Exception as e:
            print(f"錯誤:{e}")

    def Followin_Breaking_News(self):
        '''
        https://followin.io/zh-Hant
        抓取Followin的熱門快訊
        '''
        all_news = []
        driver = self.driver
        try:
            # 主頁網址
            driver.get("https://followin.io/zh-Hant")

            # 點擊 "今日熱門"
            hot_list = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[1]/div[2]/main/div[4]/div[2]/div/div[1]/div/span[4]'))
            )
            hot_list.click()

            # 展開 "熱門快訊"
            Breaking_News_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[1]/div[2]/main/div[5]/div[1]/div[6]/div/div/div[2]'))
            )
            Breaking_News_container.click()

            # 抓取所有新聞連結
            outer_table = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[2]/main/div[5]/div[1]')
            links = outer_table.find_elements(By.TAG_NAME, "a")

            # 將所有新聞連結取出
            news_urls = [link.get_attribute("href") for link in links]

            for url in news_urls:
                driver.get(url)
                
                try:
                    title = driver.find_element(By.CSS_SELECTOR, 'h1.css-1rynq56').text
                except:
                    title = ''

                try:
                    date = driver.find_element(By.CLASS_NAME, 'css-1rynq56.r-1loqt21').text
                except:
                    date = ''

                try:
                    content = driver.find_element(By.ID, 'article-content').text
                except:
                    content = ''

                try:
                    tags_element = driver.find_element(By.CLASS_NAME, 'css-175oi2r.r-150rngu.r-18u37iz')
                    tags = tags_element.find_elements(By.TAG_NAME, 'a')
                    tag_texts = [tag.text for tag in tags]
                    tags_combined = ','.join(tag_texts)
                except:
                    tags_combined = ''

                # 儲存資料
                new_information = {
                    'Date': date,
                    'Title': title,
                    'Url': url,
                    'Content': content,
                    'tags_combined': tags_combined,
                    'Domain': 'Cryptocurrency'
                }
                all_news.append(new_information)

                # 返回頁面
                driver.back()
                time.sleep(1)

            return all_news
        
        except Exception as e:
            print(f"錯誤:{e}")

    def PANews_Chosen(self):
        '''
        https://www.panewslab.com/zh_hk/index.html
        抓取PANews精選
        '''
        all_news = []
        driver = self.driver
        try:
            driver.get("https://www.panewslab.com/zh_hk/index.html")
            outer_table = driver.find_element(By.CLASS_NAME, 'index-list')
            links = outer_table.find_elements(By.CSS_SELECTOR, 'a.n-title.pa-news__list-title')
            news_urls = [link.get_attribute('href') for link in links]

            for url in news_urls:
                driver.get(url)
                try:
                    title = driver.find_element(By.CLASS_NAME, 'article-title').text
                except:
                    title = ''

                try:
                    date_text = driver.find_element(By.CLASS_NAME, 'pub-time').text
                    date = self.extract_date(date_text)
                except:
                    date = ''

                try:
                    content = driver.find_element(By.ID, 'txtinfo').text
                except:
                    content = ''

                try:
                    tags_element = driver.find_element(By.CLASS_NAME, 'pa-news__list-tags')
                    tags = tags_element.find_elements(By.TAG_NAME, 'a')
                    tag_texts = [tag.text for tag in tags]
                    tags_combined = ','.join(tag_texts)
                except:
                    tags_combined = ''

                new_information = {
                    'Date': date,
                    'Title': title,
                    'Url': url,
                    'Content': content,
                    'tags_combined': tags_combined,
                    'Domain': 'Cryptocurrency'
                }
                all_news.append(new_information)
                driver.back()

            return all_news
        except Exception as e:
            print(f"錯誤:{e}")
            return all_news

    def PANews_New_Project(self):
        '''
        https://www.panewslab.com/zh_hk/index.html
        抓取PANews新項目
        '''
        all_news = []
        driver = self.driver
        try:
            driver.get("https://www.panewslab.com/zh_hk/index.html")
            button = driver.find_element(By.XPATH, '//*[@id="scroll-content"]/button[3]')
            button.click()

            outer_table = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'index-list'))
                    )
            links = WebDriverWait(outer_table, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.n-title.pa-news__list-title'))
                    )
            news_urls = [link.get_attribute('href') for link in links]

            for url in news_urls:
                driver.get(url)
                try:
                    title = driver.find_element(By.CLASS_NAME, 'article-title').text
                except:
                    title = ''

                try:
                    date_text = driver.find_element(By.CLASS_NAME, 'pub-time').text
                    date = self.extract_date(date_text)
                except:
                    date = ''

                try:
                    content = driver.find_element(By.ID, 'txtinfo').text
                except:
                    content = ''

                try:
                    tags_element = driver.find_element(By.CLASS_NAME, 'pa-news__list-tags')
                    tags = tags_element.find_elements(By.TAG_NAME, 'a')
                    tag_texts = [tag.text for tag in tags]
                    tags_combined = ','.join(tag_texts)
                except:
                    tags_combined = ''

                new_information = {
                    'Date': date,
                    'Title': title,
                    'Url': url,
                    'Content': content,
                    'tags_combined': tags_combined,
                    'Domain': 'Cryptocurrency'
                }
                all_news.append(new_information)
                driver.back()
            return all_news
        except Exception as e:
            print(f"錯誤:{e}")
            return all_news

    def PANews_DeFi(self):
        '''
        https://www.panewslab.com/zh_hk/index.html
        抓取PANews DeFi
        '''
        all_news = []
        driver = self.driver
        try:
            driver.get("https://www.panewslab.com/zh_hk/index.html")
            button = driver.find_element(By.XPATH, '//*[@id="scroll-content"]/button[4]')
            button.click()

            outer_table = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'index-list'))
                    )
            links = WebDriverWait(outer_table, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.n-title.pa-news__list-title'))
                    )
            news_urls = [link.get_attribute('href') for link in links]

            for url in news_urls:
                driver.get(url)
                try:
                    title = driver.find_element(By.CLASS_NAME, 'article-title').text
                except:
                    title = ''

                try:
                    date_text = driver.find_element(By.CLASS_NAME, 'pub-time').text
                    date = self.extract_date(date_text)
                except:
                    date = ''

                try:
                    content = driver.find_element(By.ID, 'txtinfo').text
                except:
                    content = ''

                try:
                    tags_element = driver.find_element(By.CLASS_NAME, 'pa-news__list-tags')
                    tags = tags_element.find_elements(By.TAG_NAME, 'a')
                    tag_texts = [tag.text for tag in tags]
                    tags_combined = ','.join(tag_texts)
                except:
                    tags_combined = ''

                new_information = {
                    'Date': date,
                    'Title': title,
                    'Url': url,
                    'Content': content,
                    'tags_combined': tags_combined,
                    'Domain': 'Cryptocurrency'
                }
                all_news.append(new_information)
                driver.back()
            return all_news
        except Exception as e:
            print(f"錯誤:{e}")
            return all_news

    def PANews_Regulation(self):
        '''
        https://www.panewslab.com/zh_hk/index.html
        抓取PANews 監督
        '''
        all_news = []
        driver = self.driver
        try:
            driver.get("https://www.panewslab.com/zh_hk/index.html")
            button = driver.find_element(By.XPATH, '//*[@id="scroll-content"]/button[5]')
            button.click()

            outer_table = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'index-list'))
                    )
            links = WebDriverWait(outer_table, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.n-title.pa-news__list-title'))
                    )
            news_urls = [link.get_attribute('href') for link in links]

            for url in news_urls:
                driver.get(url)
                try:
                    title = driver.find_element(By.CLASS_NAME, 'article-title').text
                except:
                    title = ''

                try:
                    date_text = driver.find_element(By.CLASS_NAME, 'pub-time').text
                    date = self.extract_date(date_text)
                except:
                    date = ''

                try:
                    content = driver.find_element(By.ID, 'txtinfo').text
                except:
                    content = ''

                try:
                    tags_element = driver.find_element(By.CLASS_NAME, 'pa-news__list-tags')
                    tags = tags_element.find_elements(By.TAG_NAME, 'a')
                    tag_texts = [tag.text for tag in tags]
                    tags_combined = ','.join(tag_texts)
                except:
                    tags_combined = ''

                new_information = {
                    'Date': date,
                    'Title': title,
                    'Url': url,
                    'Content': content,
                    'tags_combined': tags_combined,
                    'Domain': 'Cryptocurrency'
                }
                all_news.append(new_information)
                driver.back()
            return all_news
        except Exception as e:
            print(f"錯誤:{e}")
            return all_news

    def PANews_Metaverse(self):
        '''
        https://www.panewslab.com/zh_hk/index.html
        抓取PANews 元宇宙
        '''
        all_news = []
        driver = self.driver
        try:
            driver.get("https://www.panewslab.com/zh_hk/index.html")
            button = driver.find_element(By.XPATH, '//*[@id="scroll-content"]/button[6]')
            button.click()

            outer_table = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'index-list'))
                    )
            links = WebDriverWait(outer_table, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.n-title.pa-news__list-title'))
                    )
            news_urls = [link.get_attribute('href') for link in links]

            for url in news_urls:
                driver.get(url)
                try:
                    title = driver.find_element(By.CLASS_NAME, 'article-title').text
                except:
                    title = ''

                try:
                    date_text = driver.find_element(By.CLASS_NAME, 'pub-time').text
                    date = self.extract_date(date_text)
                except:
                    date = ''

                try:
                    content = driver.find_element(By.ID, 'txtinfo').text
                except:
                    content = ''

                try:
                    tags_element = driver.find_element(By.CLASS_NAME, 'pa-news__list-tags')
                    tags = tags_element.find_elements(By.TAG_NAME, 'a')
                    tag_texts = [tag.text for tag in tags]
                    tags_combined = ','.join(tag_texts)
                except:
                    tags_combined = ''

                new_information = {
                    'Date': date,
                    'Title': title,
                    'Url': url,
                    'Content': content,
                    'tags_combined': tags_combined,
                    'Domain': 'Cryptocurrency'
                }
                all_news.append(new_information)
                driver.back()
            return all_news
        except Exception as e:
            print(f"錯誤:{e}")
            return all_news

    def PANews_Financing(self):
        '''
        https://www.panewslab.com/zh_hk/index.html
        抓取PANews 融資
        '''
        all_news = []
        driver = self.driver
        try:
            driver.get("https://www.panewslab.com/zh_hk/index.html")
            button = driver.find_element(By.XPATH, '//*[@id="scroll-content"]/button[9]')
            button.click()

            outer_table = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'index-list'))
                    )
            links = WebDriverWait(outer_table, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.n-title.pa-news__list-title'))
                    )
            news_urls = [link.get_attribute('href') for link in links]

            for url in news_urls:
                driver.get(url)
                try:
                    title = driver.find_element(By.CLASS_NAME, 'article-title').text
                except:
                    title = ''

                try:
                    date_text = driver.find_element(By.CLASS_NAME, 'pub-time').text
                    date = self.extract_date(date_text)
                except:
                    date = ''

                try:
                    content = driver.find_element(By.ID, 'txtinfo').text
                except:
                    content = ''

                try:
                    tags_element = driver.find_element(By.CLASS_NAME, 'pa-news__list-tags')
                    tags = tags_element.find_elements(By.TAG_NAME, 'a')
                    tag_texts = [tag.text for tag in tags]
                    tags_combined = ','.join(tag_texts)
                except:
                    tags_combined = ''

                new_information = {
                    'Date': date,
                    'Title': title,
                    'Url': url,
                    'Content': content,
                    'tags_combined': tags_combined,
                    'Domain': 'Cryptocurrency'
                }
                all_news.append(new_information)
                driver.back()
            return all_news
        except Exception as e:
            print(f"錯誤:{e}")
            return all_news

    def PANews_Aptos(self):
        '''
        https://www.panewslab.com/zh_hk/index.html
        抓取PANews Aptos
        '''
        all_news = []
        driver = self.driver
        try:
            driver.get("https://www.panewslab.com/zh_hk/index.html")
            button = driver.find_element(By.XPATH, '//*[@id="scroll-content"]/button[10]')
            button.click()

            outer_table = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'index-list'))
                    )
            links = WebDriverWait(outer_table, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.n-title.pa-news__list-title'))
                    )
            news_urls = [link.get_attribute('href') for link in links]

            for url in news_urls:
                driver.get(url)
                try:
                    title = driver.find_element(By.CLASS_NAME, 'article-title').text
                except:
                    title = ''

                try:
                    date_text = driver.find_element(By.CLASS_NAME, 'pub-time').text
                    date = self.extract_date(date_text)
                except:
                    date = ''

                try:
                    content = driver.find_element(By.ID, 'txtinfo').text
                except:
                    content = ''

                try:
                    tags_element = driver.find_element(By.CLASS_NAME, 'pa-news__list-tags')
                    tags = tags_element.find_elements(By.TAG_NAME, 'a')
                    tag_texts = [tag.text for tag in tags]
                    tags_combined = ','.join(tag_texts)
                except:
                    tags_combined = ''

                new_information = {
                    'Date': date,
                    'Title': title,
                    'Url': url,
                    'Content': content,
                    'tags_combined': tags_combined,
                    'Domain': 'Cryptocurrency'
                }
                all_news.append(new_information)
                driver.back()
            return all_news
        except Exception as e:
            print(f"錯誤:{e}")
            return all_news

    def PANews_Web3(self):
        '''
        https://www.panewslab.com/zh_hk/index.html
        抓取PANews Web3.0
        '''
        all_news = []
        driver = self.driver
        try:
            driver.get("https://www.panewslab.com/zh_hk/index.html")
            # 向右滑動
            right_button = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div/div[1]/div[2]/div[1]/div[2]/div[2]/div/button[1]')
            right_button.click()

            button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="scroll-content"]/button[13]'))
                    )
            button.click()

            outer_table = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'index-list'))
                    )
            links = WebDriverWait(outer_table, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.n-title.pa-news__list-title'))
                    )
            news_urls = [link.get_attribute('href') for link in links]

            for url in news_urls:
                driver.get(url)
                try:
                    title = driver.find_element(By.CLASS_NAME, 'article-title').text
                except:
                    title = ''

                try:
                    date_text = driver.find_element(By.CLASS_NAME, 'pub-time').text
                    date = self.extract_date(date_text)
                except:
                    date = ''

                try:
                    content = driver.find_element(By.ID, 'txtinfo').text
                except:
                    content = ''

                try:
                    tags_element = driver.find_element(By.CLASS_NAME, 'pa-news__list-tags')
                    tags = tags_element.find_elements(By.TAG_NAME, 'a')
                    tag_texts = [tag.text for tag in tags]
                    tags_combined = ','.join(tag_texts)
                except:
                    tags_combined = ''

                new_information = {
                    'Date': date,
                    'Title': title,
                    'Url': url,
                    'Content': content,
                    'tags_combined': tags_combined,
                    'Domain': 'Cryptocurrency'
                }
                all_news.append(new_information)
                driver.back()
            return all_news
        except Exception as e:
            print(f"錯誤:{e}")
            return all_news

    def PANews_airdrop(self):
        '''
        https://www.panewslab.com/zh_hk/index.html
        抓取PANews airdrop
        '''
        all_news = []
        driver = self.driver
        try:
            driver.get("https://www.panewslab.com/zh_hk/index.html")
            right_button = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div/div[1]/div[2]/div[1]/div[2]/div[2]/div/button[1]')
            right_button.click()

            button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="scroll-content"]/button[14]'))
                    )
            button.click()

            outer_table = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'index-list'))
                    )
            links = WebDriverWait(outer_table, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.n-title.pa-news__list-title'))
                    )
            news_urls = [link.get_attribute('href') for link in links]

            for url in news_urls:
                driver.get(url)
                try:
                    title = driver.find_element(By.CLASS_NAME, 'article-title').text
                except:
                    title = ''

                try:
                    date_text = driver.find_element(By.CLASS_NAME, 'pub-time').text
                    date = self.extract_date(date_text)
                except:
                    date = ''

                try:
                    content = driver.find_element(By.ID, 'txtinfo').text
                except:
                    content = ''

                try:
                    tags_element = driver.find_element(By.CLASS_NAME, 'pa-news__list-tags')
                    tags = tags_element.find_elements(By.TAG_NAME, 'a')
                    tag_texts = [tag.text for tag in tags]
                    tags_combined = ','.join(tag_texts)
                except:
                    tags_combined = ''

                new_information = {
                    'Date': date,
                    'Title': title,
                    'Url': url,
                    'Content': content,
                    'tags_combined': tags_combined,
                    'Domain': 'Cryptocurrency'
                }
                all_news.append(new_information)
                driver.back()
            return all_news
        except Exception as e:
            print(f"錯誤:{e}")
            return all_news

    def PANews_Layer2(self):
        '''
        https://www.panewslab.com/zh_hk/index.html
        抓取PANews Layer2
        '''
        all_news = []
        driver = self.driver
        try:
            driver.get("https://www.panewslab.com/zh_hk/index.html")
            right_button = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div/div[1]/div[2]/div[1]/div[2]/div[2]/div/button[1]')
            right_button.click()

            button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="scroll-content"]/button[16]'))
                    )
            button.click()

            outer_table = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'index-list'))
                    )
            links = WebDriverWait(outer_table, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.n-title.pa-news__list-title'))
                    )
            news_urls = [link.get_attribute('href') for link in links]

            for url in news_urls:
                driver.get(url)
                try:
                    title = driver.find_element(By.CLASS_NAME, 'article-title').text
                except:
                    title = ''

                try:
                    date_text = driver.find_element(By.CLASS_NAME, 'pub-time').text
                    date = self.extract_date(date_text)
                except:
                    date = ''

                try:
                    content = driver.find_element(By.ID, 'txtinfo').text
                except:
                    content = ''

                try:
                    tags_element = driver.find_element(By.CLASS_NAME, 'pa-news__list-tags')
                    tags = tags_element.find_elements(By.TAG_NAME, 'a')
                    tag_texts = [tag.text for tag in tags]
                    tags_combined = ','.join(tag_texts)
                except:
                    tags_combined = ''

                new_information = {
                    'Date': date,
                    'Title': title,
                    'Url': url,
                    'Content': content,
                    'tags_combined': tags_combined,
                    'Domain': 'Cryptocurrency'
                }
                all_news.append(new_information)
                driver.back()
            return all_news
        except Exception as e:
            print(f"錯誤:{e}")
            return all_news

    def PANews_NFT(self):
        '''
        https://www.panewslab.com/zh_hk/index.html
        抓取PANews NFT
        '''
        all_news = []
        driver = self.driver
        try:
            driver.get("https://www.panewslab.com/zh_hk/index.html")
            right_button = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div/div[1]/div[2]/div[1]/div[2]/div[2]/div/button[1]')
            right_button.click()

            button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="scroll-content"]/button[17]'))
                    )
            button.click()

            outer_table = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'index-list'))
                    )
            links = WebDriverWait(outer_table, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.n-title.pa-news__list-title'))
                    )
            news_urls = [link.get_attribute('href') for link in links]

            for url in news_urls:
                driver.get(url)
                try:
                    title = driver.find_element(By.CLASS_NAME, 'article-title').text
                except:
                    title = ''

                try:
                    date_text = driver.find_element(By.CLASS_NAME, 'pub-time').text
                    date = self.extract_date(date_text)
                except:
                    date = ''

                try:
                    content = driver.find_element(By.ID, 'txtinfo').text
                except:
                    content = ''

                try:
                    tags_element = driver.find_element(By.CLASS_NAME, 'pa-news__list-tags')
                    tags = tags_element.find_elements(By.TAG_NAME, 'a')
                    tag_texts = [tag.text for tag in tags]
                    tags_combined = ','.join(tag_texts)
                except:
                    tags_combined = ''

                new_information = {
                    'Date': date,
                    'Title': title,
                    'Url': url,
                    'Content': content,
                    'tags_combined': tags_combined,
                    'Domain': 'Cryptocurrency'
                }
                all_news.append(new_information)
                driver.back()
            return all_news
        except Exception as e:
            print(f"錯誤:{e}")
            return all_news

    def PANews_Chain_Games(self):
        '''
        https://www.panewslab.com/zh_hk/index.html
        抓取PANews 鏈遊
        '''
        all_news = []
        driver = self.driver
        try:
            driver.get("https://www.panewslab.com/zh_hk/index.html")
            right_button = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div/div[1]/div[2]/div[1]/div[2]/div[2]/div/button[1]')
            right_button.click()

            button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="scroll-content"]/button[18]'))
                    )
            button.click()

            outer_table = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'index-list'))
                    )
            links = WebDriverWait(outer_table, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.n-title.pa-news__list-title'))
                    )
            news_urls = [link.get_attribute('href') for link in links]

            for url in news_urls:
                driver.get(url)
                try:
                    title = driver.find_element(By.CLASS_NAME, 'article-title').text
                except:
                    title = ''

                try:
                    date_text = driver.find_element(By.CLASS_NAME, 'pub-time').text
                    date = self.extract_date(date_text)
                except:
                    date = ''

                try:
                    content = driver.find_element(By.ID, 'txtinfo').text
                except:
                    content = ''

                try:
                    tags_element = driver.find_element(By.CLASS_NAME, 'pa-news__list-tags')
                    tags = tags_element.find_elements(By.TAG_NAME, 'a')
                    tag_texts = [tag.text for tag in tags]
                    tags_combined = ','.join(tag_texts)
                except:
                    tags_combined = ''

                new_information = {
                    'Date': date,
                    'Title': title,
                    'Url': url,
                    'Content': content,
                    'tags_combined': tags_combined,
                    'Domain': 'Cryptocurrency'
                }
                all_news.append(new_information)
                driver.back()
            return all_news
        except Exception as e:
            print(f"錯誤:{e}")
            return all_news

    def Coingecko_Flash_News(self):
        '''
        https://www.coingecko.com/zh-tw/news
        抓取Coingecko 新聞
        '''
        all_news = []
        driver = self.driver
        try:
            driver.get("https://www.coingecko.com/zh-tw/news")
            links = driver.find_elements(By.CSS_SELECTOR, 'a[rel="nofollow noopener"]')
            news_url = [link.get_attribute('href') for link in links if not link.get_attribute('href') == 'https://cryptopanic.com/']
            
            for url in news_url:
                driver.get(url)
                domain = urlparse(url).netloc

                if domain == 'www.blocktempo.com' or domain == 'blockcast.it':
                    # 這兩個站點的結構似乎一致
                    try:
                        title = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[5]/div[1]/div[1]/div/div/div/div[2]/div[1]/div/div[2]/h1'))
                        ).text
                    except:
                        title = ""

                    try:
                        date_text = driver.find_element(By.XPATH, '/html/body/div[2]/div[5]/div[1]/div[1]/div/div/div/div[2]/div[1]/div/div[2]/div/div/div[1]/div[2]/a').text
                        date = self.extract_date(date_text)
                    except:
                        date = ''
                    
                    try:
                        content = driver.find_element(By.XPATH, '/html/body/div[2]/div[5]/div[1]/div[1]/div/div/div/div[2]/div[1]/div/div[6]/div[2]').text
                    except:
                        content = ''

                    try:
                        tags_element = driver.find_element(By.CLASS_NAME, 'jeg_post_tags')
                        tags = tags_element.find_elements(By.TAG_NAME, 'a')
                        tag_texts = [tag.text for tag in tags]
                        tags_combined = ','.join(tag_texts)
                    except:
                        tags_combined = ''

                elif domain == 'abmedia.io':
                    try:
                        title = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'title'))
                        ).text
                    except:
                        title = ""

                    try:
                        date_raw = driver.find_element(By.CLASS_NAME, 'post-date').text
                        date = self.process_date(date_raw)
                    except:
                        date = ''
                    
                    try:
                        content = driver.find_element(By.CLASS_NAME, 'desc').text
                    except:
                        content = ''

                    try:
                        tags_element = driver.find_element(By.CLASS_NAME, 'cat')
                        tags = tags_element.find_elements(By.TAG_NAME, 'a')
                        tag_texts = [tag.text for tag in tags]
                        tags_combined = ','.join(tag_texts)
                    except:
                        tags_combined = ''
                else:
                    # 若有額外站點可再補充
                    title = ''
                    date = ''
                    content = ''
                    tags_combined = ''

                new_information = {
                    'Date': date,
                    'Title': title,
                    'Url': url,
                    'Content': content,
                    'tags_combined': tags_combined,
                    'Domain': 'Cryptocurrency'
                }
                if title != '':
                    all_news.append(new_information)
                driver.back()

            return all_news
        except Exception as e:
            print(f"錯誤:{e}")
            return all_news

    def CoinTelegraph_News(self):
        '''
        https://cointelegraph.com/
        抓取CoinTelegraph 新聞
        '''
        all_news = []
        driver = self.driver
        try:
            driver.get("https://cointelegraph.com/")
            outer_table = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'group.main'))
            )
            links = outer_table.find_elements(By.CSS_SELECTOR, 'a.post-card__figure-link')
            news_url = [link.get_attribute('href') for link in links]

            for url in news_url:
                driver.get(url)
                try:
                    title = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'post__title'))
                    ).text
                except:
                    title = ""

                try:
                    date_raw = driver.find_element(By.CLASS_NAME, 'post-meta__publish-date').text
                    date = self.process_date(date_raw)
                except:
                    date = ''
                
                try:
                    content = driver.find_element(By.CLASS_NAME, 'post-content.relative').text
                except:
                    content = ''

                try:
                    tags_element = driver.find_element(By.CLASS_NAME, 'tags-list__list')
                    tags = tags_element.find_elements(By.TAG_NAME, 'a')
                    tag_texts = [tag.text.lstrip('#') for tag in tags]
                    tags_combined = ','.join(tag_texts)
                except:
                    tags_combined = ''

                if title != '':
                    new_information = {
                        'Date': date,
                        'Title': title,
                        'Url': url,
                        'Content': content,
                        'tags_combined': tags_combined,
                        'Domain': 'Cryptocurrency'
                    }
                    all_news.append(new_information)
                driver.back()

            return all_news
        except Exception as e:
            print(f"錯誤:{e}")
            return all_news
        
    def close_driver(self):
        '''
        關閉瀏覽器
        '''
        if self.driver:
            self.driver.quit()


if __name__ == "__main__":
    scraper = NewsScraper()

    try:
        # 抓取Followin 快訊
        # news_data = scraper.Followin_Flash_News()
        news_data = scraper.Followin_Breaking_News()
        # news_data = scraper.PANews_Chosen()
        # news_data = scraper.PANews_New_Project()
        # news_data = scraper.PANews_DeFi()
        # news_data = scraper.PANews_Regulation()
        # news_data = scraper.PANews_Metaverse()
        # news_data = scraper.PANews_Financing()
        # news_data = scraper.PANews_Aptos()
        # news_data = scraper.PANews_Web3()
        # news_data = scraper.PANews_airdrop()
        # news_data = scraper.PANews_Layer2()
        # news_data = scraper.PANews_NFT()
        # news_data = scraper.PANews_Chain_Games()
        # news_data = scraper.Coingecko_Flash_News()
        # news_data = scraper.CoinTelegraph_News()
        for news_item in news_data:
            print("-" * 50)
            print(f"Date: {news_item['Date']}\n"
                  f"Title: {news_item['Title']}\n"
                  f"URL: {news_item['Url']}\n"
                  f"Content: {news_item['Content']}\n"
                  f"tags: {news_item['tags_combined']}\n"
                  f"Domain: {news_item['Domain']}")

    finally:
        scraper.close_driver()