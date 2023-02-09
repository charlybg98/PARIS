import mss
from cv2 import imwrite, imread, bitwise_and, bitwise_not, cvtColor, COLOR_BGR2GRAY
from numpy import array, repeat, zeros, clip, newaxis
from os import path, mkdir
from datetime import datetime
from pathlib import Path

today = datetime.now().date()
path_to_prog = Path.home() / "Documents"
height = mss.mss().monitors[0]["height"]
width = mss.mss().monitors[0]["width"]

width_to_process = width // 150
height_to_process = height // 45


def processing(user, stamp, x, y, stamp_time):
    # Define the region you want to keep in color
    x = int(x)
    y = int(y)
    img_array = imread(
        path.join(path_to_prog, "NNGUI", f"{user}", f"{today}", "Full", f"{stamp}")
    )
    mask_1 = zeros(img_array.shape[:2], dtype="uint8")
    mask_2 = zeros(img_array.shape[:2], dtype="uint8")
    mask_1[
        max(0, y - height_to_process // 6) : min(height, y + height_to_process // 4),
        max(0, x - width_to_process // 4) : min(width, x + width_to_process // 5),
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


def screenshot_mss(user, x, y):
    if not path.exists(path_to_prog / "NNGUI" / f"{user}"):
        mkdir(path_to_prog / "NNGUI" / f"{user}")
    if not path.exists(path_to_prog / "NNGUI" / f"{user}" / f"{today}/"):
        mkdir(path_to_prog / "NNGUI" / f"{user}" / f"{today}")
        mkdir(path_to_prog / "NNGUI" / f"{user}" / f"{today}" / "Full")
        mkdir(path_to_prog / "NNGUI" / f"{user}" / f"{today}" / "Processed")
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
            / f"{x} {y} {current_time.hour}_{current_time.minute}_{current_time.second}.png"
        ),
        img,
    )
