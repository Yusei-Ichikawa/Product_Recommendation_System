import requests
from bs4 import BeautifulSoup
import pandas as pd
import openai

# OpenAIのAPIキー設定
openai.api_key =  ""

def fetch_product_description(url):
    # ページにアクセスしてHTMLを取得
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 製品の説明を抽出（HTML構造に基づいて適宜変更）
    description = soup.find('div', class_='main-body').text.strip()
    return description

def extract_information_with_chatgpt(description):
    # ChatGPTを使って情報を抽出
    response = openai.Completion.create(
        engine="gpt-4o",
        prompt=f"以下の製品説明から重要な特徴をリストアップしてください：\n{description}",
        max_tokens=150
    )
    return response.choices[0].text.strip()

def save_to_excel(data, filename='output.xlsx'):
    # Excelファイルに保存
    df = pd.DataFrame([{'製品特徴': data}])
    df.to_excel(filename, index=False)

# 実行例
url = 'https://www.otsuka-shokai.co.jp/products'  # 大塚商会の製品ページURL
description = fetch_product_description(url)
features = extract_information_with_chatgpt(description)
save_to_excel(features)

