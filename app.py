import os
import json
import openai
from http.server import HTTPServer, BaseHTTPRequestHandler

client = openai.OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>DeepSeek Chatbot</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; height: 100vh; display: flex; flex-direction: column; }
        .header { background: #16213e; padding: 15px; text-align: center; font-size: 1.5em; font-weight: bold; }
        .chat { flex: 1; overflow-y: auto; padding: 20px; }
        .message { margin-bottom: 15px; padding: 10px 15px; border-radius: 10px; max-width: 80%; }
        .user { background: #0f3460; margin-left: auto; text-align: right; }
        .bot { background: #533483; }
        .input-area { display: flex; padding: 15px; background: #16213e; }
        .input-area input { flex: 1; padding: 12px; border: none; border-radius: 8px; background: #1a1a2e; color: #fff; font-size: 1em; }
        .input-area button { padding: 12px 20px; margin-left: 10px; border: none; border-radius: 8px; background: #e94560; color: #fff; cursor: pointer; font-size: 1em; }
        .input-area button:hover { background: #c73e54; }
        .loading { color: #888; font-style: italic; }
    </style>
</head>
<body>
    <div class="header">🤖 DeepSeek Chatbot</div>
    <div class="chat" id="chat">
        <div class="message bot">Hello! How can I help you today?</div>
    </div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Type your message..." onkeypress="if(event.key==='Enter') send()">
        <button onclick="send()">Send</button>
    </div>
    <script>
        async function send() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (!message) return;
            
            const chat = document.getElementById('chat');
            chat.innerHTML += `<div class="message user">${message}</div>`;
            chat.innerHTML += `<div class="message bot loading">Thinking...</div>`;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;
            
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                const data = await res.json();
                const loadingMsg = document.querySelector('.loading');
                if (loadingMsg) loadingMsg.remove();
                chat.innerHTML += `<div class="message bot">${data.reply}</div>`;
            } catch (e) {
                const loadingMsg = document.querySelector('.loading');
                if (loadingMsg) loadingMsg.remove();
                chat.innerHTML += `<div class="message bot">Error: Could not reach server.</div>`;
            }
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(content_length))
            user_message = body.get('message', '')
            
            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": user_message}]
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = f"Error: {str(e)}"
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply}).encode())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'Server running on port {port}')
    server.serve_forever()
