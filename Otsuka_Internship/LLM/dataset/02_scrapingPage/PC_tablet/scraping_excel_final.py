import requests
from bs4 import BeautifulSoup
import os
from openai import OpenAI
#from dotenv import load_dotenv
from openai import AzureOpenAI
import pandas as pd
import time

#load_dotenv(dotenv_path=".env")

'''
使い方
1. 読み込むエクセルにURLを入れておく。
2. URLからスクレイピングした文章をapiに通して必要な情報を抜き出す→製品情報の列に入力
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

# ============== nonjavaScraping.py ============================================
def fetch_and_save_page_content(url):
    """Webページからscraping"""

    # Webページからコンテンツを取得
    response = requests.get(url)
    response.raise_for_status()  # ステータスコードが200でない場合はエラーを発生させる

    # HTMLコンテンツを解析
    soup = BeautifulSoup(response.text, 'html.parser')

    # テキストのみを抽出
    page_text = soup.get_text(separator='\n', strip=True)

    return page_text
# ==============================================================================

# ================= apiPlaintext.py ============================================
def extract_product_info(text):
    """OpenAI APIを使用してテキストから製品情報を抽出する関数"""

    # APIキーを環境変数から取得
    # client.api_key = os.getenv("OPENAI_API_KEY")

    # APIの呼び出し方法を更新
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            # {"role": "system", "content": "製品名、詳細仕様、オプション情報、および複数製品が存在する場合の各製品の特長を抽出してください。価格情報が明示されている製品やオプションについてはそれぞれの価格を記載し、価格情報がない場合は、市場相場や類似製品の価格を参考に適切な価格を設定してください。価格は全て税込みで表示し、明示的に税込みであることを記載する必要はありません。"},
            {"role": "system", "content": "テキストから製品名、詳細仕様、オプション情報を抽出し、各オプションに対して価格を設定してください。価格情報が明示されていない場合でも、通常追加料金が発生すると考えられるオプション（例：プロセッサアップグレード、ストレージアップグレードなど）には、市場の類似製品や一般的な価格帯を参考にして、自動的に価格を設定してください。価格設定は全て税込みで行い、その価格が税込みであることを明示する必要はありません。"},
            {"role": "user", "content": text}
        ],
        max_tokens=5000
    )
    return response.choices[0].message.content.strip()
# ==============================================================================

# # Excelファイルを読み込む
# file_path = '../../02_scrapingPage/PC_tablet/getURLData/allPC_tablet_urls.xlsx' # 読み書きするExcelファイルのpath
# df = pd.read_excel(file_path, dtype={'製品説明': str})


# # URL列をループ処理
# for index, row in df.iterrows():
#     # if pd.notna(row['製品説明']) and row['製品説明'].strip():  # すでに何かしらのテキストがある場合はスキップ
#     #     continue
#     if pd.notna(row['製品説明']) and row['製品説明'].strip():
#         continue
#     start_time = time.time()  # 処理開始時刻
#     url = row['url']
#     page_text = fetch_and_save_page_content(url)
#     product_info = extract_product_info(page_text)
#     df.at[index, '製品説明'] = str(product_info)  # product_info を文字列にキャスト
#     df.to_excel(file_path, index=False)# 変更をExcelファイルに書き戻す
#     end_time = time.time()  # 処理終了時刻
#     elapsed_time = end_time - start_time  # 経過時間を計算
#     print(f"URL {index + 1}: {url} の処理にかかった時間: {elapsed_time:.2f}秒")




# scraping_excel_2.py
# ==========================================================================================

import shutil

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
        max_tokens=5000
    )
    return response.choices[0].message.content.strip()



# エクセルファイルを複製して、複製先のファイルに書き込む
# ===============================================================================================

# Excelファイルを読み込む
file_path = '../../02_scrapingPage/PC_tablet/getURLData/allPC_tablet_urls.xlsx' # 読み書きするExcelファイルのpath
df = pd.read_excel(file_path, dtype={'製品説明': str})
df['製品説明'] = df['製品説明'].astype(str)

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

# =======================================================================================================
#=========================================================================================================
