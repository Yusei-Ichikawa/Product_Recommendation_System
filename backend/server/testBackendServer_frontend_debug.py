import flask
from flask import request
from flask_cors import CORS
import pandas as pd
import os
import json
import db
import time
from dotenv import load_dotenv
from flask import jsonify
from flask import Response

load_dotenv(dotenv_path=".env")
debug = True

# エクセルファイルの読み込み
df = pd.read_excel('../../LLM/dataset/00_latestData/cleaned_data_latest.xlsx')


query_answer_path = "query_answers.jsonl"


def save_query_and_answer(query, answer):
    timestamp = time.time()
    data = {"query": query, "answer": answer, "timestamp": timestamp}
    with open(query_answer_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")


app = flask.Flask(__name__)
CORS(app)


def json_response(ids, reasons):
    recommends = []
    for i, id in enumerate(ids):
        product_info = db.get_product_information_by_id(id)
        if product_info:
            recommends.append(
                {
                    "reason": reasons[i],
                    "products": [
                        {
                            "id": id,
                            "name": product_info["product"],
                            "price": product_info["price"],
                            "imageEncoding": product_info["image"],
                        }
                    ],
                }
            )

    response_data = {"recommends": recommends, "text": ""}

    # JSON文字列に変換して直接返す
    json_string = json.dumps(response_data, ensure_ascii=False)
    return json_string


@app.route("/chat", methods=["POST"])
def chat():
    if debug:
        print("chat() called")
    new_query = request.json.get("prompt")
    chat_id = request.json.get("chat_id")
    user_id = request.json.get("user_id")

    chat = db.select_chat_by_id(chat_id)
    if chat is not None:
        content = chat["qa_history"]
    return {
        "recommends": [
            {
                "reason": "理由",
                "products": {
                    "id": "id",
                    "name": "name",
                    "price": "123円",
                    "url": "",
                    "imageEncoding": "",
                },
            }
        ]
    }


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
    db.modify_chat_by_id(chat_id, {"qa_history": new_qa_history})
    print(new_qa_history)
    return {"chat_id": chat_id}


if __name__ == "__main__":
    app.debug = True
    app.run()
