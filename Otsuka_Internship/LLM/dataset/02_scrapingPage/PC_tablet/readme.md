# まつけんが実装してくれた（次に実装すべきの1-3）

1. LLM/dataset/00_latestData/PC_tablet/任意のファイル.xlsxの"url"の列に製品情報のWebページのURLを貼る
2. LLM/dataset/02_scrapingPage/PC_tablet/scraping_excel.pyを実行
3. 任意のファイル.xlsxに製品情報が上書き保存される（出力先のExcelファイルパスは自由に）


# yusei情報共有

- nonjavaScrape.pyやjavaScrape.py、apiPlaintext.pyはもう使う必要はない。

- scraping_excel_final.pyでurlからスクレイピングしてsymbolも消す所までできる(下のscraping_excel_2.pyまでを内包)

- scraping_excel.pyを実行 ▶ scraping_excel_2.pyで'**'など消す ▶ testPCExtractDelay.pyで製品名や値段を抽出する、で完結。



- モデルはgpt-4o-miniで十分だったので大塚商会のを使わせてもらう。

- カテゴリの抽出はapiを使ってやるつもりはないので、後で実装する
