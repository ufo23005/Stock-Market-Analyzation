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

class YahooNewsScraper:
    def __init__(self):
        # 初始化瀏覽器
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('detach', True)
        
        # # 設置其他參數
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

    def Scrape_News(self):
        """
        https://tw.stock.yahoo.com/reporter/
        抓取 Yahoo 新聞頁面上的標題和內容
        """
        all_news = []
        driver = self.driver
        try:
            self.driver.get("https://tw.stock.yahoo.com/reporter/")  # 開啟 Yahoo 新聞頁面
            # WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.ID, 'caas-lead-header-undefined'))
            #     )
            # 滑動網頁到最底
            for i in range(0, 6):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

            # 計算有幾篇新聞
            Outer_table = driver.find_element(By.ID, 'YDC-Stream')
            
            links = Outer_table.find_elements(By.CSS_SELECTOR, "a.Fw\\(b\\)")
            
            news_urls = [link.get_attribute('href') for link in links]
            
            print(len(news_urls))
            
            # if news_urls:
            #     url=news_urls[0]
            for url in news_urls:
                driver.get(url)
                try:
                    title = driver.find_element(By.ID, 'caas-lead-header-undefined').text
                except:
                    title = ''

                try:
                    date = self.extract_date(driver.find_element(By.CLASS_NAME, 'caas-attr-time-style').text)
                except:
                    date = ''

                try:
                    # 抓取包含內容的主容器
                    main_container = self.driver.find_element(By.CLASS_NAME, "caas-body")
                    
                    # 從主容器中抓取所有 <p> 標籤
                    paragraphs = main_container.find_elements(By.TAG_NAME, "p")
                    
                    # 提取文字內容
                    content = [p.text.strip() for p in paragraphs if p.text.strip()]
                    #content = driver.find_element(By.CLASS_NAME, 'caas-body').text
                except:
                    content = ''

                
                if title:
                    # 儲存資料
                    new_information = {
                        'Date': date,
                        'Title': title,
                        'Url': url,
                        'Content': content,
                        'tags_combined': '',
                        'Domain': 'StockNewsdata'
                    }
                    all_news.append(new_information)

            #     # 返回頁面 爬yahoo股市不需要
            #     #driver.back()

            return all_news
        except Exception as e:
            print(f"錯誤:{e}")
    def close_driver(self):
        '''
        關閉瀏覽器
        '''
        if self.driver:
            self.driver.quit()


# 測試 YahooNewsScraper 類別
if __name__ == "__main__":
    yahoo_scraper = YahooNewsScraper()
    try:
        news_data = yahoo_scraper.Scrape_News()
        if not news_data:  # 檢查是否抓到資料
            print("沒有抓取到任何新聞資料！")
        for news_item in news_data:
            print("-" * 50)
            print(f"Date: {news_item['Date']}\n"
                  f"Title: {news_item['Title']}\n"
                  f"URL: {news_item['Url']}\n"
                  f"Content: {news_item['Content']}\n"
                  f"tags: {news_item['tags_combined']}\n"
                  f"Domain: {news_item['Domain']}")
    except Exception as e:
        print(f"程式執行時發生錯誤: {e}")
    finally:
        yahoo_scraper.close_driver()
