
import re
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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from janome.tokenizer import Tokenizer
from rank_bm25 import BM25Okapi
import numpy as np
import faiss
import pickle

load_dotenv(dotenv_path=".env")
debug = True

# エクセルファイルの読み込み
df = pd.read_excel('./finalData_add_img_forBackend.xlsx')

#APIキーをprint
print(os.getenv("OPENAI_API_KEY"))

print(df)

# Documentオブジェクトのリストを作成
documents = []
for _, row in df.iterrows():
    content = f"id: {row['id']}\n品名: {row['品名']}\n大カテゴリ: {row['大カテゴリ']}\n小カテゴリ: {row['小カテゴリ']}\n値段: {row['値段']}\n製品説明: {row['製品説明']}\n"
    doc = Document(page_content=content, metadata={"source": row['品名'], "id": row['id']})
    documents.append(doc)


top_k = 10

# 初回のベクトルストア作成時

# ベクトルストアを保存する関数
def save_faiss_index(vectorstore, filename='faiss_index.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump(vectorstore, f)

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vectorstore = FAISS.from_documents(documents, embeddings)


# FAISSインデックスとベクトルストアを読み込む関数
def load_faiss_index(filename='faiss_index.pkl'):
    with open(filename, 'rb') as f:
        return pickle.load(f)

#loaded_vectorstore = load_faiss_index()



# 検索チェーンの作成
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4o-mini"),
    #chain_type="refine",
    retriever=vectorstore.as_retriever(search_kwargs={"k": top_k}),
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
        # Tokenizer のインスタンスを生成
        self.tokenizer = Tokenizer()

    def __call__(self, text):
        # text をトークナイズして表層形をリストとして返す
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
    top_docs = df.iloc[related_docs_indices[:top_k]]
    print("コサイン類似度に基づく上位5つのドキュメント：", top_docs['品名'].tolist())
    
    # 結果をDocumentオブジェクトに変換
    documents = []
    for _, row in top_docs.iterrows():
        content = f"id: {row['id']}\n品名: {row['品名']}\n大カテゴリ: {row['大カテゴリ']}\n小カテゴリ: {row['小カテゴリ']}\n値段: {row['値段']}\n製品説明: {row['製品説明']}\n"
        doc = Document(page_content=content, metadata={"source": row['品名'], "id": row['id']})
        documents.append(doc)
    
    return documents

class BM25Tokenizer:
    def __init__(self):
        # JanomeTokenizer のインスタンスを生成
        self.tokenizer = JanomeTokenizer()

    def __call__(self, text):
        # text をトークナイズしてトークンのリストを返す
        return self.tokenizer(text)


# bm25を用いたキーワード検索
def keyword_search(query):
    print("キーワード検索を開始します。")
    tokenizer = BM25Tokenizer()
    tokenized_corpus = [tokenizer(doc) for doc in df['製品説明'].tolist()]
    
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = tokenizer(query)
    doc_scores = bm25.get_scores(tokenized_query)
    
    top_docs_indices = doc_scores.argsort()[::-1]
    top_docs = df.iloc[top_docs_indices[:top_k]]
    
    documents = []
    for index, score in zip(top_docs_indices[:top_k], sorted(doc_scores, reverse=True)):
        row = df.iloc[index]
        content = f"id: {row['id']}\n品名: {row['品名']}\n大カテゴリ: {row['大カテゴリ']}\n小カテゴリ: {row['小カテゴリ']}\n値段: {row['値段']}\n製品説明: {row['製品説明']}\n"
        doc = Document(page_content=content, metadata={"source": row['品名'], "id": row['id'], "score": score})
        documents.append(doc)
    
    print("キーワード検索が完了しました：", [doc.metadata['source'] for doc in documents])
    return documents

def normalize_scores(scores):
    if not scores: 
        return []
    min_score = min(scores)
    max_score = max(scores)
    if max_score == min_score:
        return [1] * len(scores) 
    return [(score - min_score) / (max_score - min_score) for score in scores]

def sigmoid_normalization(scores):
    scores = np.array(scores)
    mean = np.mean(scores)
    std = np.std(scores)
    if std == 0:
        return np.ones_like(scores) * 0.5 
    z_scores = (scores - mean) / std
    sigmoid_scores = 1 / (1 + np.exp(-z_scores))
    return sigmoid_scores

def hybrid_search(query, new_query):
    print("Initiating hybrid search.")
    vector_results = []
    keyword_results = []
    vector_scores = []

    try:
        vector_results = vectorstore.similarity_search_with_score(query, k=top_k)
        print("Vector search results:", [doc[0].metadata['id'] for doc in vector_results])
        vector_scores = [score for _, score in vector_results]
        vector_results = [doc for doc, _ in vector_results]
    except Exception as e:
        print(f"Vector search failed: {e}")

    try:
        keyword_results = keyword_search(new_query)
        keyword_scores = [doc.metadata['score'] for doc in keyword_results]
        print("Keyword search results:", [doc.metadata['id'] for doc in keyword_results])
    except Exception as e:
        print(f"Keyword search failed: {e}")


    print(f"before normalize vector_scores: {vector_scores}")
    print(f"before normalize keyword_scores: {keyword_scores}")
    vector_scores = sigmoid_normalization(vector_scores)
    keyword_scores = sigmoid_normalization(keyword_scores)

    print(f"vector_scores: {vector_scores}")
    print(f"keyword_scores: {keyword_scores}")
    score_map = {}
    weight_vector = 0.7
    weight_keyword = 0.3

    for doc, score in zip(vector_results, vector_scores):
        score_map[doc.metadata['id']] = score * weight_vector

    for doc, score in zip(keyword_results, keyword_scores):
        if doc.metadata['id'] in score_map:
            score_map[doc.metadata['id']] += score * weight_keyword
        else:
            score_map[doc.metadata['id']] = score * weight_keyword

    sorted_docs = sorted(score_map.items(), key=lambda item: item[1], reverse=True)
    sorted_documents = [doc for doc_id, _ in sorted_docs[:top_k] for doc in (vector_results + keyword_results) if doc.metadata['id'] == doc_id]

    print("Combined sorted results:", [doc.metadata['id'] for doc in sorted_documents])
    return sorted_documents


def search(query, new_query):
    # ハイブリッド検索を使用
    hybrid_results = hybrid_search(query, new_query)
    
    # QAチェーンを使用して回答を生成
    result = qa_chain({"query": query, "input_documents": hybrid_results})
    
    formatted_answer = result["result"]
    source_docs = result["source_documents"]
    
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
        try:
            # DataFrameから製品情報を取得
            product_info = df.loc[df['id'] == id].iloc[0]
        except IndexError:
            # 該当するIDがない場合
            continue

        if product_info.empty:
            continue

        price = int(product_info['値段']) if pd.notna(product_info['値段']) else None

        recommends.append({
            "reason": reasons[i],
            "products": [{
                "id": id,
                "name": product_info['品名'],
                "price": price,
                "imageEncoding": product_info['画像'],
            }]
        })
    
    response_data = {
        "recommends": recommends,
        "text": ""
    }

    # JSON文字列に変換して返す
    # json_string = json.dumps(response_data, ensure_ascii=False)
    return response_data

def situation(query):
    # chatGPTにquery(状況)から、どのような複合機が適しているか特徴を考えてもらう
    # その特徴を返してもらう

    # 例
    # query: "中学校で使用するために、教育用資料や試験の印刷に対応できる低コストで効率的な複合機を探しています。使いやすさと安全性が重要です。"
    prompt = f"""
    以下の状況において必要とされている適切な製品(複合機・ノートパソコン・デスクトップPC・タブレット・周辺機器・ソフトウェア)の特徴を箇条書きで5つ挙げてください。
    状況を踏まえて、必要な製品はいくらでも追加して構いません。
    状況: {query}

    回答は以下の形式で箇条書きにしてください。状況を踏まえて必要十分な数だけ製品を追加してよいです。：


    ### 複合機・ノートパソコン・デスクトップPC・タブレット・ソフトが必要と判断された場合
    - 製品の特徴1: [なんの製品か(複合機・ノートパソコン(Mac/Windows)・デスクトップPC(Mac/Windows)・タブレット(iPad/その他)・ソフトウェア)を明記]
    - 製品の特徴2: [どの程度のスペック・あるいは機能が必要か]
    - 製品の特徴3: [その他あるべき特徴の説明]
    - 製品の特徴4: [その他あるべき特徴の説明]
    - 製品の特徴5: [オプションがあればどのようなオプションを付けるべきか]

    """
    response = ChatOpenAI(model="gpt-4o-mini").predict(prompt)
    return response



@app.route('/chat', methods=['POST'])
def chat():
    if debug:
        print("chat() called")
    new_query = request.json.get("prompt")
    chat_id = request.json.get("chat_id")
    user_id = request.json.get("user_id")
    content = "これは今までの質問履歴です。\n"
    
    chat = db.select_chat_by_id(chat_id)
    if chat is not None:
        content = chat["qa_history"]
    
    prompt = """
        ユーザーが現在の状況で求めている製品(複合機・ノートパソコン・デスクトップ・タブレット・周辺機器・ソフト)に基づいて、その製品の適合性を評価し、適切な理由とともに製品をセットで推薦してください。
       ただし、 ユーザーが特定の製品に言及している場合、その製品の種類に限定して回答を行ってください。
        そうでない場合、状況を踏まえて適切な製品のセットを推薦してください。
    """

    

    content = content + prompt + "\n"
    content = content + new_query + "\n"
    features = situation(new_query)

    content = content + "この情報も参考にしてください。\n" +  features + "\n"

    format_prompt = """
        # 返答形式
        
        id: 製品のID
        reason: 製品セットにおいて、その製品(複合機・ノートパソコン・デスクトップ・タブレット)が適している理由
        
        製品セットに含まれる製品の数だけ出力してください。出力するのは、IDとそれが適している理由のみで良いです。
    """
    
    content += format_prompt + "\n"
    print("Content:", content)
    formatted_answer = search(content, new_query)
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

    isJson = False

    if len(ids) > 0:
        return_answer = json_response(ids, reasons)
        isJson = True



    save_query(user_id, chat_id, new_query)
    save_answer(user_id, chat_id, return_answer)
    save_prompt(user_id, chat_id, prompt + format_prompt)

    if debug:
        print("Chat completed")
        print(return_answer)

    # isJsonがTrueの時return_answerは辞書型, Falseの時は文字列
    return {"answer": return_answer, "isJson": isJson}

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
            for id in ids:
                row = df_index.loc[id]
                products.append(
                    {
                        "id": id,
                        "name": row["品名"],
                        "price": str(row["値段"]),
                        "url": "",
                        "imageEncoding": row["画像"],
                    }
                )
            recommends.append({"reason": reason, "products": products})
        ret.append({"question": q, "answer": {"recommends": recommends}})
    print(ret)
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
    if user != None and user["password"] == password:
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