import os
import glob
import pygame
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import random
from threading import Thread

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

class CircularDoublyLinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.head.next = self.head
            self.head.prev = self.head
        else:
            tail = self.head.prev
            tail.next = new_node
            new_node.prev = tail
            new_node.next = self.head
            self.head.prev = new_node

    def traverse(self, direction=1):
        current = self.head
        while True:
            yield current.data
            current = current.next if direction > 0 else current.prev
            if current == self.head:
                break

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("800x600")
        self.root.configure(bg='#3b3b3b')

        pygame.mixer.init()

        self.playlist = CircularDoublyLinkedList()
        self.current_song = None
        self.is_playing = False
        self.is_paused = False

        self.create_widgets()
        self.load_all_audio_files()
        self.update_equalizer()

    def create_widgets(self):
        self.song_label = tk.Label(self.root, text="No song loaded", font=("Helvetica", 12), bg='#3b3b3b', fg='white')
        self.song_label.pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=300, height=100, bg='black')
        self.canvas.pack(pady=10)

        self.playlist_frame = tk.Frame(self.root, bg='#3b3b3b')
        self.playlist_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.playlist_box = tk.Listbox(self.playlist_frame, bg='#3b3b3b', fg='white', selectbackground='gray', activestyle='none', highlightthickness=0, bd=0, relief='flat')
        self.playlist_box.pack(pady=10, fill=tk.BOTH, expand=True)
        self.playlist_box.bind('<Double-1>', self.play_selected_song)

        self.control_frame = tk.Frame(self.root, bg='#3b3b3b')
        self.control_frame.pack(pady=20, side=tk.BOTTOM)

        self.btn_prev = tk.Button(self.control_frame, text="Prev", command=lambda: self.next_prev_song(-1), bg='#3b3b3b', fg='white')
        self.btn_prev.grid(row=0, column=0, padx=5)

        self.btn_back_10 = tk.Button(self.control_frame, text="<< 10 sec", command=self.back_10_sec, bg='#3b3b3b', fg='white')
        self.btn_back_10.grid(row=0, column=1, padx=5)

        self.btn_play_pause = tk.Button(self.control_frame, text="Play", command=self.play_pause, bg='#3b3b3b', fg='white')
        self.btn_play_pause.grid(row=0, column=2, padx=5)

        self.btn_stop = tk.Button(self.control_frame, text="Stop", command=self.stop, bg='#3b3b3b', fg='white')
        self.btn_stop.grid(row=0, column=3, padx=5)

        self.btn_skip_10 = tk.Button(self.control_frame, text="10 sec >>", command=self.skip_10_sec, bg='#3b3b3b', fg='white')
        self.btn_skip_10.grid(row=0, column=4, padx=5)

        self.btn_next = tk.Button(self.control_frame, text="Next", command=lambda: self.next_prev_song(1), bg='#3b3b3b', fg='white')
        self.btn_next.grid(row=0, column=5, padx=5)

    def load_all_audio_files(self):
        thread = Thread(target=self.load_files_thread)
        thread.start()

    def load_files_thread(self):
        extensions = ['*.mp3', '*.wav', '*.ogg']
        directories = [os.path.expanduser('~'), 'C:\\', 'D:\\']
        for directory in directories:
            for ext in extensions:
                files = glob.glob(os.path.join(directory, '**', ext), recursive=True)
                for file in files:
                    self.playlist.append(file)
                    self.playlist_box.insert(tk.END, os.path.basename(file))
        if not self.current_song and self.playlist.head:
            self.current_song = self.playlist.head
            self.update_song_label()
        messagebox.showinfo("Playlist Loaded", "All audio files loaded successfully!")

    def update_song_label(self):
        song_name = os.path.basename(self.current_song.data)
        self.song_label.config(text=song_name)

    def play_pause(self):
        if not self.current_song:
            return
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.btn_play_pause.config(text="Pause")
            self.is_paused = False
        elif self.is_playing:
            pygame.mixer.music.pause()
            self.btn_play_pause.config(text="Play")
            self.is_paused = True
        else:
            pygame.mixer.music.load(self.current_song.data)
            pygame.mixer.music.play()
            self.is_playing = True
            self.btn_play_pause.config(text="Pause")
            self.update_song_label()

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.btn_play_pause.config(text="Play")
        self.canvas.delete("all")

    def next_prev_song(self, direction):
        if not self.current_song:
            return
        self.stop()
        self.current_song = self.current_song.next if direction > 0 else self.current_song.prev
        self.play_pause()

    def skip_10_sec(self):
        if not self.current_song:
            return
        current_pos = pygame.mixer.music.get_pos() / 1000
        pygame.mixer.music.play(start=current_pos + 10)

    def back_10_sec(self):
        if not self.current_song:
            return
        current_pos = pygame.mixer.music.get_pos() / 1000
        pygame.mixer.music.play(start=max(0, current_pos - 10))

    def play_selected_song(self, event):
        selection = self.playlist_box.curselection()
        if selection:
            index = selection[0]
            current_node = self.playlist.head
            for _ in range(index):
                current_node = current_node.next
            self.current_song = current_node
            self.stop()
            self.play_pause()

    def update_equalizer(self):
        if self.is_playing and not self.is_paused:
            self.canvas.delete("all")
            for i in range(10):
                height = random.randint(1, 100)
                self.canvas.create_rectangle(i * 30, 100, i * 30 + 20, 100 - height, fill=random.choice(["green", "red", "blue", "yellow"]))
        else:
            self.canvas.delete("all")
        self.root.after(500, self.update_equalizer)

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
