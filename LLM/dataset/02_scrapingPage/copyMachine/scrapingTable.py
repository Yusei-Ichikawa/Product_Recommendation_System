import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from openai import AzureOpenAI
import re


"""
[input]
url : 製品使用の表があるWebページのURLを指定

[output]
textFolder : 製品ごとの"仕様テキスト"。ファイル名（./textFolder/製品名~.txt）
→ txtファイル内の内容をスプレッドシートにコピペ？
"""


# API関連
# =============================================================================================
# Bチーム
api_base = "https://japaninternship-teamb-swedencentral.openai.azure.com/"  # あなたのエンドポイント
api_version = "2023-05-15"  # 使用するAPIバージョンを設定
api_key = ""  # あなたのAPIキー

deployment_name = "gpt-4o-mini"  # デプロイ名
model_name = "gpt-4o-mini"  # モデル名

client = AzureOpenAI(
  api_key =api_key,
  api_version = "2023-05-15",
  azure_endpoint =api_base
)
# =============================================================================================


# URLを指定（仕様の表があるページのURL）
# url = "https://www.otsuka-shokai.co.jp/products/mfp-copy-printer/hard/im-c-8000-6500/"
# url = "https://www.otsuka-shokai.co.jp/products/mfp-copy-printer/hard/im-9000-8000-7000/util.html"
url = "https://www.otsuka-shokai.co.jp/products/mfp-copy-printer/hard/im-c-6010-5510-4510-3510-3010-2510-2010/"


# table-normalを抽出
def get_table_text(url):
    # URLからHTMLを取得
    response = requests.get(url)

    # エンコーディングを適切に設定
    response.encoding = response.apparent_encoding
    html = response.text

    if response.status_code != 200:
        return "Failed to retrieve the webpage"

    # BeautifulSoupを使用してHTMLを解析
    soup = BeautifulSoup(html, 'html.parser')

    # loop
    # class=table-normal を持つ要素を見つける
    tables = soup.find_all(class_='table-normal')

    if not tables:
        return "No table with class 'table-normal' found"

    return tables


def separate_table_info(tables, model_name):
    separated_text = ""
    for table in tables:
        response = client.chat.completions.create(
            model=model_name , # model = "deployment_name".
            messages=[
                {"role": "system", "content": "あなたはHTML形式のテキストから製品仕様を抽出し、それを明瞭かつ整理された形式で出力するエキスパートです。製品ごとに仕様を区別し、それぞれの仕様を、情報を落とさずに全て表記してください。出力は製品情報のみにしてください。"},
                {"role": "user", "content": f"このHTMLテキストから製品の仕様を抽出して、製品ごとに出力してください。：\n{table}"}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        separated_text += str(response)
    return separated_text


# ファイルに書き出し
def write_to_file(data_list):

    # フォルダ名を指定
    folder_name = 'textFolder'
    # フォルダが存在しない場合にのみ作成
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    else:
        pass

    for data in data_list:
        # ファイル名を先頭20文字に設定し、使用不可の文字をアンダースコアに置換
        filename = f"./{folder_name}/" + re.sub(r'[\\/*?:"<>|]', "_", data[:20]) + ".txt"

        # 書き込み
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(data)

# tableデータ読み込み
tables = get_table_text(url)
# 製品ごとに抽出
adjustment_result = separate_table_info(tables, model_name)

# 製品名の部分で分割
result = re.split(r'\s*####\s+|\s*###\s+', adjustment_result)

# 関数を呼び出してファイルにデータを書き出す
write_to_file(result)
