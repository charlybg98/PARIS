from utils import format_justified_text, save_unanswered_question
import socket
import struct


def send_to_server(text_to_send, server_address=("localhost", "10000")):
    """
    Sends the given text to the server for processing and returns the server's response.

    Args:
        text_to_send (str): The text message to send to the server.
        server_address (tuple): The server's IP address and port number as a tuple.

    Returns:
        str: The text response received from the server.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(server_address)

        text_data = text_to_send.encode("utf-8")
        text_length = len(text_data)
        sock.sendall(struct.pack("!I", text_length))
        sock.sendall(text_data)

        response = sock.recv(4096).decode("utf-8")
        return response


def check_server_availability(host="localhost", port=10000):
    """
    Checks the availability of a server at the given host address and port.

    Args:
        host (str): The IP address of the server to check.
        port (int): The port number of the server to check.

    Returns:
        bool: True if the server is available, False otherwise.
    """
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def get_response(question, line_width=40):
    """
    Sends a question to the server, receives the response, and formats it to a specified line width.

    Args:
        question (str): The question to send to the server.
        line_width (int): The desired maximum width of each line in characters.

    Returns:
        str: The formatted response from the server.
    """
    response = send_to_server(question)
    if (
        response
        == "En este momento, no dispongo de la información \
        suficiente para proporcionar una respuesta precisa."
    ):
        save_unanswered_question(question)
    formatted_response = format_justified_text(response, line_width)
    return formatted_response
