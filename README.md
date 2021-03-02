
# Team Groove

Bringing democracy to shared music playlists

## Vision

Allow a group of people to vote on songs in a shared playlist, thereby affecting
the frequency that the songs are played.

## Aims

1. Learn something about Python coding
1. Learn something about Scrum methodology
1. Have fun and teach each other what we've learnt
1. Produce code we can can be proud of and include in our portfolios
1. Allow everyone, regardless of ability or commitment, to contribute

Please view the
[project Wiki pages](https://github.com/CodeHubOrg/TeamGroove/wiki) in GitHub
for details of decisions, guides and notes.

## Team

This project is being run as part of the
[PyLAB](https://www.wthub.org/python-learning-for-advanced-beginners-pylab/)
(Python Learning for Advanced Beginners) workshops, hosted by
[Women's Tech Hub ~ Bristol](https://www.wthub.org/) in association with
[Bristol Code Hub](https://www.codehub.org.uk/). We hold fortnightly MeetUps as
part of
[Workshop Wednesdays](https://www.meetup.com/Womens-Tech-Hub-Bristol/), so if
you'd like to join please sign up. If you'd like to chat with us, please join
the [Bristol Code Hub Slack](http://slack.codehub.org.uk/) and introduce
yourself.

## Getting Started

If this is the first time you've checked out a project from GitHub, run a Python
project using Poetry or Django or are having trouble getting anything running,
please read through these steps. If you're still not having any joy, please get
in touch with the [team](#Team).

### 1. System requirements

Team Groove runs using Python and is intended to be OS agnostic. You should be
able to develop Team Groove in Windows, OS X or Linux.
To run Team Groove locally, for testing and developing, you'll need:

1. [git](https://git-scm.com/downloads) or a client like
[GitHub Desktop](https://desktop.github.com/) or
[GitKraken](https://www.gitkraken.com/) for source control
1. [Python 3.6 or greater](https://www.python.org/downloads/) as Team Groove is
written in Python
1. [Poetry](https://python-poetry.org/docs/#installation) as we're using this as
our tool to manage Python dependencies and virtual environments.

If you want to make changes to the code, you'll also need a text editor or
interactive development environment (IDE). Members of the team use the IDEs
listed below, so we can offer help with these if you encounter problems getting
started:

* [PyCharm](https://www.jetbrains.com/pycharm/)
* [Visual Studio Code](https://code.visualstudio.com/)
* [Sublime Text](https://www.sublimetext.com/)

### 2. Checkout code from GitHub

The Team Groove project code can be found
[here](https://github.com/CodeHubOrg/TeamGroove). To check the code out locally,
you'll need access to git. If you're using git on the command-line the command
to clone Team Groove using
[SSH](https://docs.github.com/en/github/using-git/which-remote-url-should-i-use#cloning-with-ssh-urls)
is:

``` bash
    git clone git@github.com:CodeHubOrg/TeamGroove.git
```

To clone Team Groove using
[HTTPS](https://docs.github.com/en/github/using-git/which-remote-url-should-i-use#cloning-with-https-urls),
use:

``` bash
git clone https://github.com/CodeHubOrg/TeamGroove.git
```

### 3. Install package dependencies

If you don't have Poetry installed, please follow
[the instructions](https://python-poetry.org/docs/#installation)
on the Poetry site. When you have Poetry installed, you can run the command
below to install the modules required for Team Groove.

``` bash
    poetry install
```

This command creates a virtual environment and installs the modules used to run
Team Groove, including:

* [Django](https://www.djangoproject.com/) - the web framework
* [Spotipy](https://spotipy.readthedocs.io/en/2.9.0/) - library for interacting
with the Spotify Web API. This will also install modules we're using for
developing Team Groove, but are not required for running the application.
* [Black](https://black.readthedocs.io/en/stable/) - an "uncomprimising" Python
code formatter to keep our code style consistent.
* [Pylint](https://pylint.org/) - a static code analysis tool for refactoring
and catching errors.

### 4. Run Team Groove locally

To be able to start Team Groove running, you'll need a set up some environment
variables. Copy the `.env.example` file to `.env` and open it in your preferred
editor. You'll see there are some fields that need populating.

To generate a `SECRET_KEY` for Django you can run this command on the command
line:

``` bash
    python manage.py shell -c 'from django.core.management import utils; 
    print(utils.get_random_secret_key())'
```

You can copy and paste the string generated into you `.env` file.

If you wish to Team Groove with Spotify you will need to set up a developer
account with Spotify so you can generate a API key and secret. You can log in or
create a new account [here](https://developer.spotify.com/dashboard/).

Team Groove uses [Django](https://www.djangoproject.com/) which comes complete
with a simple web server. This means you can try running Team Groove direct from
command-line once you've installed the necessary modules by running the command
below from the project directory of Team Groove

``` bash
    python manage.py runserver
```

This starts up the bundled Django web server so you should be able to see the
site running.
