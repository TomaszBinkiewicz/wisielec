from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.views import View
from hangman_app.models import Word, Player, Score
from random import randint
from hangman_app.lib import password_hash, validate_user
from django.core.exceptions import ObjectDoesNotExist


def base(request):
    return render(request, 'base.html')


class AddWord(View):
    def get(self, request):
        logged = request.session.get('logged_user')
        all_words = Word.objects.all()
        num_of_words = len(all_words)
        return render(request, 'add_word.html', context={'num_of_words': num_of_words, 'logged': logged})

    def post(self, request):
        logged = request.session.get('logged_user')
        new_word = request.POST.get('word')
        all_words = Word.objects.all()
        num_of_words = len(all_words)
        if len(new_word) > 64:
            message = 'Given word is too long. Max lenght is 64 characters'
            return render(request, 'add_word.html',
                          context={'message': message, 'num_of_words': num_of_words, 'logged': logged})
        else:
            for word in all_words:
                if new_word == word.word:
                    message = 'Given word already added'
                    return render(request, 'add_word.html',
                                  context={'message': message, 'num_of_words': num_of_words, 'logged': logged})
            Word.objects.create(word=new_word)
            num_of_words += 1
            message = 'Word added'
            return render(request, 'add_word.html',
                          context={'message': message, 'num_of_words': num_of_words, 'logged': logged})


class Play(View):
    def get(self, request):
        logged = request.session.get('logged_user')
        request.session['counter'] = 0
        all_words = Word.objects.all()
        num_of_words = len(all_words)
        draw_number = randint(0, num_of_words - 1)
        word_to_guess = all_words[draw_number].word
        request.session['word_to_guess'] = word_to_guess
        display = len(word_to_guess) * '_ '
        request.session['display'] = display
        request.session['used_letters'] = []
        return render(request, 'play.html',
                      context={'hidden': display, 'counter': request.session['counter'], 'logged': logged})

    def post(self, request):
        logged = request.session.get('logged_user')
        max_counter = 11
        word_to_guess = request.session.get('word_to_guess')
        display = request.session.get('display')
        guess = request.POST.get('guess')
        guess.strip()
        used_letters = request.session.get('used_letters')
        if guess in used_letters:
            return render(request, 'play.html',
                          context={'hidden': display, 'counter': request.session['counter'],
                                   'used_letters': used_letters, 'logged': logged})
        used_letters.append(guess)
        request.session['used_letters'] = used_letters
        if request.session['counter'] == max_counter:
            return redirect('game_over')
        else:
            new_display = ''
            if guess in word_to_guess:
                for i in range(len(word_to_guess)):
                    if display[2 * i] != '_':
                        new_display += display[2 * i] + ' '
                    else:
                        if word_to_guess[i] == guess:
                            new_display += guess + ' '
                        else:
                            new_display += '_ '
                request.session['display'] = new_display
            else:
                new_display = display
                request.session['counter'] += 1
            if '_' in new_display:
                return render(request, 'play.html',
                              context={'hidden': new_display, 'counter': request.session['counter'],
                                       'used_letters': used_letters, 'logged': logged})
            return redirect('save_score')


class AllScores(View):
    def get(self, request):
        logged = request.session.get('logged_user')
        scores = Score.objects.all().order_by('-score')
        return render(request, 'all_scores.html', context={'scores': scores, 'logged': logged})


class AllPlayers(View):
    def get(self, request):
        logged = request.session.get('logged_user')
        players = Player.objects.all().exclude(nick='anonymous_player').order_by('-total_points', 'games_played')
        return render(request, 'all_players.html', context={'logged': logged, 'players': players})


class GameOver(View):
    def get(self, request):
        logged = request.session.get('logged_user')
        word = request.session.get('word_to_guess')
        return render(request, 'game_over.html', context={'logged': logged, 'word': word})


class SaveScore(View):
    def get(self, request):
        logged = request.session.get('logged_user')
        word = request.session.get('word_to_guess')
        counter = request.session.get('counter')
        display = request.session.get('display')
        if word == display.replace(' ', ''):
            score = 11 - counter
            return render(request, 'save_score.html', context={'word': word, 'score': score, 'logged': logged})
        else:
            raise Http404('Finish playing the game')

    def post(self, request):
        logged = request.session.get('logged_user')
        score = 11 - request.session.get('counter')
        guessed_word = request.session.get('word_to_guess')
        word = Word.objects.get(word=guessed_word)
        if logged:
            player = Player.objects.get(nick=logged)
            player.total_points += score
            player.games_played += 1
            player.save()
        else:
            player = Player.objects.get(nick='anonymous_player')
            player.games_played += 1
            player.save()
        Score.objects.create(player_id=player, word_id=word, score=score)
        del request.session['counter']
        del request.session['word_to_guess']
        del request.session['used_letters']
        del request.session['display']
        return redirect('all_scores')


class Login(View):
    def get(self, request, login_error_message='', register_error_message=''):
        logged = request.session.get('logged_user')
        request.session['previous_page'] = request.META.get('HTTP_REFERER')
        return render(request, 'login.html', context={'login_error_message': login_error_message,
                                                      'register_error_message': register_error_message,
                                                      'logged': logged})

    def post(self, request):
        if 'login' in request.POST:
            nick = request.POST.get('nick')
            passwd = request.POST.get('password')
            if validate_user(nick, passwd):
                request.session['logged_user'] = nick
                previous_page = request.session.get('previous_page')
                return redirect(previous_page)
            else:
                return self.get(request, login_error_message='Wrong login data')
        elif 'register' in request.POST:
            new_nick = request.POST.get('nick')
            new_passwd = request.POST.get('password')
            if not new_nick:
                return self.get(request, register_error_message='Please enter a valid nick')
            elif not new_passwd:
                return self.get(request, register_error_message='Please enter a valid password')
            try:
                players = Player.objects.get(nick=new_nick)
            except ObjectDoesNotExist:
                new_player = Player()
                new_player.nick = new_nick
                new_player.password = password_hash(new_passwd)
                new_player.total_points = 0
                new_player.save()
                request.session['logged_user'] = new_nick
                previous_page = request.session.get('previous_page')
                return redirect(previous_page)
            else:
                return self.get(request, register_error_message='Nick already in use')


def logout(request):
    del request.session['logged_user']
    return redirect('base')
