"""
SpotifyTrueShuffle Module

This module implements a Tkinter-based GUI application that allows users to shuffle songs in a selected playlist.
"""
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import requests
import webbrowser
import io
import queue
import threading
import concurrent
from concurrent.futures import ThreadPoolExecutor
from FlaskServer import run_flask, update_api_credentials, clear_user_token
from AuthenticateWindow import AuthenticateWindow
from ShuffleInputPopupBox import ShuffleInputPopupBox
from ApiCredentialsWindow import ApiCredentialsWindow


FLASK_SERVER_URL = "http://127.0.0.1:5000"
playlists = []
image_queue = queue.Queue()
song_shuffle_amount = 0
shuffling_active = False
currently_shuffling_playlist = None


def start_flask_server():
    """
    Starts the Flask server in a separate thread and opens the API credentials input window.
    """
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    api_credentials_popupbox()


def authenticate(authenticate_window):
    """
    Opens the Spotify authentication URL and checks the authentication status.

     Args:
        authenticate_window (AuthenticateWindow): The window object that handles the authentication process.
    """
    webbrowser.open(f"{FLASK_SERVER_URL}/")
    root.after(3000, lambda: check_authentication(authenticate_window))


def authenticate_popupbox():
    """
    Displays the authentication popup window.
    """
    AuthenticateWindow(authenticate)


def check_authentication(authenticate_window):
    """
    Periodically checks if the user has successfully authenticated with Spotify.

    Args:
        authenticate_window (AuthenticateWindow): The window object that handles the authentication process.
    """
    try:
        response = requests.get(f"{FLASK_SERVER_URL}/check_authentication")
        auth_data = response.json()
        if response.status_code == 200 and auth_data.get("success"):
            root.deiconify()
            authenticate_window.destroy_window()
            root.after(2000, get_playlists)
        elif response.status_code is None or auth_data.get("success") is None:
            root.after(3000, check_authentication(authenticate_window))
        else:
            messagebox.showerror("Authentication Error", "Failed to authenticate to Spotify. Try again!")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Authentication Error", f"Failed to check authentication, please check to make sure that flask server is running properly: {e}")


def receive_api_credentials(client_id, client_secret, destroy_api_credentials_window):
    """
    Receives and updates the API credentials, then initiates the authentication process.

    Args:
        client_id (str): The Spotify API client ID.
        client_secret (str): The Spotify API client secret.
        destroy_api_credentials_window (function): The function to close the API credentials window.
    """
    clear_user_token()
    clear_user_token()
    destroy_api_credentials_window()
    update_api_credentials(client_id, client_secret)
    authenticate_popupbox()


def api_credentials_popupbox():
    """
    Displays the API credentials input window.
    """
    ApiCredentialsWindow(root, receive_api_credentials)


def fetch_playlist_images(playlist):
    """
    Fetches the cover images of playlists and resizes them for display.

    Args:
        playlist (dict): A dictionary containing playlist details, including the image URL.
    """
    try:
        if playlist["images"]:
            image_url = playlist["images"][0]["url"]
            image_response = requests.get(image_url)
            image_data = image_response.content
            image = Image.open(io.BytesIO(image_data))
            image.thumbnail((100, 100))
            image_queue.put((playlist["id"], image))
        else:
            image_queue.put((playlist["id"], None))
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        image_queue.put((playlist["id"], None))
    except Exception as e:
        print(f"Error processing image for playlist {playlist['id']}: {e}")
        image_queue.put((playlist["id"], None))


def get_playlists():
    """
    Retrieves the user's Spotify playlists and updates the Treeview widget with playlist names and images.
    """
    global playlists
    try:
        response = requests.get(f"{FLASK_SERVER_URL}/playlists")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Request Error", f"Failed to fetch playlists, Try again!: {e}")
        return
    try:
        playlists = response.json()
    except ValueError as e:
        messagebox.showerror("Playlist JSON Error", f"Failed to parse playlist JSON response, Try Again!: {e}")
        return

    for i in tree.get_children():
        tree.delete(i)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for playlist in playlists:
            tree.insert("", "end", iid=playlist["id"], text="            " + playlist["name"])
            futures.append(executor.submit(fetch_playlist_images, playlist))
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                messagebox.showerror("Image Fetch Error", f"Failed to fetch playlist images: {e}")
    root.after(100, update_treeview)


