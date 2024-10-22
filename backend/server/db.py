import psycopg2
import os
import sys
from dotenv import load_dotenv
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import json



load_dotenv(dotenv_path=".env")
_db_url = os.getenv("DATABASE_URL")
assert _db_url != None

_TABLE_USER = "otsuka_user"
_TABLE_CHAT = "otsuka_chat"
_TABLE_PRODUCT = "product_table"
_USER_COLS = ["user_id", "name", "mail", "password"]
_CHAT_COLS = ["chat_id", "user_id", "qa_history", "title"]
_PRODUCT_COLS = ["product_id", "product", "parent_category", 
                "child_category", "price", "description", "image"]



def create_product_table():
    with psycopg2.connect(_db_url) as conn:
        cursor = conn.cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS "product_table" (
            id VARCHAR(5) NOT NULL,
            product VARCHAR(100),
            parent_category VARCHAR(100),
            child_category VARCHAR(100),
            price VARCHAR(100),
            description TEXT,
            image TEXT,
            CONSTRAINT product_table_pkey PRIMARY KEY (id)
        );
        """
        cursor.execute(sql)

# テーブルの作成
def create_tables():
    with psycopg2.connect(_db_url) as conn:
        cursor = conn.cursor()
        ## ユーザー情報
        sql = f"""
              CREATE TABLE IF NOT EXISTS "{_TABLE_USER}"(
                user_id  Serial Not NULL,
                name     VARCHAR (250),
                mail     VARCHAR (100),
                password VARCHAR (100),
                CONSTRAINT {_TABLE_USER}_pkey PRIMARY KEY (user_id)
              );
              """
        cursor.execute(sql)
        ## 質問履歴
        sql = f"""
              CREATE TABLE IF NOT EXISTS "{_TABLE_CHAT}"(
                chat_id     Serial Not NULL,
                user_id     integer,
                qa_history  VARCHAR (10000),
                title       VARCHAT (100),
                CONSTRAINT {_TABLE_CHAT}_pkey PRIMARY KEY (chat_id)
              );
              """
        cursor.execute(sql)

# qa_historyの追加
def add_qa_to_history(history, question, answer):
    """
    history: json形式の文字列
    question: 文字列(質問)
    answer: {"reason": string, "ids": int[]}[](答え)
    """
    try:
        history = json.loads(history)
    except json.decoder.JSONDecodeError as e:
        print(f"{history}はjson形式でない ({e})")
        history = []
    # 追加して文字列にする
    try:
        history.append({'question':question, 'answer':answer})
        return json.dumps(history)
    except json.decoder.JSONDecodeError as e:
        print(f"{history}はjson形式でない ({e})")
        return json.dumps([])
    


# ユーザーの作成
def add_to_user_table(name, mail, password):
    with psycopg2.connect(_db_url) as conn:
        cursor = conn.cursor()
        sql = f"""
              INSERT INTO {_TABLE_USER}(name, mail, password) VALUES('{name}', '{mail}', '{password}') RETURNING user_id;;
              """
        cursor.execute(sql)
        user_id = cursor.fetchone()[0]
        add_to_chat_table(user_id, "")
        # 新しく作成したuser_idを返す
        return user_id


# ユーザーの抽出
def select_user_by_id(user_id):
    with psycopg2.connect(_db_url) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {_TABLE_USER} where user_id = {user_id}")
        rows = cursor.fetchall()
        assert len(rows) <= 1
        if len(rows) == 0:
            return None
        elif len(rows) == 1:
            r = rows[0]
            return {x: r[i] for (i, x) in enumerate(_USER_COLS)}
        else:
            print("おかしい")
            return None


# ユーザー情報の変更
def modify_user_by_id(user_id, dictionary: dict):
    for k in dictionary:
        assert k in _USER_COLS and k != "user_id"
    with psycopg2.connect(_db_url) as conn:
        cursor = conn.cursor()
        for k in dictionary:
            # TODO 文字列でない場合、引用符はどうするか
            set_list = [f"{k} = '{dictionary[k]}'"]
            sql = f"""
                    UPDATE {_TABLE_USER}
                    SET {", ".join(set_list)}
                    WHERE user_id = {user_id}
                    """
            cursor.execute(sql)


# チャットの追加
def add_to_chat_table(user_id, qa_history):
    with psycopg2.connect(_db_url) as conn:
        cursor = conn.cursor()
        sql = f"""
              INSERT INTO {_TABLE_CHAT}(user_id, qa_history) VALUES({user_id}, '{qa_history}') RETURNING chat_id;
              """
        cursor.execute(sql)
        # 新しく作成したchat_idを返す
        return cursor.fetchone()[0]


# チャットの抽出
def select_chat_by_id(chat_id):
    with psycopg2.connect(_db_url) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {_TABLE_CHAT} where chat_id = {chat_id}")
        rows = cursor.fetchall()
        assert len(rows) <= 1
        if len(rows) == 0:
            return None
        elif len(rows) == 1:
            r = rows[0]
            return {x: r[i] for (i, x) in enumerate(_CHAT_COLS)}
        else:
            print("おかしい")
            return None


# チャット情報のユーザーIDによる抽出
def select_chats_by_user_id(user_id):
    with psycopg2.connect(_db_url) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {_TABLE_CHAT} where user_id = {user_id}")
        rows = cursor.fetchall()
        return [{x: r[i] for (i, x) in enumerate(_CHAT_COLS)} for r in rows]


# チャット情報の変更
def modify_chat_by_id(chat_id, dictionary: dict):
    for k in dictionary:
        assert k in _CHAT_COLS and k != "chat_id" and k != "user_id"
    with psycopg2.connect(_db_url) as conn:
        cursor = conn.cursor()
        for k in dictionary:
            # TODO 文字列でない場合、引用符はどうするか
            set_list = [f"{k} = '{dictionary[k]}'"]
            sql = f"""
                    UPDATE {_TABLE_CHAT}
                    SET {", ".join(set_list)}
                    WHERE chat_id = {chat_id}
                    """
            cursor.execute(sql)

# idから製品情報を取得
def get_product_information_by_id(product_id):
    with psycopg2.connect(_db_url) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM \"{_TABLE_PRODUCT}\" WHERE id = %s", (product_id,))
        rows = cursor.fetchall()
        if not rows:
            return None  # 製品が見つからなかった場合
        else:
            # 製品情報を返す
            return {x: rows[0][i] for i, x in enumerate(_PRODUCT_COLS)}

#  製品情報を取得
def get_products():
    with psycopg2.connect(_db_url) as conn:
        sql = "SELECT * FROM product_table"
        df = pd.read_sql_query(sql, conn)
    return df


def get_table_schema(table_name):
    with psycopg2.connect(_db_url) as conn:
        cursor = conn.cursor()
        query = """
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = %s;
        """
        cursor.execute(query, (table_name,))
        rows = cursor.fetchall()
        return rows

def main():
    
    # テーブルの名前と列名を表示
    print(get_table_schema(_TABLE_USER))
    print(get_table_schema(_TABLE_CHAT))
    print(get_table_schema(_TABLE_PRODUCT))
    
    print(get_product_information_by_id("FC011"))
    
    # 各テーブルの全行を表示
    with psycopg2.connect(_db_url) as conn:
        cursor = conn.cursor()
        tables = [_TABLE_USER, _TABLE_CHAT, _TABLE_PRODUCT]
        columns = [_USER_COLS, _CHAT_COLS, _PRODUCT_COLS]
        for i in range(len(tables)):
            # 各テーブルの定義を表示, できなかったので保留
            # cursor.execute(f"\d {table_name};")

            print(f"{tables[i]}:")
            print(columns[i])
            cursor.execute(f"Select * From {tables[i]};")
            rows = cursor.fetchall()
            for row in rows:
                print(row)



if __name__ == "__main__":
    if len(sys.argv) == 1:
        # add_to_user_table("testuser", "testuser@timekeepers.com", "testuser")
        # print(select_user_by_id(1))
        # add_to_chat_table(1, "{}")
        # print(select_chat_by_id(1))
        # modify_chat_by_id(2, {"qa_history": "aa"})
        main()
    elif sys.argv[1] == "create_tables":
        create_tables()
    else:
        print("引数が正しくない")
