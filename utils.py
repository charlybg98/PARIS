####################################### Imports #######################################
from customtkinter import *
from tkinter import CENTER, DISABLED, NORMAL, messagebox
import mss
from pandas import (DataFrame,
                    Series,
                    concat,
                    to_datetime)
from cv2 import (imwrite,
                 imread,
                 bitwise_and,
                 bitwise_not,
                 cvtColor,
                 boundingRect,
                 rectangle,
                 COLOR_BGR2GRAY)
from numpy import (array,
                   repeat,
                   zeros,
                   clip,
                   newaxis,
                   random,
                   expand_dims)
from os import (path,
                mkdir)
from datetime import datetime
from pathlib import Path
from transformers import (BertTokenizer,
                          TFBertModel)
from pickle import load
from tensorflow import argmax, image
from keras.models import load_model
from keras import losses
from pynput import keyboard, mouse
from shutil import move
from threading import Thread
from tensorflow import nn, reduce_max

###################################### Functions ######################################


def processing(user: str = None, stamp=None, x=None, y=None, stamp_time: str = None) -> None:
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
        path.join(path_to_prog, "NNGUI",
                  f"{user}", f"{today}", "Full", f"{stamp}")
    )
    mask_1 = zeros(img_array.shape[:2], dtype="uint8")
    mask_2 = zeros(img_array.shape[:2], dtype="uint8")
    mask_1[
        max(0, y - height_to_process // 2): min(height, y + height_to_process // 2),
        max(0, x - width_to_process // 3): min(width, x + width_to_process // 3),
    ] = 255

    mask_2[
        max(0, y - height_to_process): min(height, y + height_to_process),
        max(0, x - width_to_process): min(width, x + width_to_process),
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


def formatting(text: str = None, line_width: int = 58, left_pad: int = 4) -> str:
    """
    Outputs the text formatted to fit the width selected.

    Args:
        text (string): String to be formatted
        line_width (int): Text is fitted to this width
        left_pad (int): In case space is required before the text

    Returns:
        Formatted_text (string): Text formatted as required
    """
    texto_to_list = text.split()
    formatted_text = ""
    count = left_pad

    for word in texto_to_list:
        if count+len(word) <= line_width:
            formatted_text += word+" "
            count += len(word)+1
        else:
            formatted_text += "\n"
            formatted_text += word+" "
            count = len(word)+1

    return formatted_text


def get_response(question: str = None) -> str:
    """
    Outputs the answer to a question from the question/answer dataset.

    Args:
        question (string): The input question to be answered

    Returns:
        answer (string): The most probable output to the question, based on the dataset.
    """
    question = str(question)
    question_encoded = tokenizer(question,
                                 truncation=True,
                                 padding='max_length',
                                 max_length=MAX_LENGTH,
                                 return_tensors='tf')
    predictions = chat_model.predict({'input_ids': question_encoded['input_ids'],
                                      'attention_mask': question_encoded['attention_mask']},
                                     verbose=0)
    predictions = nn.softmax(predictions)
    predicted_class = argmax(predictions, axis=-1).numpy()[0]
    predicted_label = encoder.inverse_transform([predicted_class])[0]
    predicted_probability = reduce_max(predictions, axis=-1)[0]
    response = formatting(predicted_label)

    return response


def to_classify():
    pass


def read_config(filename: str = None) -> list:
    """
    Function that reads the configuration file to setup the main program.

    Args
        filename (string): The file to be read for the configuration.

    Returns:
        data (list): The list with the parameters to be set.
    """
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
    data = line.split(',')
    if str(data[3]) not in ['light', 'dark', 'system']:
        data[3] = 'system'
    if str(data[4]) not in ['blue', 'green', 'dark-blue']:
        data[4] = 'blue'

    return data


def warmup() -> None:
    """
    Function that serves as a warmup for the chatbot model

    Args:
        None

    Returns:
        None
    """
    tensor_warmup = "a"
    tensor_encoded = tokenizer(
        tensor_warmup,
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH,
        return_tensors="tf",
    )
    chat_model.predict(
        {
            "input_ids": tensor_encoded["input_ids"],
            "attention_mask": tensor_encoded["attention_mask"],
        },
        verbose=0,
    )


###################################### Variables ######################################

today = datetime.now().date()
path_to_prog = Path.home() / "Documents"
height = mss.mss().monitors[0]["height"]
width = mss.mss().monitors[0]["width"]
width_to_process = width // 229
height_to_process = height // 144
MAX_LENGTH = 23
pro_height, pro_width = (224, 224)
user_name = ""

##################################### Initialization #####################################

# Make main directory if does not exist
if not path.exists(path_to_prog / "NNGUI"):
    mkdir(path_to_prog / "NNGUI")

# Load tokenizer
tokenizer_path = 'dccuchile/bert-base-spanish-wwm-cased'
tokenizer = BertTokenizer.from_pretrained(tokenizer_path)

# Load Chatbot label encoder/decoder
with open('ConfigFiles/encoder.pkl', 'rb') as f:
    encoder = load(f)

# Load Classification label decoder
with open("ConfigFiles/selection_list.pickle", "rb") as f:
    selection_options = sorted(load(f))

# Load Chatbot model
chat_model = load_model('Models/BERT_trained',
                        custom_objects={"TFBertModel": TFBertModel})

# Load Classification model
classification_model = load_model("Models/model_MobileNet",
                                  compile=False)
classification_model.compile("adam",
                             loss=losses.CategoricalCrossentropy(),
                             metrics=["accuracy"])

# Models warmup

warmup()

# Load and set configuration file
FAMILY_FONT, FONT_SIZE, FONT_BOLD_SIZE, APPEARANCE, COLOR_THEME, CLASSIFIER_STATUS, CHATBOT_STATUS = read_config(
    'config.txt')
set_appearance_mode(str(APPEARANCE))
set_default_color_theme(str(COLOR_THEME))
