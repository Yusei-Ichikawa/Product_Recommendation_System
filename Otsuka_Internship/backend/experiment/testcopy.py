import flask
from flask import request
from flask_cors import CORS
import pandas as pd
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
import os
import json
import Otsuka_Internship.backend.server.db as db
import time

debug = True

# エクセルファイルの読み込み
df = pd.read_excel('../LLM/dataset/latestdata/cleaned_data_latest.xlsx')

# Documentオブジェクトのリストを作成
documents = []
for _, row in df.iterrows():
    content = f"id: {row['id']}\n品名: {row['品名']}\n大カテゴリ: {row['大カテゴリ']}\n小カテゴリ: {row['小カテゴリ']}\n値段: {row['値段']}\n製品説明: {row['製品説明']}\n"
    doc = Document(page_content=content, metadata={"source": row['品名'], "id": row['id']})
    documents.append(doc)
os.environ["OPENAI_API_KEY"] = (
    ""
)
# エンベッディングの作成
embeddings = OpenAIEmbeddings()

# ベクトルストアの構成
vectorstore = FAISS.from_documents(documents, embeddings)

# 検索チェーンの作成
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4o-mini"),
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True,
)

query_answer_path = "query_answers.jsonl"

def save_query_and_answer(query, answer):
    timestamp = time.time()
    data = {"query": query, "answer": answer, "timestamp": timestamp}
    with open(query_answer_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")

def content_based_search(query):
    # DataFrameを使用して検索を行う
    content_results = df[df['製品説明'].str.contains(query, case=False) | df['品名'].str.contains(query, case=False)].head(5)

    # 結果をDocumentオブジェクトに変換
    documents = []
    for _, row in content_results.iterrows():
        content = f"id: {row['id']}\n品名: {row['品名']}\n大カテゴリ: {row['大カテゴリ']}\n小カテゴリ: {row['小カテゴリ']}\n値段: {row['値段']}\n製品説明: {row['製品説明']}\n"
        doc = Document(page_content=content, metadata={"source": row['品名'], "id": row['id']})
        documents.append(doc)

    return documents

def hybrid_search(query):
    # ベクトル検索
    vector_results = vectorstore.similarity_search(query, k=5)

    # 内容ベース検索
    content_results = content_based_search(query)

    # 結果の組み合わせと重複排除
    combined_results = list({doc.metadata['id']: doc for doc in vector_results + content_results}.values())

    # 関連性でソート（この例では単純化のため、ベクトル検索の順序を優先）
    sorted_results = sorted(combined_results, key=lambda x: vector_results.index(x) if x in vector_results else len(vector_results))

    return sorted_results[:5]  # 上位5件を返す

def semantic_search(query):
    # ハイブリッド検索を使用
    hybrid_results = hybrid_search(query)

    # QAチェーンを使用して回答を生成
    result = qa_chain({"query": query, "input_documents": hybrid_results})

    formatted_answer = result["result"]
    source_docs = result["source_documents"]

    # 上位5件の関連ドキュメントの情報を追加
    formatted_answer += "\n\n関連する複合機の情報:\n"
    for i, doc in enumerate(source_docs[:5], 1):
        formatted_answer += f"{i}. ID: {doc.metadata['id']}, 品名: {doc.metadata['source']}\n"

    return formatted_answer

app = flask.Flask(__name__)
CORS(app)

def save_query(user_id, chat_id, query):
    os.makedirs(f"test/{user_id}/{chat_id}", exist_ok=True)
    with open(f"test/{user_id}/{chat_id}/question.txt", "a") as file:
        file.write(query + "\n")

def save_answer(user_id, chat_id, answer):
    with open(f"test/{user_id}/{chat_id}/answer.txt", "a") as file:
        file.write(str(answer) + "\n")

@app.route('/chat', methods=['POST'])
def chat():
    if debug:
        print("chat() called")
    new_query = request.json.get("prompt")
    chat_id = request.json.get("chat_id")
    user_id = request.json.get("user_id")
    if debug:
        print("Prompt:", new_query)

    formatted_answer = semantic_search(new_query)
    if debug:
        print("Formatted Answer:", formatted_answer)

    save_query_and_answer(new_query, formatted_answer)
    if debug:
        print("Query and answer saved")
<<<<<<< HEAD:backend/testcopy.py

=======

    save_query(user_id, chat_id, new_query)
    save_answer(user_id, chat_id, formatted_answer)

>>>>>>> b72c89f ([add] curlを使わずにリクエストを送れるreq.pyを追加):backend/experiment/testcopy.py
    return formatted_answer

@app.route("/qa_history", methods=["POST"])
def qa_history():
    # リクエストデータを保存
    chat_id = request.json.get("chat_id")
    user_id = request.json.get("user_id")
    # TODO (chat_id,user_id)がチャットテーブルになかったらエラー
    # テーブルから取得
    before_qa_history = db.select_chat_by_id(chat_id)["qa_history"]
    print("履歴:", before_qa_history)
    return before_qa_history


@app.route("/chat_infos", methods=["POST"])
def chat_infos():
    user_id = request.json.get("user_id")
    chats = db.select_chats_by_user_id(user_id)
    return chats


@app.route("/is_valid_user", methods=["POST"])
def is_valid_user():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    user = db.select_user_by_id(user_id)
    if user["password"] == password:
        return user
    else:
        return {"name": None}


if __name__ == "__main__":
    app.debug = True
    app.run()
