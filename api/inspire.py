from http.server import BaseHTTPRequestHandler
import os
import json
from openai import OpenAI

# Initialize xAI client
# Note: xAI uses the OpenAI SDK format but with a different base URL
client = OpenAI(
    api_key=os.environ.get("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Handle the "preflight" check that browsers do
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        self.end_headers()

    def do_GET(self):
        try:
            # 1. Call xAI (Grok)
            completion = client.chat.completions.create(
                model="grok-4-1-fast-non-reasoning", 
                messages=[
                    {"role": "system", "content": "You are a creative muse."},
                    {"role": "user", "content": "Generate a short, witty, 'Hello World' themed inspirational quote. Randomize the output."}
                ]
            )
            message = completion.choices[0].message.content

            # 2. Return success
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": message}).encode('utf-8'))

        except Exception as e:
            # 3. Return error
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))
