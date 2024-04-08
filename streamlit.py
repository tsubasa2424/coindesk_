import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Streamlitアプリケーションのタイトルを設定
st.title("Web Scraper")

# キーワードの入力ウィジェット
keyword_input = st.text_input("Enter the keyword:")

# 検索ボタンが押されたときの処理
if st.button("Search"):
    # 検索結果を表示するテキストウィジェット
    result_text = st.empty()

    # Webスクレイピングを実行する関数
    def scrape_website(keyword):
        coindesk_url = "https://www.coindeskjapan.com"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")  # ウィンドウを最大化
        chrome_options.add_argument("--headless")  # ブラウザを非表示にする
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(coindesk_url)

        # 検索ボックスが見つかるまで待機
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "s"))
        )

        # サイト内検索ボックスにキーワードを自動入力
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)

        scrape_search_results(driver, keyword)

    # 検索結果をスクレイピングする関数
    def scrape_search_results(driver, keyword):
        try:
            while True:
                response = requests.get(driver.current_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # 記事のタイトルとリンクを取得して表示
                article_links = [(a.text.strip(), urljoin(driver.current_url, a['href'])) for a in soup.find_all('a', href=True)]
                if article_links:
                    for article_title, article_link in article_links:
                        result_text.text(f'{article_title}: {article_link}\n\n')
                else:
                    result_text.text('No articles found on the page.\n\n')

                # ページネーションのリンクがあれば次のページに移動
                next_page_link = soup.find('a', class_='next page-numbers')
                if next_page_link:
                    next_page_url = urljoin(driver.current_url, next_page_link['href'])
                    driver.get(next_page_url)
                else:
                    break  # ページネーションのリンクがなければ終了

        except requests.exceptions.RequestException as e:
            result_text.text(f"Failed to retrieve the page. Error: {e}\n")

    # キーワードが入力されている場合、Webスクレイピングを実行
    if keyword_input:
        scrape_website(keyword_input)
