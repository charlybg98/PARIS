####################################### Imports #######################################
from customtkinter import set_appearance_mode, set_default_color_theme
from os import path, mkdir
from pathlib import Path
from tkinter import messagebox

###################################### Variables ######################################
path_to_prog = Path.home() / "Documents"
user_name = ""
user_id = ""


###################################### Functions ######################################
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


def read_config(filename: str = None) -> list:
    """
    Function that reads the configuration file to setup the main program.

    Args
        filename (string): The file to be read for the configuration.

    Returns:
        data (list): The list with the parameters to be set.
    """
    if not path.exists(filename):
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
) = read_config("config/config.txt")
set_appearance_mode(str(APPEARANCE))
set_default_color_theme(str(COLOR_THEME))

if APPEARANCE == "dark":
    APPEARANCE_VALUES = ["Oscuro", "Claro", "Sistema"]
elif APPEARANCE == "light":
    APPEARANCE_VALUES = ["Claro", "Oscuro", "Sistema"]
else:
    APPEARANCE_VALUES = ["Sistema", "Claro", "Oscuro"]
