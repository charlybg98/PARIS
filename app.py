from utils import *
from network import *
from processor import *
from recorder import *
from chatbot_engine import *
from section_classifier import *
from PIL import ImageTk, Image
from customtkinter import (
    CTk,
    CTkImage,
    CTkFrame,
    CTkLabel,
    CTkFont,
    CTkEntry,
    CTkOptionMenu,
    CTkButton,
    CTkScrollbar,
    CTkTextbox,
    CTkToplevel,
    END,
    set_appearance_mode,
    set_default_color_theme,
)
from tkinter import CENTER, DISABLED, NORMAL
from pynput import mouse
from plyer import notification
import time
import json
import random

user_name = ""
user_id = ""
section_classifier = 0
config_data = read_config("config/config.json")
warmup_inferences()

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

with open("config/soft_threshold.json", "r", encoding="utf-8") as f:
    soft_threshold_messages = json.load(f)

with open("config/hard_threshold.json", "r", encoding="utf-8") as f:
    hard_threshold_messages = json.load(f)

with open("config/sections.json", "r", encoding="utf-8") as f:
    section_messages = json.load(f)


class PARISApplication:
    """
    Class that provides GUI for the project
    """

    def __init__(self) -> None:
        """
        initialized values for the GUI
        """
        self.last_click_time = None
        self.section_start_time = None
        self.current_section_label = None
        self.current_section = 0
        self.soft_threshold_message_shown = False
        self.hard_threshold_message_shown = False
        self.is_recording = False
        self.window = CTk()
        self.FONT = CTkFont(family=FAMILY_FONT, size=int(FONT_SIZE), weight="normal")
        self.FONT_CHAT = CTkFont(
            family=FAMILY_FONT, size=int(FONT_SIZE) + 2, weight="normal"
        )
        self.FONT_BOLD = CTkFont(
            family=FAMILY_FONT, size=int(FONT_BOLD_SIZE), weight="bold"
        )
        self.setup_main_window()

    def run(self):
        """
        Method that runs the application
        """
        self.window.mainloop()

    def check_server_and_update_ui(self):
        """Comprueba el servidor y actualiza la UI."""
        server_available = check_server_availability(HOST, PORT)
        self.server_status_icon.configure(
            image=self.server_on_img if server_available else self.server_off_img
        )
        self.retry_button.configure(state=DISABLED if server_available else NORMAL)

        self.start_button.configure(state=NORMAL if server_available else DISABLED)
        self.stop_button.configure(state=NORMAL if server_available else DISABLED)

        if not server_available:
            self.insert_message(
                "Actualmente no es posible establecer conexión con el Jetson \
                Nano. Por favor, contacta al profesor o al responsable técnico \
                para informar sobre esta situación y recibir asistencia adicional.",
                "PARIS",
                is_user=False,
            )
        else:
            self.insert_message(
                msg="¡Bienvenid@! Soy PARIS, tu asistente de aprendizaje, aquí para ayudarte con \
                retroalimentación útil, responder tus preguntas y guiarte en tu camino educativo. \
                Ya sea que necesites aclarar dudas, buscar consejos o simplemente explorar nuevos \
                conceptos, estoy aquí para apoyarte. Mi objetivo es hacer tu experiencia de aprendizaje \
                lo más enriquecedora y amena posible. No dudes en preguntar lo que necesites, ¡estoy \
                aquí para ayudarte en cada paso de tu viaje educativo!",
                sender="PARIS",
                is_user=False,
            )

    def load_images(self):
        """Cargar todas las imágenes necesarias para la GUI."""
        self.assistant_icon_img = CTkImage(
            light_image=Image.open("resources/images/icon.png"), size=(80, 80)
        )
        self.settings_icon = CTkImage(
            light_image=Image.open("resources/images/settings_icon.png"), size=(20, 20)
        )
        self.help_icon = CTkImage(
            light_image=Image.open("resources/images/help_icon.png"), size=(20, 20)
        )
        self.server_on_img = CTkImage(
            light_image=Image.open("resources/images/bulb_green.png"), size=(30, 30)
        )
        self.server_off_img = CTkImage(
            light_image=Image.open("resources/images/bulb_red.png"), size=(30, 30)
        )

    def setup_left_frame(self, parent):
        left_frame = CTkFrame(parent)
        left_frame.place(relwidth=0.33, relheight=1)

        settings_button = CTkButton(
            left_frame,
            image=self.settings_icon,
            text="Ajustes",
            command=self.open_settings_window,
            font=self.FONT,
        )
        settings_button.place(relwidth=0.4, rely=0.05, relx=0.05)

        help_button = CTkButton(
            left_frame,
            image=self.help_icon,
            text="Ayuda",
            command=self.open_help_window,
            font=self.FONT,
        )
        help_button.place(relwidth=0.4, rely=0.05, relx=0.55)

        self.assistant_icon = CTkLabel(
            left_frame, image=self.assistant_icon_img, text=""
        )
        self.assistant_icon.place(relx=0.25, rely=0.15, relwidth=0.5)

        left_label = CTkLabel(left_frame, text="Toma de datos", font=self.FONT_BOLD)
        left_label.place(relwidth=1, rely=0.35)

        self.entry_name = CTkEntry(
            left_frame, font=self.FONT, placeholder_text="Tu nombre"
        )
        self.entry_name.place(relwidth=0.5, rely=0.45, relx=0.25)

        self.entry_id = CTkEntry(
            left_frame, font=self.FONT, placeholder_text="Tu matrícula"
        )
        self.entry_id.place(relwidth=0.5, rely=0.52, relx=0.25)

        self.start_button = CTkButton(
            left_frame, text="Iniciar", command=self.start_rec, font=self.FONT
        )
        self.start_button.place(relx=0.3, rely=0.65, relwidth=0.35, anchor=CENTER)

        self.stop_button = CTkButton(
            left_frame, text="Parar", command=self.stop_rec, font=self.FONT
        )
        self.stop_button.place(relx=0.7, rely=0.65, relwidth=0.35, anchor=CENTER)

        self.current_section_label = CTkLabel(
            left_frame, text="Sección: 0", font=self.FONT
        )
        self.current_section_label.place(relx=0.05, rely=0.725, relwidth=0.9)

        self.status_label = CTkLabel(
            left_frame, text="Estatus: en espera", font=self.FONT
        )
        self.status_label.place(relwidth=1, rely=0.8)

        self.server_status_icon = CTkLabel(
            left_frame, image=self.server_off_img, text=""
        )
        self.server_status_icon.place(relx=0.8, rely=0.9)

        self.retry_button = CTkButton(
            left_frame,
            text="Reintentar Conexión",
            command=self.check_server_and_update_ui,
            font=self.FONT,
        )
        self.retry_button.place(relx=0.1, rely=0.9)

    def setup_right_frame(self, parent):
        right_frame = CTkFrame(parent)
        right_frame.place(relwidth=0.67, relheight=1, relx=0.33)
        head_label = CTkLabel(right_frame, text="Chat", font=self.FONT_BOLD, pady=10)
        head_label.place(relwidth=1)
        line = CTkLabel(right_frame, width=450, text="")
        line.place(relwidth=1, rely=0.07, relheight=0.012)

        self.text_widget = CTkTextbox(
            right_frame, width=20, height=2, font=self.FONT_CHAT, padx=5, pady=5
        )
        self.text_widget.place(relheight=0.745, relwidth=1, rely=0.08)
        self.text_widget.configure(cursor="arrow", state=DISABLED)

        scrollbar = CTkScrollbar(self.text_widget)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.configure(command=self.text_widget.yview)

        bottom_label = CTkLabel(right_frame, height=80, text="")
        bottom_label.place(relwidth=1, rely=0.825)

        self.msg_entry = CTkEntry(
            bottom_label, font=self.FONT, placeholder_text="Escribe aquí", state=NORMAL
        )
        self.msg_entry.place(relwidth=0.74, relheight=0.8, rely=0.2, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self.on_enter_pressed)

        self.send_button = CTkButton(
            bottom_label,
            text="Enviar",
            font=self.FONT_BOLD,
            width=20,
            command=lambda: self.on_enter_pressed(None),
        )
        self.send_button.place(relx=0.77, rely=0.2, relheight=0.8, relwidth=0.22)

    def setup_main_window(self):
        """
        Window setup
        """
        self.window.title("PARIS")
        self.icon_image = ImageTk.PhotoImage(Image.open("resources/images/icon.ico"))
        self.window.iconbitmap()
        self.window.iconphoto(True, self.icon_image)
        self.window.resizable(width=False, height=False)
        self.window.configure(width=705, height=550)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close_window)

        self.load_images()
        self.setup_left_frame(self.window)
        self.setup_right_frame(self.window)
        self.check_server_and_update_ui()

    def on_close_window(self):
        """Custom close behavior."""
        if not self.is_recording:
            self.window.destroy()

    def on_click(self, x, y, button, pressed):
        global user_id, section_classifier
        if pressed:
            stamp_time, img_array = screenshot_mss()
            img_processed = processing(user_id, img_array, x, y, stamp_time)
            label_int = send_image_array_to_server(
                img_processed, server_address=(HOST, PORT)
            )
            section_classifier.update_label_int(label_int)
            new_section = section_classifier.apply_heuristic_rules()

            if new_section != self.current_section:
                self.section_start_time = time.time()
                self.current_section = new_section
                self.current_section_label.configure(
                    text=f"Sección: {self.current_section}"
                )

                self.soft_threshold_message_shown = False
                self.hard_threshold_message_shown = False

            time_in_current_section = time.time() - self.section_start_time

            time_since_last_click = time.time() - self.last_click_time
            self.last_click_time = time.time()

            self.check_time_thresholds(
                time_in_current_section,
                time_since_last_click,
                label_int,
                self.current_section,
            )

    def check_time_thresholds(
        self, time_in_section, time_between_clicks, label_int, current_section
    ):
        action_soft_threshold = 5
        action_hard_threshold = 9
        section_thresholds = {
            0: [130.0662, 162.8272],
            1: [203.6434, 248.5094],
            2: [823.1206, 1144.3546],
            3: [700.8668, 959.3938],
            4: [1212.4617, 1657.3776],
            5: [11.9538, 287.8172],
        }

        def send_message_if_not_nc(message):
            if message != "NC":
                self.insert_message(message, sender="PARIS", is_user=False)

        if action_soft_threshold <= time_between_clicks < action_hard_threshold:
            message = random.choice(
                [
                    soft_threshold_messages[str(label_int)]["FM1"],
                    soft_threshold_messages[str(label_int)]["FM2"],
                ]
            )
            send_message_if_not_nc(message)
        elif time_between_clicks >= action_hard_threshold:
            message = random.choice(
                [
                    hard_threshold_messages[str(label_int)]["messages"]["FM1"],
                    hard_threshold_messages[str(label_int)]["messages"]["FM2"],
                ]
            )
            send_message_if_not_nc(message)

        soft, hard = section_thresholds[current_section]
        if soft <= time_in_section < hard and not self.soft_threshold_message_shown:
            message = random.choice(
                [
                    section_messages[str(current_section)]["soft_messages"]["SM1"],
                    section_messages[str(current_section)]["soft_messages"]["SM2"],
                ]
            )
            send_message_if_not_nc(message)
            self.soft_threshold_message_shown = True
        elif time_in_section >= hard and not self.hard_threshold_message_shown:
            message = random.choice(
                [
                    section_messages[str(current_section)]["hard_messages"]["HM1"],
                    section_messages[str(current_section)]["hard_messages"]["HM2"],
                ]
            )
            send_message_if_not_nc(message)
            self.hard_threshold_message_shown = True

    def on_enter_pressed(self, event):
        global user_name
        global user_id
        msg = self.msg_entry.get()
        user_name = self.entry_name.get()
        user_id = self.entry_id.get()
        if user_name != "" and user_id != "":
            path_initialization(user_id)
            self.insert_message(msg=msg, sender=user_name)
        else:
            messagebox.showerror("Error", "Introduce tu nombre y matrícula")

    def insert_message(self, msg, sender, is_user=True):
        if not msg:
            return

        if is_user:
            self.msg_entry.delete(0, END)
            user_msg = f"{sender.upper()}: {msg}\n\n"
            self.text_widget.configure(state=NORMAL)
            self.text_widget.insert(
                END,
                format_justified_text(user_msg, LINE_WIDTH, len(user_name) + 2)
                + "\n\n",
            )

        bot_response = (
            get_response(msg, LINE_WIDTH)
            if is_user
            else format_justified_text(msg, LINE_WIDTH)
        )
        bot_msg = f"{'PARIS'}: {bot_response}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, bot_msg)
        self.text_widget.configure(state=DISABLED)

        self.text_widget.see(END)

        self.send_notification("PARIS")

    def start_rec(self):
        """
        Method that starts screen recording.
        """
        global user_name, user_id, section_classifier
        user_id = self.entry_id.get()
        user_name = self.entry_name.get()
        if user_name != "" and user_id != "":
            path_initialization(user_id)
            self.section_start_time = time.time()
            self.last_click_time = self.section_start_time
            section_classifier = SectionClassifier(window_size=10)
            self.listener = mouse.Listener(on_click=self.on_click)
            self.listener.start()
            self.entry_name.configure(state=DISABLED)
            self.entry_id.configure(state=DISABLED)
            self.status_label.configure(text="Estatus: grabando")
            self.is_recording = True
        else:
            messagebox.showerror("Error", "Introduce un usuario")

    def stop_rec(self):
        """
        Method that stops screen recording.
        """
        if user_name != "" and user_id != "":
            self.listener.stop()
            self.status_label.configure(text="Estatus: en espera")
            self.is_recording = False
        else:
            messagebox.showerror("Error", "Introduce un usuario")

    def change_appearance_mode_event(self, appearance_mode: str):
        if appearance_mode == "Claro":
            new_appearance_mode = "light"
        elif appearance_mode == "Oscuro":
            new_appearance_mode = "dark"
        else:
            new_appearance_mode = "system"
        set_appearance_mode(new_appearance_mode)
        self.save_config(new_appearance_mode)

    def open_settings_window(self):
        self.settings_window = CTkToplevel(self.window)
        self.settings_window.title("Configuración Avanzada")
        self.settings_window.configure(width=350, height=450)
        self.settings_window.resizable(width=False, height=False)

        self.config_data = self.load_config()

        self.config_entries = {}
        row_index = 0
        for key, value in self.config_data.items():
            label = CTkLabel(
                self.settings_window,
                text=LABEL_TRANSLATIONS.get(key, key),
                font=self.FONT,
            )
            label.grid(row=row_index, column=0, padx=10, pady=10)

            if key == "APPEARANCE":
                entry = CTkOptionMenu(
                    self.settings_window,
                    values=list(APPEARANCE_OPTIONS.keys()),
                    font=self.FONT,
                    width=150,
                )
                entry.set(next(k for k, v in APPEARANCE_OPTIONS.items() if v == value))
            elif key == "COLOR_THEME":
                entry = CTkOptionMenu(
                    self.settings_window,
                    values=list(COLOR_THEME_OPTIONS.keys()),
                    font=self.FONT,
                    width=150,
                )
                entry.set(next(k for k, v in COLOR_THEME_OPTIONS.items() if v == value))
            elif key == "FAMILY_FONT":
                entry = CTkOptionMenu(
                    self.settings_window,
                    values=FONT_OPTIONS,
                    font=self.FONT,
                    width=150,
                )
                entry.set(value)
            else:
                entry = CTkEntry(self.settings_window, width=150, font=self.FONT)
                entry.insert(0, str(value))

            entry.grid(row=row_index, column=1, padx=10, pady=10)
            self.config_entries[key] = entry
            row_index += 1

        save_button = CTkButton(
            self.settings_window,
            text="Guardar",
            command=self.save_config,
            font=self.FONT,
        )
        save_button.grid(row=row_index, columnspan=2, padx=10, pady=10)

    def open_help_window(self):
        help_window = CTkToplevel(self.window)
        help_window.title("Ayuda y Soporte")
        help_window.configure(width=400, height=300)
        help_window.resizable(width=False, height=False)

        CTkLabel(help_window, text="Consejos", font=self.FONT_BOLD).pack()
        tips_text = (
            "Aquí algunos consejos para mejorar tu experiencia con la aplicación:\n\n"
            "- Revisa bien las preguntas antes de enviarlas para obtener respuestas más precisas.\n"
            "- Utiliza palabras clave relevantes para tu duda o tema de interés.\n"
            "- Experimenta con distintas funcionalidades para descubrir todo lo que la aplicación puede ofrecerte.\n"
        )
        CTkLabel(help_window, text=tips_text, font=self.FONT, justify="left").pack()

        CTkLabel(
            help_window, text="Acerca de la Aplicación", font=self.FONT_BOLD
        ).pack()
        about_text = (
            "Versión: 1.0\n"
            "Desarrollado por Carlos Alberto Bustamante Gaytán.\n"
            "Este asistente está diseñado para facilitar tu aprendizaje y mejorar tu productividad.\n"
        )
        CTkLabel(help_window, text=about_text, font=self.FONT, justify="left").pack()

        CTkLabel(help_window, text="Contacto", font=self.FONT_BOLD).pack()
        contact_text = "Si tienes alguna duda o comentario, puedes escribirme a: contact@charlyfive.com\n"
        CTkLabel(help_window, text=contact_text, font=self.FONT, justify="left").pack()

        CTkLabel(help_window, text="Inicio Rápido", font=self.FONT_BOLD).pack()
        quick_start_text = (
            "Para comenzar a usar la aplicación, simplemente introduce tu nombre y matrícula, y pulsa 'Iniciar'.\n"
            "Si necesitas asistencia o tienes alguna pregunta, utiliza la función de chat.\n"
        )
        CTkLabel(
            help_window, text=quick_start_text, font=self.FONT, justify="left"
        ).pack()

        close_button = CTkButton(
            help_window, text="Cerrar", command=help_window.destroy
        )
        close_button.pack()

    def save_config(self):
        new_config_data = {}
        for key, entry in self.config_entries.items():
            value = entry.get()
            if key == "APPEARANCE":
                new_config_data[key] = APPEARANCE_OPTIONS[value]
            elif key == "COLOR_THEME":
                new_config_data[key] = COLOR_THEME_OPTIONS[value]
            else:
                new_config_data[key] = value

        with open("config/config.json", "w") as file:
            json.dump(new_config_data, file, indent=4)

        self.settings_window.destroy()
        self.apply_new_settings(new_config_data)

    def apply_new_settings(self, new_config_data):
        set_appearance_mode(new_config_data["APPEARANCE"])
        set_default_color_theme(new_config_data["COLOR_THEME"])

    def load_config(self):
        config_path = "config/config.json"
        if not path.exists(config_path):
            messagebox.showerror("Error", "El archivo de configuración no existe.")
            return None

        with open(config_path, "r") as file:
            return json.load(file)

    def send_notification(self, title):
        notification.notify(
            title=title,
            message="Tienes un nuevo mensaje del asistente.",
            app_name="PARIS",
            app_icon="resources/images/icon.ico",
        )


if __name__ == "__main__":
    app = PARISApplication()
    app.run()
