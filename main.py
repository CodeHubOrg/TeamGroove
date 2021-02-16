# Create TeamGroove user DB
from dotenv import load_dotenv
from log_in import log_in


"""options"""
# Create new Teamgroove playlist
# Join a new already existing Teamgroove playlist
# Open a Teamgroove playlist

"""Create new Teamgroove playlist"""
# List trough current users colab playlists
# Check playlist ID against TeamGroove playlists
# if already in use, suggest joining it.
# Create Teamgroove playlist database


def main():
    load_dotenv()
    log_in()


if __name__ == "__main__":
    main()
