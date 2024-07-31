import io 
import socket
import sys

class WSGIServer(object):
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 1

    def __init__(self,server_address):

        #both point to same object
        self.listen_socket = listen_socket = socket.socket(
            self.address_family,
            self.socket_type
        )

        listen_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        listen_socket.bind(server_address)
        listen_socket.listen(self.request_queue_size)
        host,port = self.listen_socket.getsockname()[:2] #get host and port from 
        self.server_name = socket.getfqdn(host) # full server name for debug and DNS purposes
        self.server_port = port
        self.headers_set = [] # the return headers set by the Web App

    def set_app(self,application):
        self.application = application #for the WebApp

    def serve_forever(self): #listen loop
        listen_socket = self.listen_socket
        while True:
            self.client_connection,client_address = listen_socket.accept()
            self.handle_one_request()

    def handle_one_request(self):
        request_data = self.client_connection.recv(1024)
        self.request_data = request_data = request_data.decode('utf-8')
        print(''.join( # print request line by line
            f'< {line}\n' for line in request_data.splitlines()
        ))

        self.parse_request(request_data) # parse to get first line of request

        env = self.get_environ() #create environment dict with request data

        result = self.application(env, self.start_response)
        self.finish_response(result)

    def parse_request(self, text):
        request_line = text.splitlines()[0]
        request_line = request_line.rstrip('\r\n') # Windows way of newline, start at front and go down one line
        (self.request_method,
        self.path,
        self.request_version
        ) = request_line.split()

    def get_environ(self):
        env = {}
        #wsgi variables
        env['wsgi.version'] = (1,0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = io.StringIO(self.request_data) # Treat the string as a file
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False
        #wsgi cgi variables
        env['REQUEST_METHOD'] = self.request_method 
        env['PATH_INFO'] = self.path
        env['SERVER_NAME'] = self.server_name
        env['SERVER_PORT'] = str(self.server_port)
        return env
    
    def start_response(self, status, response_headers, exc_info=None):
        server_headers = [
            ('Date', 'Mon, 15 Jul 2019 5:54:48 GMT'),
            ('Server', 'WSGIServer 0.2'),
        ]
        self.headers_set = [status, response_headers + server_headers]

    def finish_response(self,result):
        try:
            status, response_headers = self.headers_set
            response = f'HTTP/1.1 {status}\r\n'
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header) #unpack header
            response += '\r\n'
            for data in result:
                response += data.decode('utf-8')
                print(''.join(
                    f'> {line}\n' for line in response.splitlines()
                ))
                response_bytes = response.encode() #back to bytes
                self.client_connection.sendall(response_bytes)
        finally:
            self.client_connection.close()

SERVER_ADDRESS = (HOST,PORT) = '',8888

def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)
    return server

if __name__ == '__main__':
    if len(sys.argv) < 2: #need 3 arguments
        sys.exit('Provide a WSGI application object as module:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module,application) #the dynamic version of module.application but application name only known at runtime
    httpd = make_server(SERVER_ADDRESS,application)
    print(f'WSGIServer: Serving HTTP on port {PORT} ...\n')
    httpd.serve_forever()
        