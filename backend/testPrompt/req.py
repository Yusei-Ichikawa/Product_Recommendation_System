import requests

# チャットエンドポイントへのPOSTリクエスト
url = 'http://127.0.0.1:5000/chat'
data = {
    "prompt": "アートギャラリーが展示作品のカタログを作成するために、高精細な画像を扱えるプリンターを求めています。色の精度と細部の再現性が求められます。",
    "chat_id": "7",
    "user_id": "18"
}
response = requests.post(url, json=data)
print(response.text)  # サーバーからの応答を表示