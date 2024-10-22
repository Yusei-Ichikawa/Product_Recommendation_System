import openai
from flask import request
from flask_cors import CORS
import pandas as pd
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai.chat_models import ChatOpenAI
from openai import OpenAI
import os
import json
import time
import Otsuka_Internship.backend.server.db as db
# ハイブリッド検索用
from rank_bm25 import BM25Okapi
from langchain.vectorstores import Chroma
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

def hybrid_search(query, documents, vectorstore):
    tokenized_query = query.lower().split(" ")

    bm25 = BM25Okapi([doc.page_content.split(" ") for doc in documents])
    keyword_scores = bm25.get_scores(tokenized_query)

    vector_results = vectorstore.search(query, top_k=10, search_type='similarity')

    # Assuming vector_results are dicts with 'id' and 'score'
    vector_scores_dict = {result['id']: result['score'] for result in vector_results}

    combined_scores = {}
    for idx, doc in enumerate(documents):
        doc_id = getattr(doc, 'id', None)
        vector_score = vector_scores_dict.get(doc_id, 0)
        combined_score = keyword_scores[idx] + vector_score
        combined_scores[doc_id] = combined_score

    sorted_docs = sorted(documents, key=lambda x: combined_scores[x.id], reverse=True)
    return sorted_docs[:5]

# 検索チェーンの作成
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4-turbo"),
    chain_type="refine",
    retriever=vectorstore.as_retriever(),
    return_source_documents=True,
)



# ユーザーの質問と回答を保存するファイルパス
query_answer_path = "testHibrid_query_answers.jsonl"  # ファイルパスを定義
# ユーザーの質問と回答をファイルに保存する関数
def save_query_and_answer(query, answer):
    data = {"query": query, "answer": answer}
    with open(query_answer_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")  # JSONL形式で書き出し


# 検索関数の定義
def semantic_search(query):
    result = qa_chain({"query": query})
    return result["result"], result["source_documents"]

def chat():
    # リクエストデータを取得

    new_query = "a"
    chat_id = "b"
    user_id = "c"

    if db.select_chat_by_id(chat_id) is None:
        db.add_to_chat_table(user_id, "")

    # chatテーブルの更新
    print("chat_id", chat_id)
    before_qa_history = db.select_chat_by_id(chat_id)["qa_history"]
    print("履歴:", before_qa_history)
    db.modify_chat_by_id(chat_id, {"qa_history":  before_qa_history + "{conversation:" +new_query + "}\n"})
    print("質問:", new_query)

    content = before_qa_history

    bot_config = """
    あなたは以下の条件に適する複合機を提案できる心優しい日本人です。
    # 条件
    """

    #返答形式の定義
    reply_format =  """
    # 返答形式
    4, 5個くらいの候補を出して
    """
    content = content + bot_config + new_query + reply_format  # 新しい質問を追加
    print(content)
    # LLMには読み込んだ内容を入力
    #answer, source_docs = semantic_search(content)

    # ハイブリッド検索
    combined_results = hybrid_search(new_query, documents, vectorstore)
    answer = combined_results
    print("回答:", answer)

    # gpt-4o-miniによって、answerをjsonに修正



    # 結果と新しい質問をファイルに保存
    #save_query_and_answer(new_query, answer)

    print("回答:", answer)
    # 応答を返す
    return answer

def qa_history():
    # リクエストデータを保存
    chat_id = request.json.get("chat_id")
    user_id = request.json.get("user_id")
    # TODO (chat_id,user_id)がチャットテーブルになかったらエラー
    # テーブルから取得
    before_qa_history = db.select_chat_by_id(chat_id)["qa_history"]
    print("履歴:", before_qa_history)
    return before_qa_history

    chat()
