from utils import *


class ChatApplication:
    """
    Class that provides GUI for the project
    """

    def __init__(self) -> None:
        """
        initialized values for the GUI
        """
        self.window = CTk()
        self.FONT = CTkFont(family=FAMILY_FONT,
                            size=int(FONT_SIZE),
                            weight='normal')
        self.FONT_BOLD = CTkFont(family=FAMILY_FONT,
                                 size=int(FONT_BOLD_SIZE),
                                 weight='bold')
        self.setup_main_window()

    def run(self):
        """
        Method that runs the application
        """
        self.window.mainloop()

    def setup_main_window(self):
        """
        Window setup
        """
        self.window.title("NNGUI")
        self.window.resizable(width=False,
                              height=False)
        self.window.configure(width=705,
                              height=550)

        left_frame = CTkFrame(self.window)
        left_frame.place(relwidth=0.33,
                         relheight=1)

        left_label = CTkLabel(left_frame,
                              text="Toma de datos",
                              font=self.FONT_BOLD)
        left_label.place(relwidth=1, rely=0.1)

        self.entry_name = CTkEntry(left_frame,
                                   font=self.FONT,
                                   placeholder_text="Tu nombre")
        self.entry_name.place(relwidth=0.5,
                              rely=0.25,
                              relx=0.25)

        start_button = CTkButton(left_frame,
                                 text="Iniciar",
                                 command=self.start_rec)
        start_button.place(relx=0.5,
                           rely=0.45,
                           anchor=CENTER)

        stop_button = CTkButton(left_frame,
                                text="Parar",
                                command=self.stop_rec)
        stop_button.place(relx=0.5,
                          rely=0.55,
                          anchor=CENTER)

        self.status_label = CTkLabel(left_frame,
                                     text="Estatus: en espera")
        self.status_label.place(relwidth=0.5,
                                relx=0.25,
                                rely=0.75)

        right_frame = CTkFrame(self.window)
        right_frame.place(relwidth=0.67,
                          relheight=1,
                          relx=0.33)

        head_label = CTkLabel(right_frame,
                              text="Chat",
                              font=self.FONT_BOLD,
                              pady=10)
        head_label.place(relwidth=1)
        line = CTkLabel(right_frame,
                        width=450,
                        text="")
        line.place(relwidth=1,
                   rely=0.07,
                   relheight=0.012)

        self.text_widget = CTkTextbox(right_frame,
                                      width=20,
                                      height=2,
                                      font=self.FONT,
                                      padx=5,
                                      pady=5)
        self.text_widget.place(relheight=0.745,
                               relwidth=1,
                               rely=0.08)
        self.text_widget.configure(cursor="arrow",
                                   state=DISABLED)

        scrollbar = CTkScrollbar(self.text_widget)
        scrollbar.place(relheight=1,
                        relx=0.974)
        scrollbar.configure(command=self.text_widget.yview)

        bottom_label = CTkLabel(right_frame,
                                height=80,
                                text="")
        bottom_label.place(relwidth=1,
                           rely=0.825)

        self.msg_entry = CTkEntry(bottom_label,
                                  font=self.FONT,
                                  placeholder_text="Escribe aquí",
                                  state=NORMAL if CHATBOT_STATUS.lower() == 'normal' else DISABLED)
        self.msg_entry.place(relwidth=0.74,
                             relheight=0.8,
                             rely=0.2,
                             relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>",
                            self.on_enter_pressed)

        send_button = CTkButton(bottom_label,
                                text="Enviar",
                                font=self.FONT_BOLD,
                                width=20,
                                command=lambda: self.on_enter_pressed(None))
        send_button.place(relx=0.77,
                          rely=0.2,
                          relheight=0.8,
                          relwidth=0.22)

    def on_click(self, x, y, button, pressed):
        if pressed:
            screenshot_mss(user_name,
                           x,
                           y)

    def on_enter_pressed(self, event):
        msg = self.msg_entry.get()
        user_name = self.entry_name.get()
        if user_name == "":
            messagebox.showerror("Error", "Introduce un usuario")
        else:
            self.insert_message(msg, user_name)

    def insert_message(self, msg, sender):
        if not msg:
            return

        self.msg_entry.delete(0, END)
        msg1 = f"{sender}: {msg}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg1)
        self.text_widget.configure(state=DISABLED)

        msg2 = f"{'Bot'}: {get_response(msg)}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg2)
        self.text_widget.configure(state=DISABLED)

        self.text_widget.see(END)

    def schedule_check(self, t):
        """
        Recursive method for the check_if_done method
        """
        self.window.after(500, self.check_if_done, t)

    def check_if_done(self, t):
        """
        Method that checks every 500ms if processing is done.
        """
        if not t.is_alive():
            if CLASSIFIER_STATUS.lower() == 'normal':
                self.status_label.configure(text="Estatus: analizando")
                self.classify()
            self.status_label.configure(text="Estatus: en espera")
            self.entry_name.configure(state=NORMAL)
        else:
            self.schedule_check(t)

    def process_im(self):
        """
        Method that process all images in the user directory.
        """
        for image_stamp in os.listdir(path_to_prog /
                                      "NNGUI" /
                                      f"{user_name}" /
                                      f"{today}" /
                                      "Full"):
            data_splitted = image_stamp.split()
            processing(user_name,
                       image_stamp,
                       data_splitted[0],
                       data_splitted[1],
                       data_splitted[2])

    def start_rec(self):
        """
        Method that starts screen recording.
        """
        global user_name
        user_name = self.entry_name.get()
        if user_name != "":
            self.listener = mouse.Listener(on_click=self.on_click)
            self.listener.start()
            self.entry_name.configure(state=DISABLED)
            self.status_label.configure(text="Estatus: grabando")
        else:
            messagebox.showerror("Error", "Introduce un usuario")

    def stop_rec(self):
        """
        Method that stops screen recording.
        """
        if user_name != "":
            self.listener.stop()
            self.status_label.configure(text="Estatus: procesando")
            th_processing = Thread(target=self.process_im)
            th_processing.start()
            self.schedule_check(th_processing)
        else:
            messagebox.showerror("Error", "Introduce un usuario")


if __name__ == "__main__":
    app = ChatApplication()
    app.run()
