####################################### Imports #######################################
from customtkinter import *
from tkinter import CENTER, DISABLED, NORMAL, messagebox
from PIL import ImageTk, Image
import mss
import socket
import struct
from cv2 import (
    imwrite,
    imread,
    bitwise_and,
    bitwise_not,
    cvtColor,
    boundingRect,
    rectangle,
    COLOR_BGR2GRAY,
)
from numpy import array, repeat, zeros, clip, newaxis, random, expand_dims
from os import path, mkdir
from datetime import datetime
from pathlib import Path
from pickle import load
from pynput import mouse
from shutil import move
from threading import Thread

###################################### Functions ######################################


def processing(
    user: str = None, stamp=None, x=None, y=None, stamp_time: str = None
) -> None:
    """
    Function that processes an image for the current classifier method. Image is saved in the user
    directory, withing the 'Processed' folder.

    Args:
        user (string): The name of the user
        stamp (any): The filename
        x (any): The x coordinate of the action
        y (any): The y coordinate of the action
        stamp_time (string): The stamp time of the action

    Returns:
        None
    """
    x = int(x)
    y = int(y)
    img_array = imread(
        path.join(path_to_prog, "NNGUI", f"{user}", f"{today}", "Full", f"{stamp}")
    )
    mask_1 = zeros(img_array.shape[:2], dtype="uint8")
    mask_2 = zeros(img_array.shape[:2], dtype="uint8")
    mask_1[
        max(0, y - height_to_process // 2) : min(height, y + height_to_process // 2),
        max(0, x - width_to_process // 3) : min(width, x + width_to_process // 3),
    ] = 255

    mask_2[
        max(0, y - height_to_process) : min(height, y + height_to_process),
        max(0, x - width_to_process) : min(width, x + width_to_process),
    ] = 255

    # Convert the rest of the image to grayscale
    img_gray = cvtColor(img_array, COLOR_BGR2GRAY)
    img_gray = repeat(img_gray[..., newaxis], 3, axis=-1)

    # Multiply the color region by a factor of 2
    color_region_1 = bitwise_and(img_array, img_array, mask=mask_1)
    color_region_1[..., 2] *= 2
    color_region_1 = clip(color_region_1, 0, 255).astype("uint8")

    color_region_2 = bitwise_and(img_array, img_array, mask=mask_2) * 1
    color_region_2 = clip(color_region_2, 0, 255).astype("uint8")

    # Merge the grayscale and color regions
    img_result = (
        color_region_1
        + color_region_2
        + bitwise_and(img_gray, img_gray, mask=bitwise_not(mask_2))
    )
    x, y, w, h = boundingRect(mask_2)
    rectangle(img_result, (x, y), (x + w, y + h), (0, 255, 0), 2)

    width_mult = 6
    height_mult = 6

    if x - width // width_mult < 0:
        left = 0
        right = 2 * width // width_mult
    elif x + width // width_mult > width:
        left = width - 2 * width // width_mult
        right = width
    else:
        left = x - width // width_mult
        right = x + width // width_mult
    if y - height // height_mult < 0:
        top = 0
        bottom = 2 * height // height_mult
    elif y + height // height_mult > height:
        top = height - 2 * height // height_mult
        bottom = height
    else:
        top = y - height // height_mult
        bottom = y + height // height_mult

    img_result = img_result[top:bottom, left:right]

    imwrite(
        str(
            path_to_prog
            / "NNGUI"
            / f"{user}"
            / f"{today}"
            / "Processed"
            / f"{stamp_time}"
        ),
        img_result,
    )


def screenshot_mss(user: str = None, x: int = None, y: int = None) -> None:
    """
    Function that takes screenshots of the screen and saves the image in the user directory,
    within the 'Full' folder. The filename includes the x and y coordinates and a timestamp.

    Args:
        user (string): The name of the user
        x (int): The x coordinate of the action
        y (int): The y coordinate of the action

    Returns:
        None
    """
    if not path.exists(path_to_prog / "NNGUI" / f"{user}"):
        mkdir(path_to_prog / "NNGUI" / f"{user}")
    if not path.exists(path_to_prog / "NNGUI" / f"{user}" / f"{today}/"):
        mkdir(path_to_prog / "NNGUI" / f"{user}" / f"{today}")
        mkdir(path_to_prog / "NNGUI" / f"{user}" / f"{today}" / "Full")
        mkdir(path_to_prog / "NNGUI" / f"{user}" / f"{today}" / "Processed")
        # mkdir(path_to_prog / "NNGUI" / f"{user}" / f"{today}" / "Classified")
    sct = mss.mss()
    current_time = datetime.now().time()
    sct_img = sct.grab(sct.monitors[0])
    img = array(sct_img)[:, :, :3]
    imwrite(
        str(
            path_to_prog
            / "NNGUI"
            / f"{user}"
            / f"{today}"
            / "Full"
            / f"{x} {y} {current_time.hour}_{current_time.minute}_{current_time.second}_{current_time.microsecond // 1000}.png"
        ),
        img,
    )


def format_justified_text(text, line_width):
    """
    Formats the given text into a justified format.

    Args:
        text (str): The text to be formatted.
        line_width (int): The maximum width of each line in characters.

    Returns:
        str: The formatted text.
    """
    words = text.split()
    formatted_lines = []
    current_line = []

    for word in words:
        if len(" ".join(current_line + [word])) > line_width:
            formatted_lines.append(" ".join(current_line))
            current_line = [word]
        else:
            current_line.append(word)

    if current_line:
        formatted_lines.append(" ".join(current_line))

    return "\n".join(formatted_lines)


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


def read_config(filename: str = None) -> list:
    """
    Function that reads the configuration file to setup the main program.

    Args
        filename (string): The file to be read for the configuration.

    Returns:
        data (list): The list with the parameters to be set.
    """
    if not os.path.exists(filename):
        messagebox.showerror("Error", "El archivo de configuración no existe.")
        return [
            "Arial",
            "14",
            "17",
            "light",
            "blue",
            "40",
            "localhost",
            "10000",
        ]
    with open(filename, "r") as file:
        line = file.readline().strip()
    data = line.split(",")
    data[3] = data[3] if data[3] in ["light", "dark", "system"] else "system"
    data[4] = data[4] if data[4] in ["blue", "green", "dark-blue"] else "blue"
    data[5] = int(data[5])
    data[-1] = int(data[-1])
    return data


###################################### Variables ######################################

today = datetime.now().date()
path_to_prog = Path.home() / "Documents"
height = mss.mss().monitors[0]["height"]
width = mss.mss().monitors[0]["width"]
width_to_process = width // 229
height_to_process = height // 144
pro_height, pro_width = (224, 224)
user_name = ""

##################################### Initialization #####################################

# Make main directory if does not exist
if not path.exists(path_to_prog / "NNGUI"):
    mkdir(path_to_prog / "NNGUI")

# Load and set configuration file
(
    FAMILY_FONT,
    FONT_SIZE,
    FONT_BOLD_SIZE,
    APPEARANCE,
    COLOR_THEME,
    LINE_WIDTH,
    HOST,
    PORT,
) = read_config("ConfigFiles/config.txt")
set_appearance_mode(str(APPEARANCE))
set_default_color_theme(str(COLOR_THEME))

if APPEARANCE == "dark":
    APPEARANCE_VALUES = ["Oscuro", "Claro", "Sistema"]
elif APPEARANCE == "light":
    APPEARANCE_VALUES = ["Claro", "Oscuro", "Sistema"]
else:
    APPEARANCE_VALUES = ["Sistema", "Claro", "Oscuro"]
