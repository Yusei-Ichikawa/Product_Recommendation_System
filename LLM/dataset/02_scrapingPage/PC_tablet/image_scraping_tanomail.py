import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import pandas as pd
import base64

# ファイルパス指定
# ====================================================
input_file_path = "../../00_latestData/finalData.xlsx"
# ====================================================

# 画像をBase64エンコードする関数
def encode_image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def save_img_from_web(page_url, df, row_index):
    # img_name: 商品名
    img_name = page_url.split("/")[-2]
    
    # Webページを取得
    response = requests.get(page_url)
    
    # レスポンスが成功したかを確認
    if response.status_code == 200:
        # BeautifulSoupでHTMLを解析
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ハイライトされた部分の親要素を指定して img タグを検索
        section_tag = soup.find('section')
        img_tag = section_tag.find('img')
        
        if img_tag:
            # 画像のURLを取得
            img_url = img_tag['src']
            print(img_url)
            img_url = ("https://www.tanomail.com" + img_url)
            
            # 画像をダウンロード
            img_response = requests.get(img_url)
            
            if img_response.status_code == 200:
                # 画像をバイトデータに変換
                image = Image.open(BytesIO(img_response.content))
                
                # # ディレクトリが存在しない場合は作成
                # if not os.path.exists("./images"):
                #     os.makedirs("./images")
                
                # # 画像保存
                # image.save(f"./images/{img_name}.jpg")

                # 画像をエンコードして文字列に変換
                img_base64_str = encode_image_to_base64(image)

                # エクセルの該当セルにエンコードされた画像を保存
                df.at[row_index, '画像'] = img_base64_str
                
                print(f"画像が正常に保存され、エクセルに追加されました: {img_name}.jpg")
            else:
                print("画像のダウンロードに失敗しました。")
        else:
            print("指定されたタグ内に画像が見つかりませんでした。")
    else:
        print("Webページの取得に失敗しました。ステータスコード:", response.status_code)

# エクセルファイルの読み込み
excel_file = input_file_path  # ここにエクセルファイルのパスを指定してください
df = pd.read_excel(excel_file)

# "url"という列からデータを取得
url_list = df['url'].dropna().tolist()

# 全URLに対して処理
for index, url in enumerate(url_list):
    save_img_from_web(url, df, index)

# 変更をエクセルファイルに保存
filepath = input_file_path.split(".xlsx")
df.to_excel(f'{filepath[0]}_add_img.xlsx', index=False)
