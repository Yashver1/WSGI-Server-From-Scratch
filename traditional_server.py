import socket

HOST,PORT = '',8888

internet_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
internet_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
internet_socket.bind((HOST,PORT))
internet_socket.listen(1)
print(f"Serving HTTP on port {PORT}")


while True:
    connection, address = internet_socket.accept()
    with connection:
        print (f'Connected by: {address}')
        request_data = connection.recv(1024)
        print(request_data.decode('utf-8'))

        response = b"""\
HTTP/1.1 200 OK

Hello,World!                   
        """
        connection.sendall(response)
        
#response needs to be flushed to the left

