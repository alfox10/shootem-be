from flask import Flask
from threading import Thread
from flask import jsonify, request, Response
import sqlite3
from sqlite3 import Error
from requests.structures import CaseInsensitiveDict

app = Flask('')

conn = None
database = r"leaderboard.db"


def create_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    global conn
    global database
    conn = None
    try:
        conn = sqlite3.connect(database, check_same_thread=False)
        return conn
    except Error as e:
        print(e)


def return_best_player():
    global conn
    if conn is None:
        create_connection()
    cur = conn.cursor()
    cur.execute("SELECT name,score FROM player order by score DESC  LIMIT 10")
    return cur.fetchall()


def insert_score(name, score):
    global conn
    if conn is None:
        create_connection()
    cur = conn.cursor()
    data_tuple = (name, score)
    try:
        cur.execute("INSERT INTO PLAYER(name,score) VALUES(?,?)", data_tuple)
        conn.commit()
        cur.close()
    except Error as e:
        print("error inseting "+name+" "+score)


@app.route('/')
def home():
    return '''<p><h1>ShootEM API homepage</h1></p><p><h3>Page not really usefull</h3></p>'''


@app.route('/api/v1/player', methods=['GET'])
def set_new_score():
    data = request.args
    insert_score(data['name'], data['score'])
    return jsonify(data)


@app.route('/api/v1/leaderboard', methods=['GET'])
def get_lb():
    result = []
    data = return_best_player()
    i = 1
    for player, score in data:
        temp_lb = {}
        temp_lb['name'] = player
        temp_lb['score'] = score
        temp_lb['position'] = i
        result.append(temp_lb)
        i += 1
    resget = {'data':result}
    response = jsonify(resget)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


if __name__ == '__main__':
    print("Starting Web Server")
    keep_alive()
