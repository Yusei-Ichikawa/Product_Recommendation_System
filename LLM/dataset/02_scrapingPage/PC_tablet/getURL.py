import requests
from bs4 import BeautifulSoup
import pandas as pd

# Webページからデータを取得
url = "https://www.tanomail.com/special/j/bf/product/pc-special-offer-soft.html"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 製品のURLを抽出
base_url = "https://www.tanomail.com"
product_links = []
for item in soup.find_all("a", class_="tano-item-name"):
    link = item.get('href')
    if link and "/product/" in link:
        full_link = base_url + link
        product_links.append(full_link)

# 取得したURLをコンソールに出力
for url in product_links:
    print(url)  # コンソールにURLを出力


import pandas as pd

# 空のデータフレームを作成し、カラムの見出しを設定
columns = ['url', 'id', '品名', '大カテゴリ', '小カテゴリ', '値段', '製品説明', '画像']
df = pd.DataFrame(columns=columns)

# URLデータをデータフレームに追加
url_data = [{'url': link} for link in product_links]  # URLリストを辞書のリストに変換
new_rows = pd.DataFrame(url_data)  # 新しいデータフレームを作成
df = pd.concat([df, new_rows], ignore_index=True)  # 既存のデータフレームに新しい行を追加

# Excelファイルに保存
df.to_excel('./getURLData/周辺機器ソフト_urls.xlsx', index=False)
