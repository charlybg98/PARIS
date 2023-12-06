from mss import mss
from numpy import array
from datetime import datetime


def screenshot_mss():
    """
    Takes a screenshot of the entire screen using the mss library and returns the timestamp
    at which the screenshot was taken along with the image array.

    Returns:
        tuple: A tuple containing the timestamp of the screenshot and the image array.
    """
    with mss() as sct:
        sct_img = sct.grab(sct.monitors[0])
        img = array(sct_img)[:, :, :3]

    timestamp = datetime.now().strftime("%H_%M_%S_%f")[:-3]

    return timestamp, img
