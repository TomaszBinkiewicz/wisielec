"""hangman URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path

from hangman_app.views import base, AddWord, Play, AllScores, AllPlayers, SaveScore, Login, logout, GameOver

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', base, name='base'),
    path('add-word', AddWord.as_view(), name='add_word'),
    path('hangman-play', Play.as_view(), name='play'),
    path('hangman-scores', AllScores.as_view(), name='all_scores'),
    path('hangman-players', AllPlayers.as_view(), name='all_players'),
    path('hangman-save-score', SaveScore.as_view(), name='save_score'),
    path('hangman-login', Login.as_view(), name='login'),
    path('logout', logout, name='logout'),
    path('hangman-game-over', GameOver.as_view(), name='game_over'),
]
