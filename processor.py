####################################### Imports #######################################
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
from numpy import repeat, zeros, clip, newaxis
from mss import mss
from datetime import datetime
from pathlib import Path
from os import path

###################################### Variables ######################################

today = datetime.now().date()
path_to_prog = Path.home() / "Documents"
height = mss().monitors[0]["height"]
width = mss().monitors[0]["width"]
width_to_process = width // 229
height_to_process = height // 144

###################################### Functions ######################################


def processing(
    user: str = None, img_array=None, x=None, y=None, stamp_time: str = None
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
        img_result: Image processed
    """
    x = int(x)
    y = int(y)

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

    img_gray = cvtColor(img_array, COLOR_BGR2GRAY)
    img_gray = repeat(img_gray[..., newaxis], 3, axis=-1)

    color_region_1 = bitwise_and(img_array, img_array, mask=mask_1)
    color_region_1[..., 2] *= 2
    color_region_1 = clip(color_region_1, 0, 255).astype("uint8")

    color_region_2 = bitwise_and(img_array, img_array, mask=mask_2) * 1
    color_region_2 = clip(color_region_2, 0, 255).astype("uint8")

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
            / f"{stamp_time}.png"
        ),
        img_result,
    )

    return img_result
