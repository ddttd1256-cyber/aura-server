from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Разрешаем твоему сайту на GitHub общаться с этим сервером
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    conn = sqlite3.connect("aura.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, recipient TEXT, text TEXT)''')
    conn.commit()
    conn.close()

init_db()

class User(BaseModel):
    username: str
    name: str = ""

class Message(BaseModel):
    sender: str
    recipient: str
    text: str

@app.post("/register")
def register(user: User):
    conn = sqlite3.connect("aura.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (username, name) VALUES (?, ?)", (user.username, user.name))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/check_user/{username}")
def check_user(username: str):
    conn = sqlite3.connect("aura.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return {"exists": bool(user)}

@app.post("/send")
def send_message(msg: Message):
    conn = sqlite3.connect("aura.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender, recipient, text) VALUES (?, ?, ?)", (msg.sender, msg.recipient, msg.text))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/chat/{user1}/{user2}")
def get_chat(user1: str, user2: str):
    conn = sqlite3.connect("aura.db")
    c = conn.cursor()
    c.execute('''SELECT sender, text FROM messages 
                 WHERE (sender=? AND recipient=?) OR (sender=? AND recipient=?) 
                 ORDER BY id ASC''', (user1, user2, user2, user1))
    msgs = [{"sender": row[0], "text": row[1]} for row in c.fetchall()]
    conn.close()
    return {"messages": msgs}
