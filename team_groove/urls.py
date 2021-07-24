"""team_groove URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth import views as auth_views

from core.views import FrontPageView
from users.views import signup
from grooveboard.views import grooveboard

from room.views import (
    add_room,
    activate_room,
    room,
    invite,
    accept_invitation,
    edit_room,
    delete_room,
    delete_invitation,
    remove_user_from_room,
)

from spotify.views import (
    authorize_with_spotify,
    user_playlist_tracks,
    add_playlist_to_room,
    search_track_name, 
    search_results, 
    add_track_id_to_playlist
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", FrontPageView.as_view(), name="frontpage"),
    path("grooveboard/", grooveboard, name="grooveboard"),
    path("room/add_room/", add_room, name="add_room"),
    path("room/activate_room/<int:room_id>/", activate_room, name="activate_room"),
    path("room/<int:room_id>/", room, name="room"),
    path("room/invite/", invite, name="invite"),
    path("room/edit_room/", edit_room, name="edit_room"),
    path("room/delete_room/<int:room_id>/", delete_room, name="delete_room"),
    path("room/accept_invitation/", accept_invitation, name="accept_invitation"),
    path(
        "room/delete_invitation/<str:email>/",
        delete_invitation,
        name="delete_invitation",
    ),
    path(
        "room/remove_user_from_room/<str:email>/",
        remove_user_from_room,
        name="remove_user_from_room",
    ),
    path(
        "spotify/authorize_with_spotify/<spotify_code>",
        authorize_with_spotify,
        name="authorize_with_spotify",
    ),
    path(
        "spotify/authorize_with_spotify/",
        authorize_with_spotify,
        name="authorize_with_spotify",
    ),
    path(
        "spotify/user_playlist_tracks/<playlist_id>/",
        user_playlist_tracks,
        name="user_playlist_tracks",
    ),
    path(
        "spotify/add_playlist_to_room/<playlist_id>/",
        add_playlist_to_room,
        name="add_playlist_to_room",
    ),
    path(
        "spotify/search_track_name/<playlist_id>/", 
        search_track_name, 
        name="search_track_name"
    ),
    path(
        "spotify/search_track_name/", 
        search_track_name, 
        name="search_track_name"
    ),
    path(
        "spotify/search_results/<playlist_id>/", 
        search_results, 
        name="search_results"
    ),
    path(
        "spotify/add_track_id_to_playlist/<track_id>/", 
        add_track_id_to_playlist, 
        name="add_track_id_to_playlist"
    ), 
    path("signup/", signup, name="signup"),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="password_reset.html"),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
