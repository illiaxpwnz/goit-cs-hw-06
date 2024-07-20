import http.server
import socketserver
import multiprocessing
import os
import socket
import cgi
import datetime
import pymongo

# HTTP Server
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        elif self.path == '/message':
            self.path = 'message.html'
        elif self.path.startswith('/static/'):
            self.path = self.path.lstrip('/')
        else:
            self.path = 'error.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        if self.path == '/message':
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            username = form.getvalue('username')
            message = form.getvalue('message')
            
            # Send to socket server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', 5000))
                s.sendall(bytes(str({'username': username, 'message': message}), 'utf-8'))

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Message received and forwarded')
        else:
            self.send_error(404, "File Not Found {}".format(self.path))

def run_http_server():
    handler = MyHttpRequestHandler
    httpd = socketserver.TCPServer(("", 3000), handler)
    print("Serving HTTP at port", 3000)
    httpd.serve_forever()

# Socket Server
def run_socket_server():
    MONGO_URI = "mongodb://mongo:27017/"
    DB_NAME = "messages_db"
    COLLECTION_NAME = "messages"
    
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("", 5000))
    server.listen(5)
    print("Socket server listening on port", 5000)

    while True:
        client_sock, address = server.accept()
        request = client_sock.recv(1024)
        message_data = request.decode('utf-8')
        message_dict = eval(message_data)
        message_dict["date"] = datetime.datetime.now().isoformat()
        collection.insert_one(message_dict)
        client_sock.close()

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=run_http_server)
    p2 = multiprocessing.Process(target=run_socket_server)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
