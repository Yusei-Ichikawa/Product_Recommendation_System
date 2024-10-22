import pandas as pd
import openai
import time
from openai import AzureOpenAI
import re


# OpenAI APIの設定
# openai.api_key = ''

# API関連
# ===============================================================================
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
# ==============================================================================

def extract_info(text):
    # ChatCompletionを用いた製品情報の抽出
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            # {"role": "system", "content": "製品名、詳細仕様、オプション情報、および複数製品が存在する場合の各製品の特長を抽出してください。価格情報が明示されている製品やオプションについてはそれぞれの価格を記載し、価格情報がない場合は、市場相場や類似製品の価格を参考に適切な価格を設定してください。価格は全て税込みで表示し、明示的に税込みであることを記載する必要はありません。"},
            {"role": "system", "content": "製品情報を抽出します。"},
            {"role": "user", "content": f"次の文章から製品名、大カテゴリ、小カテゴリ、値段を抽出してください：\n{text}"}
        ],
        max_tokens=1024
    )
    return response.choices[0].message.content.strip()

def parse_extracted_info(extracted_info):
    # 正規表現を使用して各カテゴリを抽出
    product_name = re.search(r'製品名: (.+)', extracted_info)
    major_category = re.search(r'大カテゴリ: (.+)', extracted_info)
    minor_category = re.search(r'小カテゴリ: (.+)', extracted_info)
    price = re.search(r'値段: (.+)', extracted_info)

    # 抽出したデータを辞書として返す
    return {
        '品名': product_name.group(1) if product_name else '',
        '大カテゴリ': major_category.group(1) if major_category else '',
        '小カテゴリ': minor_category.group(1) if minor_category else '',
        '値段': price.group(1) if price else ''
    }

# Excelファイルを読み込む
excel_file_path = '../00_latestData/tanomall_data.xlsx'
df = pd.read_excel(excel_file_path)

# `スクレイピング`情報がある列を指定
# "製品説明" 列を指定
scraped_col_index = df.columns.get_loc("製品説明")

# 必要な処理を続行
if df.shape[1] > scraped_col_index:
    # 抽出した情報を保存するための新しい列を初期化
    df['品名'] = ''
    df['大カテゴリ'] = ''
    df['小カテゴリ'] = ''
    df['値段'] = ''

    # DataFrameの更新部分
    for index, row in df.iterrows():
        if index > 30:
            break
        scraped_text = row["製品説明"]
        try:
            extracted_info = extract_info(scraped_text)
            info_dict = parse_extracted_info(extracted_info)
            df.at[index, '品名'] = info_dict['品名']
            df.at[index, '大カテゴリ'] = info_dict['大カテゴリ']
            df.at[index, '小カテゴリ'] = info_dict['小カテゴリ']
            df.at[index, '値段'] = info_dict['値段']
        except openai.error.RateLimitError:
            print("レートリミットに到達しました。しばらく待ってから再試行します。")
            time.sleep(20)
            extracted_info = extract_info(scraped_text)
            info_dict = parse_extracted_info(extracted_info)
            df.at[index, '品名'] = info_dict['品名']
            df.at[index, '大カテゴリ'] = info_dict['大カテゴリ']
            df.at[index, '小カテゴリ'] = info_dict['小カテゴリ']
            df.at[index, '値段'] = info_dict['値段']

    # 更新したDataFrameを新しいExcelファイルとして保存
    df.to_excel('../00_latestData/tanomall_data_updated.xlsx', index=False)
else:
    print("エラー: 'スクレイピング' 列が見つかりません。列インデックスを確認してください。")
