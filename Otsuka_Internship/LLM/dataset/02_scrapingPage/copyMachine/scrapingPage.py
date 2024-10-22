import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime

"""
[input]
url : 商品Webページ（どのページでも）

[output]
「表データ以外」のデータを出力。ファイル名 : output.txt
→ output.txtの中身をスプレッドシートにコピペ

"""

# URLからHTMLを取得
url = 'https://www.otsuka-shokai.co.jp/products/mfp-copy-printer/hard/im-c-8000-6500/'
response = requests.get(url)

# エンコーディングを適切に設定
response.encoding = response.apparent_encoding
html = response.text

# HTMLを解析
soup = BeautifulSoup(html, 'html.parser')

# IDが'main-body'のdivタグを取り出す
main_body = soup.find('div', id='main-body')

# headerタグを取り出す
header = soup.find_all('header')[1]

# 文字列に変換
header = str(header)
main_body = str(main_body)

# table-normalを削除
main_body = re.sub(r'<div class="table-normal">.*?</div>', '', main_body)
# footerを削除
main_body = re.sub(r'<footer >.*?</footer>', '', main_body)
# imageを削除
main_body = re.sub(r'<img .*?>', '', main_body)
# ページ下部削除
main_body = re.sub(r'<section><h2>複合機の導入.*?</section></div>', '', main_body)

# 結合
output = (header + main_body)

# 保存ディレクトリのパス
save_dir = './resultScrapingPage/'

# ディレクトリが存在しない場合は作成
os.makedirs(save_dir, exist_ok=True)

# 現在の日付と時刻を取得
current_time = datetime.now().strftime("%m_%d_%H:%M:%S")

# 結果をテキストファイルに保存するためのファイルパス
save_path = os.path.join(save_dir, f'Scraped_{current_time}.txt')

# 結果をテキストファイルに保存
with open(save_path, 'w', encoding='utf-8') as f:
    # f.write(header.text + main_body.text)
    f.write(output)
