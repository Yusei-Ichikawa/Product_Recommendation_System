import pandas as pd
import openai
import os
import time

# APIキーの読み込み
with open('../../../api_key.txt', 'r') as file:
    api_key = file.read().strip()
# APIキー設定
openai.api_key = api_key
print(api_key)

# openai.api_key = ''

# タグ設定
# =================================
keyword = "角度調整"
# =================================

#
def check_keyword(text, keyword):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたは製品の仕様を判定するエキスパートです。"},
            {"role": "user", "content": f"次の文章から、この製品が{keyword}可能かどうかを判断し、「{keyword}可能」または「{keyword}不可能」と答えてください。{keyword}についての記載がない場合は「{keyword}不可能」と答えてください：\n{text}"}
        ],
        max_tokens=10,
        temperature=0.5
    )
    return response['choices'][0]['message']['content'].strip()

# Excelファイルを読み込む
df = pd.read_excel('./latestdata/otsuka_DB_latest.xlsx')
# df = pd.read_excel('./test.xlsx')

# `スクレイピング`列の名前を指定して取得
scraped_col_name = "製品説明"

# 新しい列"角度調節"を追加
df[keyword] = ''

# スクレイピングされたデータが含まれる列を処理
for index, row in df.iterrows():
    if index > 40:  # 16行目まで処理
            break
    scraped_text = row[scraped_col_name]  # 列名で指定

    # 製品説明セルに何も入ってなかったら
    if scraped_text == "":
         break

    try:
        adjustment_result = check_keyword(scraped_text, keyword)
        df.at[index, keyword] = adjustment_result

    except openai.error.RateLimitError as e:
        print("レートリミットに到達しました。しばらく待ってから再試行します。")
        time.sleep(20)  # レートリミット解除まで20秒待つ

        adjustment_result = check_keyword(scraped_text, keyword)
        df.at[index, keyword] = adjustment_result

# 更新したDataFrameを新しいExcelファイルとして保存
df.to_excel('./latestdata/otsuka_DB_tag.xlsx', index=False)
