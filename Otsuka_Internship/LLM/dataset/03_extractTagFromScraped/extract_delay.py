import pandas as pd
import openai
import time

# OpenAI APIの設定
openai.api_key = ''

'''
def extract_info(text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-2024-07-18",  # 最新のモデル名を使用
        prompt=f"次の文章から製品名、大カテゴリ、小カテゴリ、値段を抽出してください：\n{text}",
        max_tokens=150
    )
    return response['choices'][0]['text'].strip()
'''

def extract_info(text):
    # ChatCompletionを用いた製品情報の抽出
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-2024-07-18",  # 使用するモデルを確認し、適切に設定
        messages=[
            {"role": "system", "content": "製品情報を抽出します。"},
            {"role": "user", "content": f"次の文章から製品名、大カテゴリ、小カテゴリ、値段を抽出してください：\n{text}"}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

# Excelファイルを読み込む
df = pd.read_excel('/Users/ichikawayousay/Desktop/otsuka_DB_2.xlsx')

# `スクレイピング`情報がある列を指定
scraped_col_index = 5

# 必要な処理を続行
if df.shape[1] > scraped_col_index:
    # 抽出した情報を保存するための新しい列を初期化
    df['品名'] = ''
    df['大カテゴリ'] = ''
    df['小カテゴリ'] = ''
    df['値段'] = ''

    # 'scraped'列から情報を抽出
    for index, row in df.iterrows():
        if index > 30:  # 30行目まで処理
            break
        scraped_text = row.iloc[scraped_col_index]
        try:
            extracted_info = extract_info(scraped_text)
            info_parts = extracted_info.split('/')
            if len(info_parts) >= 4:
                df.at[index, '品名'] = info_parts[0].strip()
                df.at[index, '大カテゴリ'] = info_parts[1].strip()
                df.at[index, '小カテゴリ'] = info_parts[2].strip()
                df.at[index, '値段'] = info_parts[3].strip()
        except openai.error.RateLimitError as e:
            print("レートリミットに到達しました。しばらく待ってから再試行します。")
            time.sleep(20)  # レートリミット解除まで20秒待つ
            # 再試行
            extracted_info = extract_info(scraped_text)
            info_parts = extracted_info.split('/')
            if len(info_parts) >= 4:
                df.at[index, '品名'] = info_parts[0].strip()
                df.at[index, '大カテゴリ'] = info_parts[1].strip()
                df.at[index, '小カテゴリ'] = info_parts[2].strip()
                df.at[index, '値段'] = info_parts[3].strip()

    # 更新したDataFrameを新しいExcelファイルとして保存
    df.to_excel('/Users/ichikawayousay/02_univercity/大学院/就活/大塚商会インターン/updated_file-1.xlsx', index=False)
else:
    print("エラー: 'スクレイピング' 列が見つかりません。列インデックスを確認してください。")
