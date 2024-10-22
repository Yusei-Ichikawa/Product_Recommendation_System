import pandas as pd

# エクセルファイルを読み込む
df = pd.read_excel('../PC_tablet/getURLData/testApple_urls2.xlsx')

# 'url'カラムの重複を削除（最初のエントリーを残す）
df = df.drop_duplicates(subset='url', keep='first')

# 結果を新しいエクセルファイルに保存する
df.to_excel('../PC_tablet/getURLData/testApple_urls2.xlsx', index=False)
