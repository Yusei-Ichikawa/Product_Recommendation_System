#これは特長から製品名やカテゴリ、値段を抽出するコード（エクセルに出力する機能も作りたいが保留）

import pandas as pd
import openai
import time

# OpenAI APIの設定
openai.api_key = ''

'''
def extract_info(text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-2024-07-18",  # 最新のモデル名を使用
        prompt=f"大カテゴリは「複合機・コピー機・プリンター」です。次の文章から製品名、小カテゴリ、値段を抽出してください：\n{text}",
        max_tokens=150
    )
    return response['choices'][0]['text'].strip()
'''

def extract_info(text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": "製品情報を抽出します。"},
            {"role": "user", "content": f"大カテゴリは「複合機・コピー機・プリンター」です。次の文章から製品名、小カテゴリ、値段を抽出してください：\n{text}"}
        ],
        max_tokens=150,
        temperature=0.5
    )
    extracted_text = response['choices'][0]['message']['content'].strip()
    print("Extracted Text:", extracted_text)  # 抽出されたテキストを表示
    return response['choices'][0]['message']['content'].strip()

# Excelファイルを読み込む
df = pd.read_excel('/Users/ichikawayousay/Desktop/otsuka_DB_2.xlsx')

# 結果を格納するための新しいDataFrame
results_df = pd.DataFrame(columns=['name', 'parent_category', 'child_category', 'price'])

# `スクレイピング`情報がある列を指定
scraped_col_index = 5

# DataFrameの初期化
df['name'] = ''
df['parent_category'] = ''
df['child_category'] = ''
df['price'] = ''

# スクレイピングされたデータが含まれる列を処理
for index, row in df.iterrows():
    if index > 3:  # 4行目まで処理
        break
    scraped_text = row.iloc[scraped_col_index]  # 列インデックスに統一
    extracted_info = extract_info(scraped_text)
    info_parts = extracted_info.split('/')
    if len(info_parts) >= 4:
        df.at[index, 'name'] = info_parts[0].strip()
        df.at[index, 'parent_category'] = info_parts[1].strip()
        df.at[index, 'child_category'] = info_parts[2].strip()
        df.at[index, 'price'] = info_parts[3].strip()

# 更新したDataFrameを新しいExcelファイルとして保存
df.to_excel('/Users/ichikawayousay/02_univercity/大学院/就活/大塚商会インターン/updated_file.xlsx', index=False)
