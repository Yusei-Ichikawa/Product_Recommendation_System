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
    llm=ChatOpenAI(model="gpt-4-turbo"),
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True,
)

query_answer_path = "query_answers.jsonl"

def save_query_and_answer(query, answer):
    data = {"query": query, "answer": answer}
    with open(query_answer_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")

def semantic_search(query):
    result = qa_chain({"query": query})

    formatted_answer = result["result"]
    source_docs = result["source_documents"]

    # 上位5件の関連ドキュメントの情報を追加
    formatted_answer += "\n\n関連する複合機の情報:\n"
    for i, doc in enumerate(source_docs[:5], 1):
        formatted_answer += f"{i}. ID: {doc.metadata['id']}, 品名: {doc.metadata['source']}\n"

    return formatted_answer

app = flask.Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    if debug:
        print("chat() called")
    new_query = request.json.get("prompt")
    if debug:
        print("Prompt:", new_query)

    formatted_answer = semantic_search(new_query)
    if debug:
        print("Formatted Answer:", formatted_answer)

    save_query_and_answer(new_query, formatted_answer)
    if debug:
        print("Query and answer saved")

    return formatted_answer

@app.route("/qa_history", methods=["POST"])
def qa_history():
    chat_id = request.json.get("chat_id")
    user_id = request.json.get("user_id")
    before_qa_history = db.select_chat_by_id(chat_id)["qa_history"]
    print("履歴:", before_qa_history)
    return before_qa_history

if __name__ == "__main__":
    app.debug = True
    app.run()
