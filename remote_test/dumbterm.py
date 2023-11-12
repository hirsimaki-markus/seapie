import socket
import sys
import atexit
import base64


# Create a client socket and connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 12355))


# Register the cleanup function to close the client socket on exit
def cleanup_client():
    client_socket.close()
    print("Client socket closed.")


atexit.register(cleanup_client)


def read_socket_until_newline(sock):
    """Reads the b64 + newline encoded message from a socket"""
    buffer = b""  # Use bytes for the buffer

    while True:
        data = sock.recv(1)  # Receive one byte at a time
        if data == b"\n":
            # Newline encountered, break the loop
            break
        buffer += data
    # print("received input", buffer.decode('utf-8'))

    if buffer.startswith(b"@"):
        # this is input
        return (
            base64.b64decode(buffer[1:]).decode("utf-8"),
            True,
        )  # Assuming the text is in UTF-8 encoding
    else:
        return base64.b64decode(buffer).decode("utf-8"), False


def socket_send_message(message):
    """uses a signature that matches print function so it can patch
    built in print.
    """

    b64_message = base64.b64encode(message.encode("utf-8")).decode("utf-8")
    b64_message += "\n"  # We use a newline as an end of message.
    # It cant occur in the b64 so its safe to use.
    client_socket.sendall(b64_message.encode())


# disable nagle algorithm to prefer many small packets over fewer larger packats.
# this makes holding down enter in input prompt less likely to cause
# artifacts.
client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

# Client loop
try:
    while True:
        message, input_requested = read_socket_until_newline(client_socket)

        if input_requested:
            user_input = input(message)
            socket_send_message(user_input)  # send a packet
        else:
            print(
                message, end=""
            )  # client should not print with newline, remote already does


except KeyboardInterrupt:
    pass
finally:
    cleanup_client()
