import socket
import atexit
import builtins
import base64


def patch_print_and_input():
    # Save the original print and input functions
    builtins.__print__ = builtins.print
    builtins.__input__ = builtins.input

    # Connect to a socket and register cleanup
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 12355))
    server_socket.listen(1)
    client_socket, address = server_socket.accept()
    print(f"Accepted connection from {address}")

    def cleanup_server():
        client_socket.close()
        server_socket.close()
        # print("Server sockets closed.")

    atexit.register(cleanup_server)

    # Patch print to write to the socket
    def socket_print(
        *objects, sep=" ", end="\n", file=None, flush=True, __input_req__=False
    ):
        """uses a signature that matches print function so it can patch
        built in print.

        Additional "secret" parameter __input_req__ is used to signify that
        a packet should be sent to dumb client to provide an input

        the flus argument is ignored always except if someone is printing to
        a file

        # todo: dokumentoi tarkkaan miten patch toimii

        if file argument is provided, the printing wont happen into a socket
        """

        if file is not None:
            # Soeone is trying to print to a specific file. Lets print to
            # there instead
            builtins.__print__(*objects, sep, end, file, flush)
            return

        message = sep.join(str(obj) for obj in objects) + end

        b64_message = base64.b64encode(message.encode("utf-8")).decode("utf-8")
        b64_message += "\n"  # We use a newline as an end of message.
        # It cant occur in the b64 so its safe to use.

        if __input_req__:  # tell the client that the print should be
            # used for input instead
            b64_message = "@" + b64_message

        client_socket.sendall(b64_message.encode())

    def socket_input(prompt):
        socket_print(
            prompt, end="", __input_req__=True
        )  # input does not put newline when reading

        # receive a packet
        buffer = b""  # Use bytes for the buffer
        while True:
            data = client_socket.recv(1)  # Receive one byte at a time
            if data == b"\n":
                # Newline encountered, break the loop
                break
            buffer += data
        # print("received input", buffer.decode('utf-8'))

        # disable nagle algorithm to prefer many small packets over fewer
        # larger packats. this makes holding down enter in input prompt less
        # likely to cause artifacts arising from buffering
        return base64.b64decode(buffer).decode(
            "utf-8"
        )  # Assuming the text is in UTF-8 encoding

    builtins.print = socket_print
    builtins.input = socket_input

    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)


patch_print_and_input()
# Server loop
# time.sleep(1)
while True:
    # Use the patched input function to get data from the client
    data = input(">>> ")
    print(data)


# term size pitää pakottaa 80 kun remote yhteys koska voi olla headless

# myös client-> server pitää paketoida b64


# packet structure: [@][base64][\n]
# newline is end of message, we always read until newline.
# base64 will never contain an newline or @ so they are safe to use.
# the optional starting @ signifies that that the print should be used fo
# input instead of printing.
