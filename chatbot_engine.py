import tensorflow as tf
from transformers import AlbertTokenizer, TFAlbertForSequenceClassification
import json
from utils import format_justified_text, save_unanswered_question
import re

MAX_LENGTH = 36
PRED_THRESHOLD = 0.7

model_path = "resources/models/ALBERT"
tokenizer_path = "resources/models/tokenizer"
answers_path = "config/answers.json"

model = TFAlbertForSequenceClassification.from_pretrained(model_path)
tokenizer = AlbertTokenizer.from_pretrained(tokenizer_path)

with open(answers_path, "r", encoding="utf-8") as json_file:
    answers_dict = json.load(json_file)


def preprocess_text(text):
    """
    Preprocesa el texto para:
    - Reemplazar símbolos o cualquier carácter no alfanumérico por un espacio
    - Convertir el texto a minúsculas
    - Asegurar que solo haya un espacio entre palabras
    - Eliminar espacios al inicio y al final
    """
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    text = text.lower()
    return text


def warmup_inferences(count=5):
    sample_texts = [
        "Hola",
        "¿Cómo estás?",
        "Cuéntame más",
        "Eso es interesante",
        "Sigue así",
    ]
    for text in sample_texts[:count]:
        encodings = tokenizer(
            text,
            return_tensors="tf",
            padding="max_length",
            truncation=True,
            max_length=MAX_LENGTH,
        )
        _ = model.predict(
            {
                "input_ids": encodings["input_ids"],
                "attention_mask": encodings["attention_mask"],
            },
            verbose=0,
        )


def make_inference(question):
    mod_question = preprocess_text(question)
    encodings = tokenizer(
        mod_question,
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH,
        return_tensors="tf",
    )
    predictions = model.predict(
        {
            "input_ids": encodings["input_ids"],
            "attention_mask": encodings["attention_mask"],
        },
        verbose=0,
    )
    predictions = tf.nn.softmax(predictions.logits, axis=-1)
    max_prob = tf.reduce_max(predictions).numpy()

    predicted_class = tf.argmax(predictions, axis=-1).numpy()[0]
    predicted_label = answers_dict.get(str(predicted_class), "Respuesta no encontrada.")
    return predicted_label, max_prob


def get_response(question, line_width=40):
    response, max_prob = make_inference(question)
    if max_prob < PRED_THRESHOLD:
        save_unanswered_question(question)
        response = "En este momento, no dispongo de la información suficiente para proporcionar una respuesta precisa."
    formatted_response = format_justified_text(response, line_width)
    return formatted_response
