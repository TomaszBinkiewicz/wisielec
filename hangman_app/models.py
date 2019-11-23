from django.db import models


class Word(models.Model):
    word = models.CharField(max_length=64)


class Player(models.Model):
    nick = models.CharField(max_length=64)
    password = models.TextField()
    total_points = models.BigIntegerField(default=0)
    games_played = models.BigIntegerField(default=0)


class Score(models.Model):
    score = models.IntegerField()
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    word_id = models.ForeignKey(Word, on_delete=models.SET('---'))
