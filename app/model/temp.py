from requests import request
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from collections import defaultdict
import pandas as pd
import statistics
from urllib.parse import quote
import random
from collections import Counter
import numpy as np

## info
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="49a38597365d450c82bde54db724a4df", client_secret="676bfa0ea98549acb92c38e0573d5354"))
url_music_recommendation = f"https://musicrecommendationtst.azurewebsites.net/musicrecommendation"
url_token_music = "https://musicrecommendationtst.azurewebsites.net/token"
url_token_movie = "https://movierecommender123.azurewebsites.net/login"
url_movie_quotes = "https://api.quodb.com/search/"
url_movie_recommendation = "https://movierecommender123.azurewebsites.net/movierecommendation/"
url_lyrics = "https://api.musixmatch.com/ws/1.1/"
musicxmatch_api_key = "&apikey=811aaabaa26952f4ee07b374e8105061"
musicxmatch_api_key2 = "&apikey=ba16e7eb0f095325645ab93d48555392" ##backup
musicxmatch_api_key3 = "&apikey=811aaabaa26952f4ee07b374e8105061"

# song = str(input("Input song title: "))
# year = int(input("Input song year: "))

def find_song_artist(name, year):
    results = sp.search(q= 'track: {} year: {}'.format(name,year), limit=1)
    if results['tracks']['items'] == []:
        return None
    results = results['tracks']['items'][0]['artists']
    for i in results:
        artist = i['name']
    song_info = [name,artist]
    return song_info

def find_song_valence(name, year):
    results = sp.search(q= 'track: {} year: {}'.format(name,year), limit=1)
    if results['tracks']['items'] == []:
        return None
    results = results['tracks']['items'][0]
    track_id = results['id']
    audio_features = sp.audio_features(track_id)[0]

    return audio_features['valence']

def find_song_energy(name, year):
    results = sp.search(q= 'track: {} year: {}'.format(name,year), limit=1)
    if results['tracks']['items'] == []:
        return None

    results = results['tracks']['items'][0]
    track_id = results['id']
    audio_features = sp.audio_features(track_id)[0]

    return audio_features['energy']

# obtain access token
def generate_token(url):
    token_data = []
    url = url
    data = {
        "username": "divya",
        "password": "mysecret"
    }
    response = request("POST", url, data=data)
    token_data.append(response.json()["access_token"]) 
    token_data.append(response.json()["token_type"]) 
    return token_data


# make the request
def get_music_mood(songlist):
    # metadata_cols = ['song_recommendations', 'mood based on songs'] 
    user_result = {}
    url = url_music_recommendation
    token_type = generate_token(url_token_music)[1]
    access_token = generate_token(url_token_music)[0]
    headers = {
        "accept": "application/json",
        "Authorization": token_type + " " + access_token, 
        "Content-Type": "application/json"
    }
    params = {
        "name": songlist[0]['name'],
        "year": songlist[0]['year']
    }
    try:
        response2 = request("POST", url, headers=headers, json=params)
        res = response2.json()
        user_result.update(song_recommendations=res)
        songList = []
        for x in res:
            songList.append(x['name'])
        yearList = []
        valenceList = []
        energyList = []
        for x in res:
            yearList.append(x['year'])
        for (i,j) in zip(yearList, songList):
            ## error handler
            try:
                valence_value = float(find_song_valence(i, j))
                energy_value = float(find_song_energy(i, j))
                valenceList.append(valence_value)
                energyList.append(energy_value)
            except:
                continue
        ## get valence and energy avg value 
        valence_avg = statistics.mean(valenceList)
        energy_avg = statistics.mean(energyList)

        ## mood classification 
        if (0.0 <= valence_avg < 0.50) and (0.0 <= energy_avg < 0.50):
            mood = 'Sad'
        elif (0.0 <= valence_avg < 0.50) and (0.50 <= energy_avg < 1.00):
            mood = 'Angry'
        elif (0.50 <= valence_avg < 1.00) and (0.0 <= energy_avg < 0.50):
            mood = 'Calm'
        else: 
            mood = 'Happy'
        user_result.update(mood=mood)
        return user_result
    except:
        print("Server Error Occured. Please reinput your data")

def get_lyrics(song, artist):
    api_call = url_lyrics + "matcher.lyrics.get" + "?format=json&callback=callback" + "&q_artist=" + artist + "&q_track=" + song + musicxmatch_api_key
    response = request("GET", api_call)
    data = response.json()['message']['body']['lyrics']['lyrics_body']
    if (data):
        return(data)
    else:
        print("Unfortunately we're not authorized to show these lyrics")