def update_treeview():
    """
    Updates the Treeview widget with the playlist images.
    """
    try:
        while not image_queue.empty():
            playlist_id, image = image_queue.get_nowait()
            if image:
                if image.width != image.height:
                    image_width, image_height = image.size
                    image_size = min(image_width, image_height)
                    image_left = (image_width - image_size) // 2
                    image_top = (image_height - image_size) // 2
                    image_right = (image_width + image_size) // 2
                    image_bottom = (image_height + image_size) // 2
                    image_cropped = image.crop((image_left, image_top, image_right, image_bottom))
                    new_image_size = (100, 100)
                    photo_final = image_cropped.resize(new_image_size, Image.Resampling.LANCZOS)
                else:
                    photo_final = image
                photo = ImageTk.PhotoImage(photo_final)

                tree.item(playlist_id, image=photo)
                # Keep a reference to the image to avoid garbage collection
                tree.images[playlist_id] = photo
    except queue.Empty:
        pass


def shuffle_playlist():
    """
    Shuffles songs in the selected playlist by adding random songs to the queue.
    """
    global currently_shuffling_playlist
    for item in tree.get_children():
        if item == currently_shuffling_playlist:
            tree.item(currently_shuffling_playlist, values=("",))

    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a playlist.")
        return
    playlist_id = selected_item[0]
    currently_shuffling_playlist = playlist_id
    for i in range(song_shuffle_amount):
        try:
            shuffle_playlist_response = requests.post(f"{FLASK_SERVER_URL}/add_random_song_to_queue/{playlist_id}")
            shuffle_playlist_response.raise_for_status()
        except requests.exceptions.RequestException:
            messagebox.showerror("Shuffle Error", f"Failed to shuffle playlist, try unpausing and pausing a song on spotify then try again!")
            return
    if not shuffling_active:
        for item in tree.get_children():
            if item == currently_shuffling_playlist:
                tree.item(currently_shuffling_playlist, values=("Last Shuffled..",))
        skip_to_next_song()
        messagebox.showinfo("Success", "Playlist shuffled Successfully!")


def skip_to_next_song(): #REMOVED TRUE AND FALSE RETURN STATMENTS
    """
    Skips to the next song in the Spotify queue.
    """
    try:
        response = requests.post(f"{FLASK_SERVER_URL}/skip_to_next_song")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to skip to next song: {e}")


def receive_input_popupbox(get_song_shuffle_amount):
    """
    Receives the number of songs to shuffle and starts the shuffle process.

    Args:
        get_song_shuffle_amount (int): The number of songs to be shuffled.
    """
    global song_shuffle_amount
    song_shuffle_amount = get_song_shuffle_amount
    shuffle_playlist()


def shuffle_button_action():
    """
    Displays the input box to receive the number of songs to shuffle.
    """
    ShuffleInputPopupBox(root, receive_input_popupbox)


root = tk.Tk()
root.withdraw()
style = ttk.Style(root)
root.tk.call("source", "forest-dark.tcl")
style.theme_use("forest-dark")
root.option_add("*tearOff", False)
root.title("Spotify True Shuffle")
root.iconbitmap("assets/icon.ico")
root.resizable(None,None)
spotify_green_color = "#1DB954"
dark_Gray_color = "#121212"
root.configure(background = dark_Gray_color)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 900
window_height = 650
position_x = (screen_width // 2) - (window_width // 2)
position_y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")


title_label = tk.Label(root,
                       text="Spotify True Shuffle",
                       font=("Segoe UI", 25, "bold"),
                       fg=spotify_green_color,
                       background=dark_Gray_color)
title_label.pack(pady=5)

style.configure("Treeview",
                rowheight=150,
                font=("Segoe UI", 20),
                background=dark_Gray_color,
                bordercolor=dark_Gray_color)

tree_frame = ttk.Frame(root, width=895,height=460)
tree_frame.pack_propagate(0)
tree_frame.place(x=0, y=110)

tree = ttk.Treeview(tree_frame, show="tree", columns=("Shuffling",))
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
tree.column("#0", width=675, stretch=tk.NO)
tree.column("Shuffling", width=170, stretch=tk.NO)

tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=tree_scroll.set)

# Initialize the images attribute to avoid garbage collection
tree.images = {}

change_api_credentials_button = ttk.Button(root, text="  Change Api  \n  Credentials  ", style="Accent.TButton", command=api_credentials_popupbox)
change_api_credentials_button.place(x=10 ,y=10)

reauthenticate_button = ttk.Button(root, text="Re-Authenticate\n     to Spotify", style="Accent.TButton", command=authenticate_popupbox)
reauthenticate_button.place(x=775 ,y=10)

shuffle_playlist_button = ttk.Button(root, text="Shuffle\nPlaylist", style="Accent.TButton", width=15, command=shuffle_button_action)
shuffle_playlist_button.place(x=385 ,y=585)

refresh_playlists_button = ttk.Button(root, text=" Refresh Playlists ", style="Accent.TButton", command=get_playlists)
refresh_playlists_button.place(x=385 ,y=65)


start_flask_server()
root.mainloop()