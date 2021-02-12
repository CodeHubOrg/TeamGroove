import json
from log_in import sp
#make into a class with two methods for main program.
#1) list users collabs
#2) choose playlist
def get_users_collab_playlists():
    playlists = sp.current_user_playlists()
    collab_playlists = []
    for playlist in playlists['items']:
        if playlist['collaborative']:
            collab_playlists.append(playlist)
    return collab_playlists

def list_collab_playlists():
    playlists = get_users_collab_playlists()
    for number, playlist in enumerate(playlists):
        print(f"{number+1}) {playlist['name']}")

def choose_playlist():
    choice = input("Enter number for playlist\n> ")
    chosen_playlist = get_users_collab_playlists()[int(choice)-1]
    return chosen_playlist

def get_playlist_uri():
    uri = choose_playlist()['uri']
    return uri


list_collab_playlists()
playlist_uri = get_playlist_uri()
data = choose_playlist()
a = json.dumps(choose_playlist(),indent=4)
print(type(a))


# def get_playlist_uri(choose_playlist):
#     playlist_id = choose_playlist()['uri']
#     return playlist_id
#
# def save_tracks_db():
#     tracks = sp.playlist_items(get_playlist_uri())
#     for track in tracks['items']:
#         print(track['track']['name'])






















# sp.add_to_queue('1I4EczxGBcPR3J3KeyqFJP')

# Int set up
# user logs in
# get access to shared play list
# store shared playlist as a TeamGroove playlist (max 2?)
# store all tracks in the db



# check if new songs have been added/removed

