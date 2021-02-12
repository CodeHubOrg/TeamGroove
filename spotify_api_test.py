# 	Get a List of Current User's Playlists
#  	Get a Playlist/ Get a Playlist Cover Image
#   Get a Playlist's Items
#	Reorder a Playlist's Items
import requests
import json


def get_playlists():
    # token needed here
    endpoint = "https://api.spotify.com/v1/me/playlists"
    headers = {'Authorization': 'Bearer {token}'.format(token=token)}

    r = requests.get(
        endpoint,
        headers=headers
    )
    playlists = r.json()
    return playlists


def get_playlist_names():
    playlists = get_playlists()
    for num, playlist in enumerate(playlists['items']):
        print(num, playlist['name'])


def get_playlist_id(user_choice):
    playlists = get_playlists()
    playlist = playlists['items'][int(user_choice)]
    print(playlist)
    # print(f"playlist id {playlist['id']}")
    print(f"Chosen playlist = {playlist['name']}")


get_playlist_names()
get_playlist_id(input("Choose number"))
