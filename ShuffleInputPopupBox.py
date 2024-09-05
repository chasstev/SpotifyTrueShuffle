"""
ShuffleInputPopupBox Module

This module creates a popup window using Tkinter to receive input for the number of songs to shuffle.
"""
import tkinter as tk
from tkinter import ttk, messagebox


class ShuffleInputPopupBox:
    """
    A class to create a popup window for user input regarding the number of songs to shuffle from a playlist.
    """
    def __init__(self, root, receive_input_popupbox):
        """
        Initialize the ShuffleInputPopupBox.

        Args:
            root (tk.Tk): The root window of the application.
            receive_input_popupbox (function): A callback function that receives the user's input from the popup box.
        """
        self.root = root
        self.receive_input_popupbox = receive_input_popupbox
        spotify_green_color = "#1DB954"
        dark_gray_color = "#121212"
        self.window = tk.Toplevel(root)
        self.window.transient(root)
        self.window.grab_set()
        self.window.option_add("*tearOff", False)
        self.window.title("# of songs")
        self.window.iconbitmap("assets/icon.ico")
        self.window.geometry("275x150")
        self.window.resizable(None,None)
        self.window.configure(background=dark_gray_color)
        self.window.focus_set()

        window_width = 275
        window_height = 150
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_position_x = (screen_width // 2) - (window_width // 2)
        window_position_y = (screen_height // 2) - (window_height // 2)
        self.window.geometry(f"{window_width}x{window_height}+{window_position_x}+{window_position_y}")

        auth_to_spotify_label = tk.Label(self.window,
                               text="Select how many songs you want \nto shuffle from the playlist.",
                               font=("Segoe UI", 8, "bold"),
                               background=dark_gray_color,
                               foreground=spotify_green_color,
                               pady=10)
        auth_to_spotify_label.pack()

        self.song_shuffle_entry = ttk.Entry(self.window, width=15)
        self.song_shuffle_entry.pack(pady=10)

        ok_button = ttk.Button(self.window, text="Ok", style="Accent.TButton", command=self.get_input_popupbox, width=15)
        ok_button.pack(pady=10)


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

        self.song_shuffle_entry.bind("<Button-3>", lambda event: show_context_menu(event, self.song_shuffle_entry))

        self.window.mainloop()

    def get_input_popupbox(self):
        """
        Get the user's input from the popup box, validate it, and pass it to the callback function.
        """
        try:
            get_song_shuffle_amount = int(self.song_shuffle_entry.get())
            if get_song_shuffle_amount is None:
                messagebox.showerror("Invalid Input", "Please enter a number into the text box")
                self.window.focus_force()
            elif get_song_shuffle_amount <= 0:
                messagebox.showerror("Invalid Input", "Please enter a number greater than 0 into the text box.")
                self.window.focus_force()
            elif get_song_shuffle_amount > 25:
                messagebox.showerror("Invalid Input", "Please enter a number less than 25 into the text box.")
                self.window.focus_force()
            else:
                self.receive_input_popupbox(get_song_shuffle_amount)
                print(get_song_shuffle_amount)
                self.window.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a number into the text box")
            self.window.focus_force()

    def destroy_window(self):
        """
        Destroys the main window, called after the user presses the ok button.
        """
        self.window.destroy()