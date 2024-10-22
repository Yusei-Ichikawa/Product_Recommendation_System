import pandas as pd
import os
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings  # 修正後のインポートパス
from langchain_openai.chat_models import ChatOpenAI  # 修正後のインポートパス
import json

# エクセルファイルの読み込み
df = pd.read_excel('./backend/cleaned_data.xlsx')

# Documentオブジェクトのリストを作成
documents = []
for _, row in df.iterrows():
    content = f"id: {row['id']}\nname: {row['name']}\nprice: {row['price']}\ncategory: {row['parent_category']} > {row['child_category']}"
    doc = Document(page_content=content, metadata={"source": row['name']})
    documents.append(doc)

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

# エンベッディングの作成
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# ベクトルストアの構成を調整
vectorstore = FAISS.from_documents(documents, embeddings)

# チャットモデルの初期化
chat_model = ChatOpenAI(model="gpt-4-turbo")  # 修正

# 検索チェーンの作成
qa_chain = RetrievalQA.from_chain_type(
    llm=chat_model,  # 修正
    chain_type="refine",
    retriever=vectorstore.as_retriever(),
    return_source_documents=True
)

# 検索関数の定義
def semantic_search(query):
    result = qa_chain({"query": query})
    return result["result"], result["source_documents"]

# ユーザーの質問と回答を保存するファイルパス
query_answer_path = "query_answers.jsonl"  # ファイルパスを定義

# ユーザーの質問と回答をファイルに保存する関数
def save_query_and_answer(query, answer):
    data = {"query": query, "answer": answer}
    with open(query_answer_path, 'a') as file:  # 'a' for append
        file.write(json.dumps(data) + "\n")  # JSONL形式で書き出し

def semantic_search(query):
    result = qa_chain({"query": query})
    return result["result"], result["source_documents"]

# ユーザーの質問を処理する関数
def handle_query(new_query):
    # 新しい質問をファイルに追加
    with open(query_answer_path, 'a') as file:
        file.write(json.dumps({"query": new_query}) + "\n")  # 新しい質問をファイルに書き込む

    # ファイルから過去の質問と回答を読み込む
    with open(query_answer_path, 'r') as file:
        content = file.read()

    # LLMには読み込んだ内容を入力
    answer, source_docs = semantic_search(content)

    # 結果と新しい質問をファイルに保存
    save_query_and_answer(new_query, answer)

    # 結果を表示
    print("回答:", answer)

# テスト
handle_query("複合機の価格を教えてください")
