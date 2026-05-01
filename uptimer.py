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
        # Konsolga ortiqcha loglar chiqarmaslik uchun
        return

def run_uptimer(port=8000):
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Uptimer server {port}-portda ishga tushdi...")
    server.serve_forever()

def start_uptimer():
    # Asosiy bot ishlashiga xalaqit bermasligi uchun alohida oqimda ishga tushiramiz
    thread = threading.Thread(target=run_uptimer, daemon=True)
    thread.start()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000)) # Render bergan portni oladi
    app.run(host="0.0.0.0", port=port) # 0.0.0.0 barcha manzillardan eshitadi