from openai import OpenAI
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv(dotenv_path=".env")

# API関連
# =============================================================================================
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
# =============================================================================================

def load_text_from_file(file_path):
    """ファイルからテキストを読み込む関数"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

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
        max_tokens=1024
    )
    return response.choices[0].message.content.strip()

def save_text_to_file(text, file_path):
    """テキストをファイルに保存する関数"""
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)
    print(f'File saved: {file_path}')

# ファイルパス指定
input_file_path = './outputScraping/test.txt'  # 適切なファイル名に変更してください
output_file_path = input_file_path.replace('.txt', '_api.txt')

# ファイルからテキストを読み込む
page_text = load_text_from_file(input_file_path)

# テキストから製品情報を抽出
product_info = extract_product_info(page_text)

# 結果を新しいファイルに保存
save_text_to_file(product_info, output_file_path)
