#エクセルのscraped列に含まれるHTMLタグを全て削除し、プレーンなテキストにする

import pandas as pd
from bs4 import BeautifulSoup

# Excelファイルを読み込む
df = pd.read_excel('./latestdata/otsuka_DB_latest.xlsx')

# 'scraped'カラムにアクセスし、HTMLをクリーンアップ
def clean_html(content):
    # データがNaNまたは数値型の場合、空の文字列を返す
    if pd.isna(content) or isinstance(content, float):
        return ""
    soup = BeautifulSoup(str(content), 'html.parser')
    return soup.get_text(strip=True)

# 'scraped'カラムにclean_html関数を適用
df['製品説明'] = df['製品説明'].apply(clean_html)

# 結果を新しいExcelファイルに保存
df.to_excel('cleaned_data_latest.xlsx', index=False)
