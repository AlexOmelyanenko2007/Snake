import sqlite3

'''
Аннотация нашей таблицы
Table scores
| id | player_name | best_score |
'''


class ScoreTable:
    con = None
    cur = None

    def __init__(self):  # конструктор
        self.con = sqlite3.connect("snake.db")
        self.cur = self.con.cursor()

        # проверяем существование таблицы
        try:
            self.cur.execute("SELECT * FROM scores")
        except sqlite3.OperationalError:
            self.create_table()  # и если её нет, то создаем

    def create_table(self):
        self.cur.execute('''
            CREATE TABLE scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name VARCHAR DEFAULT 'ghost',
                best_score INTEGER DEFAULT '0'
            );
        ''')

    def get_scores(self):
        res = self.cur.execute("SELECT player_name, best_score FROM scores ORDER BY best_score DESC")
        return res.fetchall()

    def get_score_by_username(self, username):
        res = self.cur.execute(f"SELECT * FROM scores WHERE player_name = '{username}'")
        return res.fetchone()

    def set_score_by_username(self, username, score):
        user = self.get_score_by_username(username)

        if user is not None:
            if score > user[2]:
                self.cur.execute(f"UPDATE scores SET best_score = {score} WHERE player_name = '{username}'")
        else:
            self.cur.execute(f"INSERT INTO scores (id, player_name, best_score) VALUES (NULL, '{username}', {score})")

        self.con.commit()

