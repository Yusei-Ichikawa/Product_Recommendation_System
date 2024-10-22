import json

# 入力ファイルと出力ファイルのパスを指定
input_file = 'trainingFiles/chat0827-0.jsonl'
output_file = 'trainingFiles/chat0827-1.jsonl'

# ファイルを読み込み、変換後の結果を保存するリスト
converted_data = []

# JSONLファイルを読み込み、変換を実行
with open(input_file, 'r', encoding='utf-8') as infile:
    for line in infile:
        # 各行をJSONとしてパース
        data = json.loads(line)
        
        # messagesキーの各contentを変更
        if 'messages' in data:
            for message in data['messages']:
                if 'content' in message:
                    message['content'] = message['content'].replace(", ", "で、")
        
        # 変換後のデータをリストに追加
        converted_data.append(data)

# 変換後のデータを新しいJSONLファイルに書き込み
with open(output_file, 'w', encoding='utf-8') as outfile:
    for item in converted_data:
        outfile.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"変換が完了しました。出力ファイル: {output_file}")
