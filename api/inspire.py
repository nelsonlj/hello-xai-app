from http.server import BaseHTTPRequestHandler
import os
import json
from openai import OpenAI
import psycopg2

# 1. Setup xAI
client = OpenAI(
    api_key=os.environ.get("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

# 2. Setup Database Connection
# Vercel provides 'POSTGRES_URL' automatically
def get_db_connection():
    return psycopg2.connect(os.environ.get("POSTGRES_URL"))

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        self.end_headers()

    def do_GET(self):
        conn = None
        try:
            # --- A. Generate the Roast (xAI) ---
            completion = client.chat.completions.create(
                model="grok-4-1-fast-non-reasoning",
                messages=[
                    {"role": "system", "content": "You are a savage stand-up comedian."},
                    {"role": "user", "content": "Roast a software engineer who uses 'Hello World' apps to impress people. Keep it short (under 20 words)."}
                ]
            )
            new_roast = completion.choices[0].message.content

            # --- B. Database Operations (Neon) ---
            conn = get_db_connection()
            cur = conn.cursor()

            # 1. Insert the new roast
            cur.execute("INSERT INTO roasts (content) VALUES (%s)", (new_roast,))
            conn.commit()

            # 2. Fetch the last 5 roasts (History)
            cur.execute("SELECT content FROM roasts ORDER BY created_at DESC LIMIT 5")
            rows = cur.fetchall()
            # formatting: rows comes back like [('roast 1',), ('roast 2',)]
            history = [row[0] for row in rows]

            # --- C. Send Response ---
            response_data = {
                "current_roast": new_roast,
                "history": history
            }

            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))
        
        finally:
            # Always close the connection to avoid leaks!
            if conn:
                cur.close()
                conn.close()