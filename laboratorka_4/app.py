import customtkinter as ctk

import matrix_maker

class App:
    def __init__(self):
        self._main_window = ctk.CTk()
        self._main_window.title("PotatoSudoku")
        screen_width = self._main_window.winfo_screenwidth()
        win_width = int(screen_width * 0.25)
        win_height = int(win_width * 5 / 4)
        self._main_window.geometry(f"{win_width}x{win_height}")
        self._main_window.resizable(False, False)
        self.seek_offset = 0
        self.create_interface()


    def clear_window(self):
        for widget in self._main_window.winfo_children():
            widget.destroy()


    def slider_settings(self, text, from_, command, set_value):
        frame = ctk.CTkFrame(self._main_window, fg_color="transparent")
        frame.pack(pady=10)
        ctk.CTkLabel(frame, text=text, font=("Arial", 30)).pack(side="left", padx=5)
        slider = ctk.CTkSlider(frame, from_=from_, to=1, command=command)
        slider.set(set_value)
        slider.pack(pady=10)
        return slider


    def get_settings_menu(self):
        settings_menu = SettingsMenu(self)
        settings_menu.run()


    def create_interface(self):
        menu_frame = ctk.CTkFrame(self._main_window, fg_color="transparent")
        menu_frame.place(relx=0.5, rely=0.5, anchor="center")


        ctk.CTkLabel(menu_frame, text="Потато Судоку", font=("Arial", 14)).pack(pady=5)
        ctk.CTkLabel(menu_frame, text="Выберите уровень сложности").pack(pady=5)


        button_frame = ctk.CTkFrame(menu_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        levels = {
            "Легко": 1,
            "Средне": 2,
            "Тяжко": 3,
            "Курсовой": 4
        }
        
        for level_text in levels:
            ctk.CTkButton(
                button_frame,
                text=level_text,
                width=80,
                height=30,
                fg_color="transparent",
                command=lambda l=level_text: self.start_game(levels[l])
            ).pack(side="left", padx=10)


        self.settings_button = ctk.CTkButton(
            self._main_window,
            text="☭",
            width=40,
            height=20,
            corner_radius=20,
            font=("Arial", 25),
            fg_color="transparent",
            command=self.get_settings_menu
        )
        self.settings_button.place(relx=1.0, rely=0.0, anchor="ne")


    def start_game(self, level):
        self.clear_window()
        sudoku = matrix_maker.Sudoku(level)
        sudoku.create_sudoku()
        grid = sudoku.get_grid()

        menu_frame = ctk.CTkFrame(self._main_window, fg_color="transparent")
        menu_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.cells = []

        for r, row in enumerate(grid):
            for c, num in enumerate(row):
                if num != 0:
                    cell = ctk.CTkLabel(
                        menu_frame,
                        text=str(num),
                        width=30,
                        height=30,
                        font=("Arial", 14),
                        fg_color="grey",
                        corner_radius=5
                    )
                else:
                    cell = ctk.CTkEntry(
                        menu_frame,
                        width=30,
                        height=30,
                        font=("Arial", 14),
                        fg_color="grey",
                        corner_radius=5
                    )
                cell.grid(row=r, column=c, padx=2, pady=2)
                self.cells.append(cell)

        for i in range(9):
            menu_frame.grid_columnconfigure(i, weight=1, uniform="equal")
            menu_frame.grid_rowconfigure(i, weight=1, uniform="equal")

        check_button = ctk.CTkButton(
            menu_frame,
            text="Проверить",
            width=80,
            height=30,
            fg_color="transparent",
            command=self.get_user_grid
        )
        check_button.grid(row=9, column=0, columnspan=9, pady=10)


        
    def get_user_grid(self):
        user_grid = []
        for i, widget in enumerate(self.cells):
            row, col = divmod(i, 9)
            if col == 0:
                user_grid.append([])

            if isinstance(widget, ctk.CTkEntry):
                val = widget.get()
                user_grid[row].append(int(val) if val.isdigit() else 0)
            else:
                user_grid[row].append(int(widget.cget("text")))
        print(user_grid)
        return user_grid






    def run(self):
        self._main_window.mainloop()




class SettingsMenu:
    def __init__(self, app: App):
        self.app = app
        self._main_window = ctk.CTk()
        self._main_window.title("PotatoPlayer/Settings")

        screen_width = self._main_window.winfo_screenwidth()
        settings_width = int(screen_width * 0.2)
        settings_height = int(settings_width * 2 / 8)

        x = app._main_window.winfo_x()
        y = app._main_window.winfo_y()
        w = app._main_window.winfo_width()
        self._main_window.geometry(f"{settings_width}x{settings_height}+{x + w}+{y}")
        self._main_window.resizable(False, False)

        self.opacity_slider = self.slider_settings(
            text='🌓',
            from_=0.3,
            command=self.set_opacity,
            set_value=1
        )

    def set_opacity(self, value):
        self.app._main_window.attributes("-alpha", value)
        self._main_window.attributes("-alpha", value)    


    def slider_settings(self, text, from_, command, set_value):
        frame = ctk.CTkFrame(self._main_window, fg_color="transparent")
        frame.pack(pady=10)
        ctk.CTkLabel(frame, text=text, font=("Arial", 30)).pack(side="left", padx=5)
        slider = ctk.CTkSlider(frame, from_=from_, to=1, command=command)
        slider.set(set_value)
        slider.pack(pady=10)
        return slider   


    def run(self):
        self._main_window.mainloop()