"""
APICredentialsWindow Module

This module provides an Api credentials window for the user to input their Spotify API credentials.
The `ApiCredentialsWindow` class manages the creation and behavior of the window where users enter their credentials,
with added functionalities like context menus for text entry fields, hyperlinking, and credential validation.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser


class ApiCredentialsWindow:
    """
    A class to create a Tkinter window for users to input their Spotify API credentials.
    """
    def __init__(self, root, update_api_credentials):
        """
        Initializes the ApiCredentialsWindow instance.

        Args:
            root (tk.Tk): The root window of the application.
            update_api_credentials (function): A callback function that receives the user's input from the Window.
        """
        self.root = root
        self.update_api_credentials = update_api_credentials
        spotify_green_color = "#1DB954"
        dark_gray_color = "#121212"
        hyperlink_blue_color = "#5d2491"
        hyperlink_purple_color = "#5d2491"
        self.window = tk.Toplevel(root)
        self.window.transient(root)
        self.window.grab_set()
        self.window_style = ttk.Style(self.window)
        self.window.option_add("*tearOff", False)
        self.window.title("Spotify True Shuffle")
        self.window.iconbitmap("assets/icon.ico")
        self.window.geometry("375x320")
        self.window.resizable(None, None)
        self.window.configure(background=dark_gray_color)

        window_width = 375
        window_height = 320
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_position_x = (screen_width // 2) - (window_width // 2)
        window_position_y = (screen_height // 2) - (window_height // 2)
        self.window.geometry(f"{window_width}x{window_height}+{window_position_x}+{window_position_y}")

        enter_api_credentials_label = tk.Label(self.window,
                                               text="Enter your Spotify API credentials!",
                                               font=("Segoe UI", 14, "bold"),
                                               background=dark_gray_color,
                                               foreground=spotify_green_color,
                                               padx=50, pady=20)
        enter_api_credentials_label.pack()

        def on_link_click(event):
            """
            Handles the event when the hyperlink is clicked. The function opens the specified url in the default web browser.

            Args:
                event (tkinter.Event): The event object containing information about the click event.
            """
            webbrowser.open_new("https://github.com/chasstev/SpotifyTrueShuffle/wiki/How-to-Find-Client-ID-and-Client-Secret")
            instructions_label.config(foreground=hyperlink_purple_color)

        def on_enter(event):
            """
           Handles the event when the mouse cursor enters the hyperlink label area. The function changes the cursor to a "hand" cursor.

           Args:
               event (tkinter.Event): The event object containing information about the mouse enter event.
           """
            instructions_label.config(cursor="hand2")

        def on_leave(event):
            """
            Handles the event when the mouse cursor leaves the hyperlink label area. The function resets the cursor to the default.

             Args:
                event (tkinter.Event): The event object containing information about the mouse leave event.
            """
            instructions_label.config(cursor="")

        instructions_label = tk.Label(self.window,
                                      text="Instructions to find Client ID and Client Secret",
                                      font=("Segoe UI", 10, "underline"),
                                      background=dark_gray_color,
                                      foreground=hyperlink_blue_color)
        instructions_label.pack(pady=(0, 5))
        instructions_label.bind("<Button-1>", on_link_click)
        instructions_label.bind("<Enter>", on_enter)
        instructions_label.bind("<Leave>", on_leave)

        client_id_label = tk.Label(self.window, text="Client ID", font=("Segoe UI", 11), background=dark_gray_color)
        client_id_label.pack(pady=(10, 0))
        self.client_id_entry = ttk.Entry(self.window, width=40)
        self.client_id_entry.pack(pady=(0, 10))

        client_secret_label = tk.Label(self.window, text="Client secret:", font=("Segoe UI", 11), background=dark_gray_color)
        client_secret_label.pack(pady=(10, 0))
        self.client_secret_entry = ttk.Entry(self.window, width=40)
        self.client_secret_entry.pack(pady=(0, 10))

        next_button = ttk.Button(self.window, text="Next", style="Accent.TButton", command=self.check_credentials)
        next_button.pack(pady=(15, 0))

        def show_context_menu(event, entry_widget):
            """
            Display a context menu for cut, copy, paste, delete, and select all actions.

            Args:
                event (tk.Event): The event object containing information about the event.
                entry_widget (ttk.Entry): The entry widget to which the context menu is bound.
            """
            context_menu = tk.Menu(self.window, tearoff=0, bd=0, borderwidth=0, activeborderwidth=0, relief="flat")
            context_menu.add_command(label="Cut", command=lambda: cut(entry_widget))
            context_menu.add_command(label="Copy", command=lambda: copy(entry_widget))
            context_menu.add_command(label="Paste", command=lambda: paste(entry_widget))
            context_menu.add_command(label="Delete",command=lambda: delete(entry_widget))
            context_menu.add_separator()
            context_menu.add_command(label="Select All",command=lambda: select_all(entry_widget))
            context_menu.post(event.x_root, event.y_root)

        def cut(entry_widget):
            """
            Cut the selected text from the entry widget and copy it to the clipboard.

            Args:
                entry_widget (ttk.Entry): The entry widget from which to cut text.
            """
            try:
                self.window.clipboard_clear()
                self.window.clipboard_append(entry_widget.selection_get())
                start_index, end_index = entry_widget.index(tk.SEL_FIRST), entry_widget.index(tk.SEL_LAST)
                entry_widget.delete(start_index, end_index)
            except Exception as e:
                pass

        def copy(entry_widget):
            """
            Copy the selected text from the entry widget to the clipboard.

            Args:
                entry_widget (ttk.Entry): The entry widget from which to copy text.
            """
            try:
                self.window.clipboard_clear()
                self.window.clipboard_append(entry_widget.selection_get())
            except Exception as e:
                pass

        def paste(entry_widget):
            """
            Paste text from the clipboard into the entry widget.

            Args:
                entry_widget (ttk.Entry): The entry widget into which to paste text.
            """
            try:
                if entry_widget.selection_present():
                    start_index, end_index = entry_widget.index(tk.SEL_FIRST), entry_widget.index(tk.SEL_LAST)
                    entry_widget.delete(start_index, end_index)
                entry_widget.insert(tk.INSERT, self.window.clipboard_get())
            except Exception as e:
                pass

        def delete(entry_widget):
            """
            Delete the selected text from the entry widget.

            Args:
                entry_widget (ttk.Entry): The entry widget from which to delete text.
            """
            try:
                start_index, end_index = entry_widget.index(tk.SEL_FIRST), entry_widget.index(tk.SEL_LAST)
                entry_widget.delete(start_index, end_index)
            except Exception as e:
                pass

        def select_all(entry_widget):
            """
            Select all text in the entry widget.

            Args:
                entry_widget (ttk.Entry): The entry widget in which to select all text.
            """
            try:
                entry_widget.select_range(0, 'end')
            except Exception as e:
                pass

        self.client_id_entry.bind("<Button-3>", lambda event: show_context_menu(event, self.client_id_entry))
        self.client_secret_entry.bind("<Button-3>", lambda event: show_context_menu(event, self.client_secret_entry))

        self.load_api_credentials_from_file()

        self.window.mainloop()

    def load_api_credentials_from_file(self):
        """
        Loads the Spotify API credentials from a configuration file (config.conf).
        """
        try:
            config_file_path = "config.conf"
            with open(config_file_path, 'r') as file:
                client_id = file.readline().strip()
                client_secret = file.readline().strip()
                if len(client_id) == 32 and len(client_secret) == 32:
                    self.client_id_entry.insert(0, client_id)
                    self.client_secret_entry.insert(0, client_secret)
        except Exception as e:
            print(f"Error loading client ID from file: {e}")

    def check_credentials(self):
        """
        Validates the format of the entered API credentials.
        """
        if len(self.client_id_entry.get()) == 32 and len(self.client_secret_entry.get()) == 32:
            self.get_credentials()
        else:
            messagebox.showerror("Invalid Credentials", "Credentials are invalid. Try again!")

    def get_credentials(self):
        """
        Saves the entered API credentials to a configuration file and updates the credentials via a callback.
        """
        config_file_path = "config.conf"
        get_client_id = self.client_id_entry.get()
        get_client_secret = self.client_secret_entry.get()
        with open(config_file_path, 'w') as file:
            file.write(f"{get_client_id}\n{get_client_secret}\n")
        self.update_api_credentials(get_client_id, get_client_secret, self.destroy_window)

    def destroy_window(self):
        """
        Destroys the main window, called after the user presses the next button.
        """
        self.window.destroy()