from os import path, mkdir
from pathlib import Path
from tkinter import messagebox
from datetime import datetime
from pathlib import Path
import json


def path_initialization(user: str = None):
    path_to_prog = Path.home() / "Documents"
    today = datetime.now().date()

    if not path.exists(path_to_prog / "NNGUI"):
        mkdir(path_to_prog / "NNGUI")
    if not path.exists(path_to_prog / "NNGUI" / f"{user}"):
        mkdir(path_to_prog / "NNGUI" / f"{user}")
    if not path.exists(path_to_prog / "NNGUI" / f"{user}" / f"{today}/"):
        mkdir(path_to_prog / "NNGUI" / f"{user}" / f"{today}")
        mkdir(path_to_prog / "NNGUI" / f"{user}" / f"{today}" / "Processed")


def format_justified_text(text, line_width, user_len=7):
    """
    Formats the given text into a justified format, considering the length of the user's name.

    Args:
        text (str): The text to be formatted.
        line_width (int): The maximum width of each line in characters.
        user_len (int): The length to subtract from the line width for the first line.

    Returns:
        str: The formatted text.
    """
    words = text.split()
    formatted_lines = []
    current_line = []
    is_first_line = True

    def justify_line(line, width):
        if len(line) == 1:
            return line[0]
        spaces_needed = width - sum(len(word) for word in line)
        spaces_between_words = spaces_needed // (len(line) - 1)
        extra_spaces = spaces_needed % (len(line) - 1)

        justified_line = ""
        for i, word in enumerate(line[:-1]):
            justified_line += word + " " * (
                spaces_between_words + (1 if i < extra_spaces else 0)
            )
        justified_line += line[-1]

        return justified_line

    for word in words:
        if (
            is_first_line
            and len(" ".join(current_line + [word])) > line_width - user_len
        ):
            formatted_lines.append(justify_line(current_line, line_width - user_len))
            current_line = [word]
            is_first_line = False
        elif not is_first_line and len(" ".join(current_line + [word])) > line_width:
            formatted_lines.append(justify_line(current_line, line_width))
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
