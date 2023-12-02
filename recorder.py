####################################### Imports #######################################
from mss import mss
from datetime import datetime
from os import mkdir, path
from cv2 import imwrite
from numpy import array
from pathlib import Path

###################################### Variables ######################################
today = datetime.now().date()
path_to_prog = Path.home() / "Documents"


###################################### Functions ######################################
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

    sct = mss()
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
