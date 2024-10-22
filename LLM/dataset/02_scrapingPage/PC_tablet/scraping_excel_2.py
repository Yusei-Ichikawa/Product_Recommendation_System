#このファイルはscraping_excel.pyを実行して一回api通したやつの**とか数字の見出しを消してさらに綺麗にするプログラム

import requests
from bs4 import BeautifulSoup
import os
from openai import OpenAI
from dotenv import load_dotenv
from openai import AzureOpenAI
import pandas as pd
import shutil
import time

load_dotenv(dotenv_path=".env")

'''
使い方
1. 読み込むエクセルはすでにscraping_exel.pyを使って必要な情報がスクレイピングされた状態のやつ。
2. 製品情報を読み取って、'**'や'##'などの記号を消して複製したclean(本のファイル名).xlsxに書き込む
'''

# API関連
# ===============================================================================
api_base = "https://japaninternship-teamb-swedencentral.openai.azure.com/"  # あなたのエンドポイント
api_version = "2023-05-15"  # 使用するAPIバージョンを設定
api_key = "36095eb031a9415da06cd372d32c717a"  # あなたのAPIキー

deployment_name = "gpt-4o-mini"  # デプロイ名
model_name = "gpt-4o-mini"  # モデル名

client = AzureOpenAI(
  api_key =api_key,
  api_version = "2023-05-15",
  azure_endpoint =api_base
)
# ==============================================================================



def remove_symbols(text):
    """OpenAI APIを使用してテキストから製品情報を抽出する関数"""

    # APIキーを環境変数から取得
    # client.api_key = os.getenv("OPENAI_API_KEY")

    # APIの呼び出し方法を更新
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "文章から特定の記号 '**'、'###'、'-' を削除してください。他のテキストはそのまま残して、結果を出力してください。"},
            {"role": "user", "content": text}
        ],
        max_tokens=1024
    )
    return response.choices[0].message.content.strip()





# エクセルファイルを複製して、複製先のファイルに書き込む
# ===============================================================================================

# Excelファイルを読み込む
file_path = '../../02_scrapingPage/PC_tablet/getURLData/testApple_urls2.xlsx' # 読み書きするExcelファイルのpath

# ファイル名とディレクトリのパスを取得
dir_name = os.path.dirname(file_path)
base_name = os.path.basename(file_path)

# 新しいファイル名を生成
new_file_name = 'clean' + base_name
new_file_path = os.path.join(dir_name, new_file_name)

# 元のファイルを新しいファイル名で複製
shutil.copyfile(file_path, new_file_path)

# 複製したファイルを読み込む
df = pd.read_excel(new_file_path)


# 製品説明列をループ処理
for index, row in df.iterrows():
    url = row['url']
    start_time = time.time()  # 処理開始時刻
    product_description = row['製品説明']
    clean_description = remove_symbols(product_description)
    df.at[index, '製品説明'] = str(clean_description)
    df.to_excel(new_file_path, index=False)  # 各URL処理後にExcelファイルに保存
    end_time = time.time()  # 処理終了時刻
    elapsed_time = end_time - start_time  # 経過時間を計算
    print(f"remove symbols {index + 1}: {url} の処理にかかった時間: {elapsed_time:.2f}秒")

# ==============================================================================================
