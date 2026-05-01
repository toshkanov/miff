from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"I am alive!")

    def log_message(self, format, *args):
        return

def run_uptimer(port):
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Uptimer server {port}-portda ishga tushdi...")
    server.serve_forever()

def start_uptimer():
    # Render taqdim etadigan PORT'ni olamiz
    port = int(os.environ.get("PORT", 8000))
    # Alohida oqimda (Thread) ishga tushiramiz
    thread = threading.Thread(target=run_uptimer, args=(port,), daemon=True)
    thread.start()