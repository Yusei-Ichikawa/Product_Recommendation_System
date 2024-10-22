import flask
import openai
from flask import request
from flask_cors import CORS
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
    llm=ChatOpenAI(model="gpt-4o"),
    chain_type="refine",
    retriever=vectorstore.as_retriever(),
    return_source_documents=True,
)

# ユーザーの質問と回答を保存するファイルパス
query_answer_path = "query_answers.jsonl"  # ファイルパスを定義


# ユーザーの質問と回答をファイルに保存する関数
def save_query_and_answer(query, answer):
    data = {"query": query, "answer": answer}
    with open(query_answer_path, "a", encoding="utf-8") as file:  # 'a' for append
        file.write(json.dumps(data, ensure_ascii=False) + "\n")  # JSONL形式で書き出し


# 検索関数の定義
def semantic_search(query):
    result = qa_chain({"query": query})
    return result["result"], result["source_documents"]


app = flask.Flask(__name__)
CORS(app)



@app.route('/chat', methods=['POST'])
def chat():
    # リクエストデータを取得

    new_query = request.json.get("prompt")
    chat_id = request.json.get("chat_id")
    user_id = request.json.get("user_id")

    if db.select_chat_by_id(chat_id) is None:
        db.add_to_chat_table(user_id, "")

    # chatテーブルの更新
    print("chat_id", chat_id)
    before_qa_history = db.select_chat_by_id(chat_id)["qa_history"]
    print("履歴:", before_qa_history)
    db.modify_chat_by_id(chat_id, {"qa_history": "{conversation:" + before_qa_history + new_query + "}\n"})
    print("質問:", new_query)

#<<<<<<< HEAD
    #with open(query_answer_path, "r", encoding="utf-8") as file:
    #    content = file.read()

    # chat_idから過去の質問と回答を取得
    content = before_qa_history

    #
#=======
#     with open(query_answer_path, "r", encoding="utf-8") as file:
#         content = file.read()
#     #
# >>>>>>> 3467d63 (add testprompt.txt file)

    bot_config = """
    あなたは以下の条件に適する複合機を提案できる心優しい日本人です。
    # 条件
    """

    #返答形式の定義
    reply_format =  """
    # 返答形式
    4, 5個くらいの候補を出してほしいが、適するものがない場合はそれより少なくなっても良い。
    以下の形式で列挙して。
    ・id: ここにidを書いて
    ・その複合機を提案する理由: 理由

    上の形式の物以外の文字列は出力しないで
    """
    content = content + bot_config + new_query + reply_format  # 新しい質問を追加
    print(content)
    # LLMには読み込んだ内容を入力
    answer, source_docs = semantic_search(content)

    # 結果と新しい質問をファイルに保存
    #save_query_and_answer(new_query, answer)

    print("回答:", answer)
    # 応答を返す
    return answer


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


if __name__ == "__main__":
    app.debug = True
    app.run()

### TODO sd
# 1. 登録・ログイン機能の実装
# 2. ユーザーの質問と回答をデータベースに保存
# 3. ユーザーの質問と回答をデータベースから取得
####
#### curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d '{"prompt": "大量のカラープリントに対応できる複合機のおすすめを教えてください。", "chat_id": "3"}'

####
