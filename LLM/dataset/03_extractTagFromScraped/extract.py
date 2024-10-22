import pandas as pd
import openai
import time
from openai import AzureOpenAI

# OpenAI APIの設定
#openai.api_key = ''

'''
def extract_info(text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-2024-07-18",  # 最新のモデル名を使用
        prompt=f"大カテゴリは「複合機・コピー機・プリンター」です。次の文章から製品名、小カテゴリ、値段を抽出してください：\n{text}",
        max_tokens=150
    )
    return response['choices'][0]['text'].strip()
'''

# def extract_info(text):
#     response = openai.ChatCompletion.create(
#         model="gpt-4o-mini-2024-07-18",
#         messages=[
#             {"role": "system", "content": "製品情報を抽出します。"},
#             {"role": "user", "content": f"大カテゴリは「複合機・コピー機・プリンター」です。次の文章から製品名、小カテゴリ、値段を抽出してください：\n{text}"}
#         ],
#         max_tokens=150,
#         temperature=0.5
#     )
#     extracted_text = response['choices'][0]['message']['content'].strip()
#     print("Extracted Text:", extracted_text)  # 抽出されたテキストを表示
#     return response['choices'][0]['message']['content'].strip()



#API関連
#===============================================================================
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
#==============================================================================



def extract_info(text):
    """OpenAI APIを使用してテキストから製品情報を抽出する関数"""

    # APIキーを環境変数から取得
    # client.api_key = os.getenv("OPENAI_API_KEY")

    # APIの呼び出し方法を更新
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            # {"role": "system", "content": "製品情報を抽出します。次の文章から品名、値段を抽出してください。「値段+詳細」などは書かずに品名と値段のみをそのまま抽出して。もし値段が複数ある場合は本体価格や提供価格、またはそのいずれもない場合は一番高い値段を書いて。"},
            {"role": "system", "content": "以下の文章から製品の品名と価格を抽出してください。価格は数字のみを記載し、価格に関する説明や追加情報は含めないでください。価格が複数記載されている場合は、本体価格や提供価格を優先して抽出してください。それらが明確でない場合は、最も高い価格の数字のみを抽出してください。「製品名:」や「価格：」のような書き方はしないで。出力形式「製品名/1,000円」"},
            {"role": "user", "content": text}
        ],
        max_tokens=1024
    )
    return response.choices[0].message.content.strip()

# def extract_info(text):
#     """OpenAI APIを使用してテキストから製品情報を抽出する関数"""

#     # APIキーを環境変数から取得
#     # client.api_key = os.getenv("OPENAI_API_KEY")

#     # APIの呼び出し方法を更新
#     response = openai.chat.completions.create(
#         model="gpt-4-turbo",
#         # model="gpt-4o-mini-2024-07-18",
#         messages=[
#             # {"role": "system", "content": "製品情報を抽出します。次の文章から品名、値段を抽出してください。「値段+詳細」などは書かずに品名と値段のみをそのまま抽出して。もし値段が複数ある場合は本体価格や提供価格、またはそのいずれもない場合は一番高い値段を書いて。"},
#             # {"role": "system", "content": "以下の文章から製品の品名と価格を抽出してください。ただし、以下の点に注意して抽出作業を行ってください。1.品名と価格のみを抽出し、その他の詳細情報（例えば「値段+詳細」など）は記載しないでください。2.製品に複数の価格が記載されている場合は、本体価格や提供価格を優先して記載してください。本体価格や提供価格が見当たらない場合は、最も高い価格を抽出してください。"},
#             {"role": "system", "content": "以下の文章から製品の品名と価格を抽出してください。価格は数字のみを記載し、価格に関する説明や追加情報は含めないでください。価格が複数記載されている場合は、本体価格や提供価格を優先して抽出してください。それらが明確でない場合は、最も高い価格の数字のみを抽出してください。「製品名:」や「価格：」のような書き方はしないで。出力形式「製品名/1,000円」"},
#             {"role": "user", "content": text}
#             # {"role": "system", "content": "製品情報を抽出します。"},
#             # {"role": "user", "content": f"次の文章から製品名、値段を抽出してください：\n{text}"}

#         ],
#         max_tokens=1024
#     )
#     return response.choices[0].message.content.strip()

# Excelファイルを読み込む
df = pd.read_excel('../02_scrapingPage/PC_tablet/getURLData/testendedcleanallPC_tablet_urls.xlsx')

# 結果を格納するための新しいDataFrame
results_df = pd.DataFrame(columns=['品名', '値段'])

# DataFrameの初期化
df['品名'] = ''
df['値段'] = ''

# `製品説明`情報がある列を指定
description_col_index = 6

# 製品説明されたデータが含まれる列を処理
for index, row in df.iterrows():
    # if pd.isna(row['品名']) or not row['品名'].strip() or pd.isna(row['値段']) or not row['値段'].strip():
        start_time = time.time()  # 処理開始時間
        description_text = row.iloc[description_col_index]  # 製品説明列
        extracted_info = extract_info(description_text)
        info_parts = extracted_info.split('/')
        if len(info_parts) >= 2:
            df.at[index, '品名'] = info_parts[0].strip()
            df.at[index, '値段'] = info_parts[1].strip()
            df.to_excel('../02_scrapingPage/PC_tablet/getURLData/testendedcleanallPC_tablet_urls.xlsx', index=False)
            elapsed_time = time.time() - start_time  # 処理にかかった時間
            print(f"Row {index} updated: {df.at[index, '品名']}, {df.at[index, '値段']} in {elapsed_time:.2f} seconds.")
        else:
            print(f"Row {index}: No valid data extracted.")
        df.to_excel('../02_scrapingPage/PC_tablet/getURLData/testendedcleanallPC_tablet_urls.xlsx', index=False)
    # else:
        # print(f"Row {index}: Skipped because data already exists.")
