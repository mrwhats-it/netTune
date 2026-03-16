import os

MUSIC_FOLDER = "../music"

def get_all_songs():
    return [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(".mp3")]

def song_exists(song_name):
    return song_name in get_all_songs()

def get_song_path(song_name):
    return os.path.join(MUSIC_FOLDER, song_name)

def get_song_size(song_name):
    path = get_song_path(song_name)
    return os.path.getsize(path)
