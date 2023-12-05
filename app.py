####################################### Imports #######################################
from utils import *
from network import *
from processor import *
from recorder import *
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
)
from tkinter import CENTER, DISABLED, NORMAL
from pynput import mouse
from plyer import notification


###################################### Main class ######################################
class ChatApplication:
    """
    Class that provides GUI for the project
    """

    def __init__(self) -> None:
        """
        initialized values for the GUI
        """
        self.window = CTk()
        self.FONT = CTkFont(family=FAMILY_FONT, size=int(FONT_SIZE), weight="normal")
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
        self.msg_entry.configure(state=NORMAL if server_available else DISABLED)

        self.retry_button.configure(state=DISABLED if server_available else NORMAL)

        if not server_available:
            self.insert_message(
                "Actualmente no es posible establecer conexión con el Jetson \
                Nano. Por favor, contacta al profesor o al responsable técnico \
                para informar sobre esta situación y recibir asistencia adicional.",
                "Bot",
                is_user=False,
            )
        else:
            self.insert_message(
                msg="¡Bienvenido! Soy tu asistente de aprendizaje, aquí para ayudarte con \
                retroalimentación útil, responder tus preguntas y guiarte en tu camino educativo. \
                Ya sea que necesites aclarar dudas, buscar consejos o simplemente explorar nuevos \
                conceptos, estoy aquí para apoyarte. Mi objetivo es hacer tu experiencia de aprendizaje \
                lo más enriquecedora y amena posible. No dudes en preguntar lo que necesites, ¡estoy \
                aquí para ayudarte en cada paso de tu viaje educativo!",
                sender="Bot",
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

        start_button = CTkButton(
            left_frame, text="Iniciar", command=self.start_rec, font=self.FONT
        )
        start_button.place(relx=0.3, rely=0.65, relwidth=0.35, anchor=CENTER)

        stop_button = CTkButton(
            left_frame, text="Parar", command=self.stop_rec, font=self.FONT
        )
        stop_button.place(relx=0.7, rely=0.65, relwidth=0.35, anchor=CENTER)

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
            right_frame, width=20, height=2, font=self.FONT, padx=5, pady=5
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

        send_button = CTkButton(
            bottom_label,
            text="Enviar",
            font=self.FONT_BOLD,
            width=20,
            command=lambda: self.on_enter_pressed(None),
        )
        send_button.place(relx=0.77, rely=0.2, relheight=0.8, relwidth=0.22)

    def setup_main_window(self):
        """
        Window setup
        """
        self.window.title("NNGUI")
        self.icon_image = ImageTk.PhotoImage(Image.open("resources/images/icon.ico"))
        self.window.iconbitmap()
        self.window.iconphoto(True, self.icon_image)
        self.window.resizable(width=False, height=False)
        self.window.configure(width=705, height=550)

        self.load_images()
        self.setup_left_frame(self.window)
        self.setup_right_frame(self.window)
        self.check_server_and_update_ui()

    def on_click(self, x, y, button, pressed):
        global user_id
        if pressed:
            stamp_time, img_array = screenshot_mss(user_id, x, y)
            img_processed = processing(user_id, img_array, x, y, stamp_time)

    def on_enter_pressed(self, event):
        global user_name
        global user_id
        msg = self.msg_entry.get()
        user_name = self.entry_name.get()
        user_id = self.entry_id.get()
        if user_name != "" and user_id != "":
            self.insert_message(msg=msg, sender=user_name)
        else:
            messagebox.showerror("Error", "Introduce tu nombre y matrícula")

    def insert_message(self, msg, sender, is_user=True):
        if not msg:
            return

        if is_user:
            self.msg_entry.delete(0, END)
            user_msg = f"{sender}: {msg}\n\n"
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
        bot_msg = f"{'Bot'}: {bot_response}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, bot_msg)
        self.text_widget.configure(state=DISABLED)

        self.text_widget.see(END)

        self.send_notification("NNGUI")

    def start_rec(self):
        """
        Method that starts screen recording.
        """
        global user_name
        global user_id
        user_id = self.entry_id.get()
        user_name = self.entry_name.get()
        if user_name != "" and user_id != "":
            self.listener = mouse.Listener(on_click=self.on_click)
            self.listener.start()
            self.entry_name.configure(state=DISABLED)
            self.entry_id.configure(state=DISABLED)
            self.status_label.configure(text="Estatus: grabando")
        else:
            messagebox.showerror("Error", "Introduce un usuario")

    def stop_rec(self):
        """
        Method that stops screen recording.
        """
        if user_name != "" and user_id != "":
            self.listener.stop()
            self.status_label.configure(text="Estatus: en espera")
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
            app_name="NNGUI",
            app_icon="resources/images/icon.ico",
        )


if __name__ == "__main__":
    app = ChatApplication()
    app.run()
