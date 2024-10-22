import pandas as pd
import openai
import os
import random
from openai import AzureOpenAI

def generate_product_info(prompt):
    """OpenAI APIを使用して架空の製品情報を生成する関数"""
    try:
        response = openai.chat.completion.create(
            model="gpt-4-turbo",
        messages=[
            # {"role": "system", "content": "製品情報を抽出します。次の文章から品名、値段を抽出してください。「値段+詳細」などは書かずに品名と値段のみをそのまま抽出して。もし値段が複数ある場合は本体価格や提供価格、またはそのいずれもない場合は一番高い値段を書いて。"},
            # {"role": "system", "content": "以下の文章から製品の品名と価格を抽出してください。ただし、以下の点に注意して抽出作業を行ってください。1.品名と価格のみを抽出し、その他の詳細情報（例えば「値段+詳細」など）は記載しないでください。2.製品に複数の価格が記載されている場合は、本体価格や提供価格を優先して記載してください。本体価格や提供価格が見当たらない場合は、最も高い価格を抽出してください。"},
            {"role": "system", "content": "次の製品について説明してください。"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"


    # )
    # return response.choices[0].message.content.strip()


def main():
    # OpenAI APIの設定
    openai.api_key = ''

    # 既存のExcelファイルを読み込む
    file_path = './makeProduct.xlsx'
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['url', 'id', '品名', '大カテゴリ', '小カテゴリ', '値段', '製品説明', '画像'])

    # 最初の空白行を検出
    first_empty_row = df[df.isnull().all(axis=1)].index.min()
    if pd.isna(first_empty_row):
        first_empty_row = len(df)

    # 5個の架空の製品情報を生成して追加
    for _ in range(5):
        product_name = generate_product_info("架空の製品名を生成してください。")
        major_category = "コンピュータ・テクノロジー"
        minor_category = generate_product_info("架空の小カテゴリを生成してください。例：セキュリティソフト")
        price = f"{random.randint(5000, 100000)}円"
        description = generate_product_info("架空の製品説明を生成してください。")

        # データフレームに情報を追加
        df.loc[first_empty_row, ['品名', '大カテゴリ', '小カテゴリ', '値段', '製品説明']] = [product_name, major_category, minor_category, price, description]
        df.loc[first_empty_row, ['url', 'id', '画像']] = [None, None, None]  # None を使用してセルを埋める
        first_empty_row += 1

    # Excelファイルに保存（既存のデータを上書き）
    df.to_excel(file_path, index=False)

if __name__ == "__main__":
    main()
