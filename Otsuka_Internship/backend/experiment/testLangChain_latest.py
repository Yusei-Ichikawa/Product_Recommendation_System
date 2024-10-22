import openai
import pandas as pd
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai.chat_models import ChatOpenAI
from langchain.llms import OpenAI
import os
import json
import time
import Otsuka_Internship.backend.server.db as db
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

# エクセルファイルの読み込み
df = pd.read_excel('../LLM/dataset/latestdata/cleaned_data_latest.xlsx')

# Documentオブジェクトのリストを作成
documents = []
for _, row in df.iterrows():
    # 文書内容の構造を明確に
    content = f"id: {row['id']}\n品名: {row['品名']}\n大カテゴリ: {row['大カテゴリ']}\n小カテゴリ: {row['小カテゴリ']}\n 値段{row['値段']}\n製品説明: {row['製品説明']}\n"
    doc = Document(page_content=content, metadata={"source": row['品名']})
    documents.append(doc)



# エンベッディングの作成
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# ベクトルストアの構成を調整
vectorstore = FAISS.from_documents(documents, embeddings)

# 検索チェーンの作成
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4o-mini"),
    chain_type="refine",
    retriever=vectorstore.as_retriever(),
    return_source_documents=True,
)


# ユーザーの質問と回答をファイルに保存する関数
def save_query_and_answer(query, answer, filename):
    data = {"query": query, "answer": answer}
    with open(filename, "a", encoding="utf-8") as file:  # 'a' for append
        file.write(json.dumps(data, ensure_ascii=False) + "\n")  # JSONL形式で書き出し

# ファイルから過去のチャット履歴を読み込む関数
def load_chat_history(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return ""

# 検索関数の定義
def semantic_search(query, filename):
    # ファイルから過去の履歴を読み込み
    before_qa_history = load_chat_history(filename)

    # 新しい質問を履歴に追加してファイルに保存
    save_query_and_answer(query, "これは仮の回答です。", filename)

    bot_config = """
    あなたはデータベースを参照して以下の条件に適する複合機を提案できる心優しい日本人です。
    # 条件
    """
    reply_format = """
    # 返答形式
    4, 5個くらいの候補を出してほしいが、適するものがない場合はそれより少なくなっても良い。
    以下の形式で列挙して。
    ・id: ここにidを書いて
    ・その複合機を提案する理由: 理由
    上の形式の物以外の文字列は出力しないで
    """
    content = before_qa_history + bot_config + query + reply_format  # 新しい質問を追加

    # 実際にはここで機械学習モデルを使用した処理が必要
    # 仮の回答を返す
    return "これは仮の回答です。", "ソースドキュメント情報"

# 新しい質問を処理
new_query = "予算400万円以下"
filename = "chat1.txt"  # ユーザーが指定したかもしれない新しいファイル名
answer, source_docs = semantic_search(new_query, filename)
print("得られた回答:", answer)
