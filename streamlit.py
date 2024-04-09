import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

class WebScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("Web Scraper")

        self.keyword_input = st.sidebar.text_input("Enter the keyword:")
        self.search_button = st.sidebar.button("Search")
        self.exit_button = st.sidebar.button("Exit")

        # 検索結果を表示するテキストウィンドウ
        self.result_text = st.empty()

    def search_on_website(self):
        keyword = self.keyword_input
        self.result_text.text("")  # 検索前にテキストをクリア
        self.scrape_website(keyword)

    def scrape_website(self, keyword):
        coindesk_url = "https://www.coindeskjapan.com"
        chromedriver_path = "C:/Users/otatu/OneDrive/chrome-win32/chromedriver-win32/chromedriver.exe"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")  # ウィンドウを最大化
        chrome_options.add_argument("--headless")  # ブラウザを非表示にする
        driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
        driver.get(coindesk_url)

        # 検索ボックスが見つかるまで待機
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "s"))
        )

        # サイト内検索ボックスにキーワードを自動入力
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)

        self.scrape_search_results(driver, keyword)

    def scrape_search_results(self, driver, keyword):
        try:
            while True:
                response = requests.get(driver.current_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # 記事のタイトルとリンクを取得して表示
                article_links = [(a.text.strip(), urljoin(driver.current_url, a['href'])) for a in soup.find_all('a', href=True)]
                if article_links:
                    for article_title, article_link in article_links:
                        self.result_text.text(f'{article_title}: {article_link}\n\n')
                else:
                    self.result_text.text('No articles found on the page.\n\n')

                # ページネーションのリンクがあれば次のページに移動
                next_page_link = soup.find('a', class_='next page-numbers')
                if next_page_link:
                    next_page_url = urljoin(driver.current_url, next_page_link['href'])
                    driver.get(next_page_url)
                else:
                    break  # ページネーションのリンクがなければ終了

        except requests.exceptions.RequestException as e:
            self.result_text.text(f"Failed to retrieve the page. Error: {e}\n")

def main():
    root = st
    app = WebScraperApp(root)
    app.search_on_website()

if __name__ == "__main__":
    main()
