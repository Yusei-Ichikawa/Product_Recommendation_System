import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

def fetch_and_save_page_content(url, save_dir):
    # ディレクトリが存在しない場合は作成
    os.makedirs(save_dir, exist_ok=True)

    # Webページからコンテンツを取得
    response = requests.get(url)
    response.raise_for_status()  # ステータスコードが200でない場合はエラーを発生させる

    # HTMLコンテンツを解析
    soup = BeautifulSoup(response.text, 'html.parser')

    # テキストのみを抽出
    page_text = soup.get_text(separator='\n', strip=True)

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
