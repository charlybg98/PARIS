####################################### Imports #######################################
from utils import HOST, PORT, format_justified_text
import socket
import struct


###################################### Functions ######################################
def send_to_server(text_to_send, server_address=("192.168.1.7", 10000)):
    """
    Sends the given text to the server for processing and returns the server's response.

    Args:
        text_to_send (str): The text to send to the server.
        server_address (tuple): A tuple containing the server's IP address and port number.

    Returns:
        str: The response received from the server.
    """
    # Connect to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(server_address)

        # Encode and send the text
        text_data = text_to_send.encode("utf-8")
        text_length = len(text_data)
        sock.sendall(struct.pack("!I", text_length))
        sock.sendall(text_data)

        # Receive and decode the response
        response = sock.recv(4096).decode("utf-8")
        return response


def check_server_availability(host, port):
    """Check if the server is available."""
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def get_response(question, line_width=40):
    """
    Modified to send the question to the server, receive the response, and format it.

    Args:
        question (str): The question to be sent to the server.
        line_width (int): The maximum width of each line in characters for text formatting.

    Returns:
        str: The formatted response from the server.
    """
    response = send_to_server(question, (HOST, PORT))
    formatted_response = format_justified_text(response, line_width)
    return formatted_response