def common_word_lyrics(songlist, target):
    ## error handler --> musixmatch limited the hit on free users
    user_result = {}
    try:
        song = songlist[0]['name']
        year = songlist[0]['year']
        artist = find_song_artist(song, year)
        data = get_lyrics(artist[1], artist[0])
        transform = str(data)
        split_it = transform.split()
        temp = Counter(split_it)
        most_occur = temp.most_common(6)
        words = ""
        temp = []
        film=''
        films = ''
        filmsList = []
        quotes = ''
        for i in most_occur:
            words +=  (i[0]) + " "
        # arr = np.array(most_occur)
        text_encoded = quote(words)
        url_target = url_movie_quotes + text_encoded + '?titles_per_page=10'
        response = request("GET", url_target)
        res = response.json() 
        for j in res['docs']:
            try:
                film += str(j['title'])
                quotes += j['phrase']
                films = get_movie_recommendation(film)
                filmsList.append(films)
                temp.append(j['title'])
            except:
                continue
            else:
                if (films): 
                    break
                break
        if (target == "only_quotes"):
            user_result.update(quotes=quotes)
            user_result.update(film=film)
            print(user_result)
            return user_result
        if (target == "all"): 
            user_result.update(quotes=quotes)
            user_result.update(quotes_by_film=film)
            user_result.update(film_recommendations=films)
            print(user_result)
            return user_result
    except:
        print("I'm sorry, we can't get the data you want since Musixmatch limit their api hit per day for free users. Come back again tomorrow or you can use other endpoints")
    # else:
    #     print("ok")

def get_quotes(mood, target): 
    ## example: https://api.quodb.com/search/bright%20smile?titles_per_page=50
    user_result = {}
    keywords = {
        "Sad": ["Don't be sad", "Be happy" , "You look great", "Doing best", "Don't Give up"],
        "Angry": ["It's Okay", "Take a deep breath", "It's okay not to be okay", "Don't let anger"],
        "Happy": ["great day", "bright smile", "Happy looks good on you"],
        "Calm": ["nothing impossible", "just keep swimming", "miracles take a little time"]
    }
    # for (key, value) in keywords.items():
    temp = []
    film=''
    films = ''
    filmsList = []
    quotes = ''
    random.shuffle(keywords[mood])
    for i in  keywords[mood]:
        text_encoded = quote(i)
        url_target = url_movie_quotes + text_encoded + '?titles_per_page=10'
        response = request("GET", url_target)
        res = response.json() 
        for j in res['docs']:
            try:
                film += str(j['title'])
                quotes += j['phrase']
                films = get_movie_recommendation(film)
                filmsList.append(films)
                temp.append(j['title'])
            except:
                continue
            else:
                if (films): 
                    break
                break
            break
        break
    if (target == "only_quotes"):
        user_result.update(quotes=quotes)
        user_result.update(film=film)
        return user_result
    if (target == "all"): 
        user_result.update(quotes=quotes)
        user_result.update(quotes_by_film=film)
        user_result.update(film_recommendations=films)
        return user_result

def get_movie_recommendation(film):
    url = url_movie_recommendation
    token_type = generate_token(url_token_movie)[1]
    access_token = generate_token(url_token_movie)[0]
    headers = {
        "accept": "application/json",
        "Authorization": token_type + " " + access_token, 
        "Content-Type": "application/json"
    }
    params = {
        "judul_film": film,
    }
    response = request("POST", url, headers=headers, json=params)
    res = response.json()
    filmList = list(res['Title'].values())
    return filmList

def get_all(songlist, target):
    user_result = {}
    first_dict = get_music_mood(songlist)['song_recommendations']
    user_result.update(song_recommendations=first_dict)
    second_dict = get_music_mood(songlist)['mood']
    user_result.update(mood=second_dict)
    if (target == 'mood'):
        third_dict = get_quotes(second_dict, "only_quotes")
        user_result.update(quotes=third_dict)
        forth_dict = get_quotes(second_dict, "all")['quotes_by_film']
        user_result.update(quotes_by_film=forth_dict)
        fifth_dict = get_quotes(second_dict, "all")['film_recommendations']
        user_result.update(film_recommendations=fifth_dict)
        return user_result
    if (target == 'lyrics'):
        third_dict = common_word_lyrics(songlist, "only_quotes")
        user_result.update(quotes=third_dict)
        forth_dict = common_word_lyrics(songlist, "all")['quotes_by_film']
        user_result.update(quotes_by_film=forth_dict)
        fifth_dict = common_word_lyrics(songlist, "all")['film_recommendations']
        user_result.update(film_recommendations=fifth_dict)
    return user_result

# get_movie_recommendation("Avatar")
# common_word_lyrics([{'name': 'Say So', 'year':2019}], "all")
# get_music_valence()
# word_cloud_song_lyrics()
# id = get_track_id("Doja Cat", "Say So")
# print(id)
# get_lyrics("Say So", "Doja Cat")
# find_song_artist("Woman", 2021)
# print(artist[1])
# common_word_lyrics()
# song_mood = get_music_mood()
# get_music_mood()
# target1 = "only_quotes"
# target2 = "all"
# get_quotes(song_mood, target1)
# get_quotes(song_mood, target2)
# common_word_lyrics(get_lyrics(get_track_id(artist[1], song[0])))
# get_movie_recommendation("Finding Nemo")
                                   


