import sqlite3
from kolory import bcolors

file = 'DB/chat.db'

class SQLite():
    def __init__(self, file):
        self.file = file
    def __enter__(self):
        self.conn = sqlite3.connect(self.file) 
        return self.conn.cursor()
    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

def setup():
    #conn = sqlite3.connect('DB/chat.db')
    #cur = conn.cursor()
    print(f'{bcolors.PUPRPLE}{bcolors.BOLD}Tworzenie bazy danych{bcolors.ENDC}')
    
    with SQLite(file=file) as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            login text NOT NULL,
            password text NOT NULL,
            mail text,
            status text
        );
        """)
        print(f'{bcolors.OKGREEN}Tabela "users" utworzona')
        
        cur.execute("""CREATE TABLE IF NOT EXISTS converstaions (
            id inTEGER PRIMARY KEY,
            date_created text NOT NULL,
            date_last_activity text NOT NULL,
            user_one text,
            user_two TEXT,
            FOREIGN KEY (user_one) REFERENCES users (id),
            FOREIGN KEY (user_two) REFERENCES users (id)
        );
        """)
        print(f'Tabela "conversations" utworzona')
        
        cur.execute("""CREATE TABLE IF NOT EXISTS messages (
            id integer PRIMARY KEY,
            date_sent text NOT NULL,
            sender_id TEXT,
            conversation_id text,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (conversation_id) REFERENCES conversaions (id)
        );
        """)
        print(f'Tabela "messages" utworzona')
        print(f'{bcolors.PUPRPLE}{bcolors.BOLD}Tworzenie bazy danych zakończone {bcolors.ENDC}')



def convo_check(user1, user2):
    with SQLite(file=file) as cur:
        cur.execute(f"""SELECT id
        FROM converstaions
        WHERE (user_one = '{user1}' AND user_two = '{user2}')
        OR (user_one = '{user2}' AND user_two = '{user1}');
        """)
        data = cur.fetchall()
        if len(data) > 0:
            return data[0][0]
        else:
            cur.execute(f"""INSERT INTO converstaions (user_one, user_two, date_created, date_last_activity)
            VALUES ('{user1}', '{user2}', 'nie', 'nie');
            """)
            cur.execute(f"""SELECT * FROM converstaions ORDER BY id DESC LIMIT 1;""")
            return(cur.fetchall()[0][0])

def add_message(sender,reciver,msg): #muszą być passnięci jako loginy
    con_id = convo_check(sender, reciver)
    with SQLite(file=file) as cur:
        cur.execute(f"""INSERT INTO messages (date_sent, sender_id, conversation_id)
        VALUES ('{msg}','{sender}','{con_id}');
        """)

def user_log_in(user, password):
    with SQLite(file=file) as cur:
        cur.execute(f"""SELECT
            login,
            password
        FROM
            users
        WHERE
            login = "{user}";
        """.format(user))
        login_info = cur.fetchall()
        try:
            return login_info[0][1] == password # if password matches we return True, but if it does not we return False
        except Exception as e: #TODO dodać loggowanie tego błędu, jak inny niż index out of range
            return False # if for any reason the entry cannot be found or is incomplete, we just return False



"""
USERS
    ID
    LOGIN
    PASSWORD
    MAIL
    STATUS (UNVERIFIED/MOD/ADMIN)

CONVO
    ID
    USER_one
    user_two
    DATE_CREATED

MESSAGES
    ID
    CONVO_ID
    USER_ID (SENDER)
    TIME_SENT

"""
