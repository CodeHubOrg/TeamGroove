
def append_track_data(request, returned_data, LIMIT):
    # TRACK_ARTIST, TRACK_NAME and TRACK_ALBUM are intended for view
    # TRACK_ID is used for adding to a playlist        
    track_artist = []
    track_name   = []
    track_id     = []
    track_album  = []

    index = 0        
    while index < LIMIT:
        try:
            track_artist.append(returned_data['items'][index]['track']['artists']['name'])
            track_name.append(returned_data['items'][index]['track']['name']) 
            track_id.append(returned_data['items'][index]['track']['id'])
            track_album.append(returned_data['items'][index]['track']['album']['name'])
            index += 1  
        except IndexError:
            break
        except:
            messages.error(request, 'ERROR: Unknown Error compiling track ids, artist names and track names.')
        else:
            context = {
                    'track_artist': track_artist,
                    'track_name':   track_name,
                    'track_id':     track_id,
                    'track_album':  track_album
            }
