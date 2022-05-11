def append_track_data(returned_data, track_name_artist_album, track_id, LIMIT):
    # TRACK_ARTIST, TRACK_NAME and TRACK_ALBUM are intended for view
    # TRACK_ID is used for adding to a playlist        
    index = 0        
    while index < LIMIT:
        try:
            track_name_artist_album.append(
                returned_data['tracks']['items'][index]['name']
                + '    ' 
                + returned_data['tracks']['items'][index]['artists'][0]['name']
                + '    ' 
                + returned_data['tracks']['items'][index]['album']['name']
            )
            track_id.append(returned_data['tracks']['items'][index]['id'])
        except IndexError:
            break
        else:
            pass
        index += 1  

    cleaned_search_result = { 'track_name_artist_album': track_name_artist_album, 'track_id': track_id }

    return cleaned_search_result