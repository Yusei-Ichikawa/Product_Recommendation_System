from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
from datetime import datetime

def fetch_and_save_page_content(url, save_dir):
    # ディレクトリが存在しない場合は作成
    os.makedirs(save_dir, exist_ok=True)

    # セレニウムの設定
    options = Options()
    options.headless = True  # ヘッドレスモードで実行
    service = Service(ChromeDriverManager().install())

    # WebDriverの初期化
    driver = webdriver.Chrome(service=service, options=options)

    # ページを開く
    driver.get(url)

    # ページのロードを少し待つ
    driver.implicitly_wait(10)  # 10秒待つ

    # ページのテキストを取得
    page_text = driver.find_element(By.TAG_NAME, "body").text

    # WebDriverを閉じる
    driver.quit()

    # 現在の日付と時刻を取得
    current_time = datetime.now().strftime("%m_%d_%H:%M:%S")

    # 結果をテキストファイルに保存するためのファイルパス
    save_path = os.path.join(save_dir, f'Scraped_{current_time}.txt')

    # 結果をテキストファイルに保存
    with open(save_path, 'w', encoding='utf-8') as file:
        file.write(page_text)

    print(f'File saved: {save_path}')

# URLと保存ディレクトリを指定
url = 'https://www.tanomail.com/product/6894177/'
save_dir = './outputScrapingPage'

# 関数を実行
fetch_and_save_page_content(url, save_dir)
