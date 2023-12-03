####################################### Imports #######################################
from customtkinter import set_appearance_mode, set_default_color_theme
from os import path, mkdir
from pathlib import Path
from tkinter import messagebox
import json

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


def read_config(filename: str = None) -> dict:
    """
    Function that reads the configuration file to setup the main program.

    Args:
        filename (string): The file to be read for the configuration.

    Returns:
        data (dict): The dictionary with the parameters to be set.
    """
    if not path.exists(filename):
        messagebox.showerror("Error", "El archivo de configuración no existe.")
        return {
            "FAMILY_FONT": "Arial",
            "FONT_SIZE": 14,
            "FONT_BOLD_SIZE": 17,
            "APPEARANCE": "light",
            "COLOR_THEME": "blue",
            "LINE_WIDTH": 40,
            "HOST": "localhost",
            "PORT": 10000,
        }

    with open(filename, "r") as file:
        data = json.load(file)

    data["APPEARANCE"] = (
        data.get("APPEARANCE", "system")
        if data.get("APPEARANCE") in ["light", "dark", "system"]
        else "system"
    )
    data["COLOR_THEME"] = (
        data.get("COLOR_THEME", "blue")
        if data.get("COLOR_THEME") in ["blue", "green", "dark-blue"]
        else "blue"
    )
    data["FONT_SIZE"] = int(data.get("FONT_SIZE", 14))
    data["FONT_BOLD_SIZE"] = int(data.get("FONT_BOLD_SIZE", 17))
    data["LINE_WIDTH"] = int(data.get("LINE_WIDTH", 40))
    data["PORT"] = int(data.get("PORT", 10000))

    return data


##################################### Initialization #####################################

if not path.exists(path_to_prog / "NNGUI"):
    mkdir(path_to_prog / "NNGUI")

config_data = read_config("config/config.json")

FAMILY_FONT = config_data["FAMILY_FONT"]
FONT_SIZE = config_data["FONT_SIZE"]
FONT_BOLD_SIZE = config_data["FONT_BOLD_SIZE"]
APPEARANCE = config_data["APPEARANCE"]
COLOR_THEME = config_data["COLOR_THEME"]
LINE_WIDTH = config_data["LINE_WIDTH"]
HOST = config_data["HOST"]
PORT = config_data["PORT"]

set_appearance_mode(APPEARANCE)
set_default_color_theme(COLOR_THEME)

APPEARANCE_OPTIONS = {"Claro": "light", "Oscuro": "dark", "Sistema": "system"}
COLOR_THEME_OPTIONS = {"Azul": "blue", "Azul oscuro": "dark-blue", "Verde": "green"}
FONT_OPTIONS = ["Open Sans", "Arial", "Verdana", "Courier"]
LABEL_TRANSLATIONS = {
    "FAMILY_FONT": "Fuente",
    "FONT_SIZE": "Tamaño de fuente",
    "FONT_BOLD_SIZE": "Tamaño de Fuente en Negrita",
    "APPEARANCE": "Modo de apariencia",
    "COLOR_THEME": "Tema de Color",
    "LINE_WIDTH": "Ancho de línea",
    "HOST": "Dirección del Servidor",
    "PORT": "Puerto",
}
