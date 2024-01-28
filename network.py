import socket
import struct
import cv2


def send_image_array_to_server(image_array, server_address=("localhost", 10000)):
    """
    Sends an image array to the server for classification and returns the Label_int received from the server.

    Args:
        image_array (numpy.ndarray): The image array to send to the server.
        server_address (tuple): The server's IP address and port number as a tuple.

    Returns:
        int: The Label_int received from the server.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(server_address)

        result, image_data = cv2.imencode('.png', image_array)
        if not result:
            raise RuntimeError("Error al codificar la imagen")

        image_bytes = image_data.tobytes()

        message_length = struct.pack("!I", len(image_bytes))
        sock.sendall(message_length + image_bytes)

        label_int_data = sock.recv(4)
        if label_int_data:
            label_int = struct.unpack("!I", label_int_data)[0]
            return label_int
        else:
            raise RuntimeError("No se recibió Label_int del servidor")


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
