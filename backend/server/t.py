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
import db
import time
from dotenv import load_dotenv
from flask import jsonify
from flask import Response
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from janome.tokenizer import Tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer

load_dotenv(dotenv_path=".env")
debug = True

# エクセルファイルの読み込み
df = pd.read_excel('../../LLM/dataset/00_latestData/cleaned_data_latest.xlsx')

# Documentオブジェクトのリストを作成
documents = []
for _, row in df.iterrows():
    content = f"id: {row['id']}\n品名: {row['品名']}\n大カテゴリ: {row['大カテゴリ']}\n小カテゴリ: {row['小カテゴリ']}\n値段: {row['値段']}\n製品説明: {row['製品説明']}\n"
    doc = Document(page_content=content, metadata={"source": row['品名'], "id": row['id']})
    documents.append(doc)



# エンベッディングの作成
embeddings = OpenAIEmbeddings()

# ベクトルストアの構成
vectorstore = FAISS.from_documents(documents, embeddings)

# 検索チェーンの作成
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4o-mini"),
    chain_type="refine",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True,
)

query_answer_path = "query_answers.jsonl"

def save_query_and_answer(query, answer):
    timestamp = time.time()
    data = {"query": query, "answer": answer, "timestamp": timestamp}
    with open(query_answer_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")

class JanomeTokenizer:
    def __init__(self):
        self.tokenizer = Tokenizer()

    def __call__(self, text):
        return [token.surface for token in self.tokenizer.tokenize(text)]


# TF-IDFベクトル化器を日本語対応で初期化
vectorizer = TfidfVectorizer(tokenizer=JanomeTokenizer(), lowercase=False)


def content_based_search(query):
    print("コンテンツベース検索を開始します。")
    # DataFrame全体でTF-IDFを計算
    tfidf_matrix = vectorizer.fit_transform(df['製品説明'])
    print("TF-IDF行列が計算されました。")

    # クエリのTF-IDFベクトルを生成
    query_vector = vectorizer.transform([query])
    
    # コサイン類似度で検索
    cosine_similarities = linear_kernel(query_vector, tfidf_matrix).flatten()
    print("コサイン類似度が計算されました：", cosine_similarities)

    # 類似度が高い順にインデックスを取得
    related_docs_indices = cosine_similarities.argsort()[::-1]
    
    # 最も類似度が高い上位5件のドキュメントを取得
    top_docs = df.iloc[related_docs_indices[:5]]
    print("コサイン類似度に基づく上位5つのドキュメント：", top_docs['品名'].tolist())
    
    # 結果をDocumentオブジェクトに変換
    documents = []
    for _, row in top_docs.iterrows():
        content = f"id: {row['id']}\n品名: {row['品名']}\n大カテゴリ: {row['大カテゴリ']}\n小カテゴリ: {row['小カテゴリ']}\n値段: {row['値段']}\n製品説明: {row['製品説明']}\n"
        doc = Document(page_content=content, metadata={"source": row['品名'], "id": row['id']})
        documents.append(doc)
    
    return documents



def hybrid_search(query):
    print("Initiating hybrid search.")
    try:
        # ベクトル検索
        vector_results = vectorstore.similarity_search(query, k=5)
        print("Vector search results:", vector_results)
    except Exception as e:
        print(f"Vector search failed: {e}")
        vector_results = []

    try:
        # 内容ベース検索
        content_results = content_based_search(query)
        print("Content search results:", [doc.metadata['id'] for doc in content_results])
    except Exception as e:
        print(f"Content search failed: {e}")
        content_results = []

    # 結果の組み合わせと重複排除
    id_to_doc = {doc.metadata['id']: doc for doc in vector_results + content_results}
    combined_results = list(id_to_doc.values())
    
    # 関連性でソート（この例では単純化のため、ベクトル検索の順序を優先）
    sorted_results = sorted(combined_results, key=lambda x: (vector_results.index(x) if x in vector_results else float('inf')))
    print("Combined sorted results:", [doc.metadata['id'] for doc in sorted_results])
    
    return sorted_results[:5]  # 上位5件を返す

def search(query):
    # ハイブリッド検索を使用
    hybrid_results = hybrid_search(query)
    
    # QAチェーンを使用して回答を生成
    result = qa_chain({"query": query, "input_documents": hybrid_results})
    
    formatted_answer = result["result"]
    source_docs = result["source_documents"]
    
    # 上位5件の関連ドキュメントの情報を追加
    #formatted_answer += "\n\n関連する複合機の情報:\n"
    #for i, doc in enumerate(source_docs[:5], 1):
    #    formatted_answer += f"{i}. ID: {doc.metadata['id']}, 品名: {doc.metadata['source']}\n"
    
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
        
        
def save_prompt(user_id, chat_id, prompt):
    with open(f"test/{user_id}/{chat_id}/prompt.txt", "a") as file:
        file.write(prompt + "\n")

# 

def json_response(ids, reasons):
    recommends = []
    for i, id in enumerate(ids):
        product_info = db.get_product_information_by_id(id)
        if product_info:
            recommends.append({
                "reason": reasons[i],
                "products": [{
                    "id": id,
                    "name": product_info['product'],
                    "price": product_info['price'],
                    "imageEncoding": product_info['image']
                }]
            })
    
    response_data = {
        "recommends": recommends,
        "text": ""
    }

    # JSON文字列に変換して直接返す
    json_string = json.dumps(response_data, ensure_ascii=False)
    return json_string

@app.route('/chat', methods=['POST'])
def chat():
    if debug:
        print("chat() called")
    new_query = request.json.get("prompt")
    chat_id = request.json.get("chat_id")
    user_id = request.json.get("user_id")
    content = "これは今までの質問履歴です。"
    
    chat = db.select_chat_by_id(chat_id)
    if chat is not None:
        content = chat["qa_history"]
    
    prompt = """
        このあと状況が与えられます。その状況に適する複合機を理由とともに教えてください。
        
        # 状況
        
    """

    format_prompt = """
        # 返答形式
        id: 複合機のID
        reason: その複合機が適している理由
        
        最大で3~5つまで教えて下さい。出力するのは、IDと理由のみよいです。
    """
    content = content + prompt
        
    content += new_query   
    
    content += format_prompt
    print("Content:", content)
    formatted_answer = search(content)
    if debug:
        print("Formatted Answer:", formatted_answer)
    
    save_query_and_answer(content, formatted_answer)
    if debug:
        print("Query and answer saved")
    
    
    # formatter_answerから、idとreasonを取り出して、存在する場合はjsonで返す。
    # ない場合はそのまま返す
    return_answer = formatted_answer
    ids, reasons = [], []
    for line in formatted_answer.split("\n"):
        if "id:" in line:
            ids.append(line.split("id:")[1].strip())
        if "reason:" in line:
            reasons.append(line.split("reason:")[1].strip())

    if len(ids) > 0:
        return_answer = json_response(ids, reasons)


    save_query(user_id, chat_id, new_query)
    save_answer(user_id, chat_id, return_answer)
    save_prompt(user_id, chat_id, prompt + format_prompt)
    
    return return_answer

@app.route("/qa_history", methods=["POST"])
def qa_history():
    print("/qa_history", request.json)
    chat_id = request.json.get("chat_id")
    user_id = request.json.get("user_id")
    # dfのindexを設定
    df_index = df.set_index("id")
    # TODO (chat_id,user_id)がチャットテーブルになかったらエラー
    # テーブルから取得
    before_qa_history = db.select_chat_by_id(chat_id)["qa_history"]
    try:
        qa_history_list = json.loads(before_qa_history)
    except json.decoder.JSONDecodeError as e:
        qa_history_list = []
        print(f"過去履歴の形式がおかしいため、[]で代用")
    print(qa_history_list)
    ret = []
    for qa in qa_history_list:
        a = qa["answer"]
        q = qa["question"]
        recommends = []
        if a == None:
            continue
        for recommend in a["recommends"]:
            reason = recommend["reason"]
            ids = recommend["ids"]
            # TODO データベースを使うようにする？？
            products = []
            for _ in ids:
                id = df_index.index[0]
                row = df_index.loc[id]
                products.append(
                    {
                        id: id,
                        "name": row["品名"],
                        "price": str(row["値段"]),
                        "url": "",
                        "imageEncoding": row["画像"],
                    }
                )
            recommends.append({"reason": reason, "products": products})
        ret.append({"question": q, "answer": {"recommends": recommends}})
    return ret


@app.route("/chat_infos", methods=["POST"])
def chat_infos():
    print("/chat_infos", request.json)
    user_id = request.json.get("user_id")
    chats = db.select_chats_by_user_id(user_id)
    return chats


@app.route("/is_valid_user", methods=["POST"])
def is_valid_user():
    print("/is_valid_user", request.json)
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    user = db.select_user_by_id(user_id)
    if user["password"] == password:
        return user
    else:
        return {"name": None}


@app.route("/new_chat", methods=["POST"])
def new_chat():
    print("/new_chat", request.json)
    user_id = request.json.get("user_id")
    new_chat_id = db.add_to_chat_table(user_id, "")
    return {"chat_id": new_chat_id}


@app.route("/update_chat_title", methods=["POST"])
def update_chat_title():
    print("/update_chat_title", request.json)
    chat_id = request.json.get("chat_id")
    title = request.json.get("title")
    db.modify_chat_by_id(chat_id, {"title": title})
    return {"chat_id": chat_id, "title": title}


@app.route("/add_qa_history", methods=["POST"])
def add_qa_history():
    print("/add_qa_history", request.json)
    user_id = request.json.get("user_id")
    chat_id = request.json.get("chat_id")
    question = request.json.get("question")
    answer = request.json.get("answer")
    before_qa_history = db.select_chat_by_id(chat_id)["qa_history"]
    new_qa_history = db.add_qa_to_history(before_qa_history, question, answer)
    db.modify_chat_by_id(chat_id, {"qa_history":new_qa_history})
    print(new_qa_history)
    return {"chat_id": chat_id}
    

if __name__ == "__main__":
    app.debug = True
    app.run()