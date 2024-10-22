import openai

openai.api_key = ""

response = openai.ChatCompletion.create(
    model="ft:gpt-4o-2024-08-06:personal:printer20-2:A0id3ljp:ckpt-step-80",  # ここにファインチューニングされたモデルIDを指定
    messages=[
        {"role": "system", "content": """このチャットボットは営業向けに複合機やプリンターなどに関する質問に答えます。

         以下のようなjson形式で製品について回答してください。

            {
                "商品ID": <>,
                "商品名": "<>",
                "価格": "<>",
                "大カテゴリ": "<>",
                "小カテゴリ": "<>",
                "特徴": "<>"
            }

         """},
        {"role": "user", "content": """
        RICOH IM C8000について教えて
"""}
    ]
)

print(response['choices'][0]['message']['content'])
