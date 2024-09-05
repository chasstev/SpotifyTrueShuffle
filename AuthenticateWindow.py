"""
AuthenticateWindow Module

This module provides an authenticate window for the user to authenticate with spotify.
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class AuthenticateWindow:
    """
    A class to create and manage a Spotify authentication window.
    """
    def __init__(self, authenticate):
        """
        Initializes the AuthenticateWindow instance, sets up the window, styles, and widgets.

        Args:
            authenticate (function): A callback function that is invoked when the "Login with Spotify" button is clicked.
        """
        self.authenticate = authenticate
        spotify_green_color = "#1DB954"
        dark_gray_color = "#121212"
        self.window = tk.Tk()
        self.window_style = ttk.Style(self.window)
        self.window.tk.call("source", "forest-dark.tcl")
        self.window_style.theme_use("forest-dark")
        self.window.option_add("*tearOff", False)
        self.window.title("Spotify True Shuffle")
        self.window.iconbitmap("assets/icon.ico")
        self.window.geometry("275x125")
        self.window.resizable(None,None)
        self.window.configure(background=dark_gray_color)

        window_width = 275
        window_height = 125
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_position_x = (screen_width // 2) - (window_width // 2)
        window_position_y = (screen_height // 2) - (window_height // 2)
        self.window.geometry(f"{window_width}x{window_height}+{window_position_x}+{window_position_y}")

        auth_to_spotify_label = tk.Label(self.window,
                               text="Authenticate to Spotify!",
                               font=("Segoe UI", 12, "bold"),
                               background=dark_gray_color,
                               foreground=spotify_green_color,
                               padx=50, pady=10)
        auth_to_spotify_label.pack()

        spotify_logo_image = Image.open('assets/white_spotify_icon.png')
        spotify_logo_image.thumbnail((20, 20))  # Adjust the size as needed
        spotify_logo_photo = ImageTk.PhotoImage(spotify_logo_image, master=self.window)
        next_button = ttk.Button(self.window,
                                 text=" Login with Spotify",
                                 style="Accent.TButton",
                                 command=lambda: authenticate(self),
                                 image=spotify_logo_photo,
                                 compound="left")
        next_button.pack(pady=20)

        self.window.mainloop()

    def destroy_window(self):
        """
        Destroys the main window, called after the authentication process is complete.
        """
        self.window.destroy()