import pandas as pd
from requests import request
import json
import numpy as np
from machine import *
import os
import time

# set table
df_babyname = pd.read_csv('babyname.csv')
df_babyname.fillna(0, inplace = True)
# def babynameGenerator(judul_film, judul_lagu, tahun_lagu):
def babynameGenerator(jenis_kelamin, jumlah_huruf_minimal, jumlah_huruf_maksimal, jumlah_nama, judul_film, judul_lagu, tahun_lagu):
    url_movie = "https://movierecommender123.azurewebsites.net/login"
    data = {
        "username": "string",
        "password": "string"
    }
    response_movie = request("POST", url_movie, data=data)
    access_token = response_movie.json()["access_token"]
    token_type = response_movie.json()["token_type"]

    #Membuat request
    url_movie = f"https://movierecommender123.azurewebsites.net/movierecommendation/"
    headers = {
        "accept": "application/json",
        "Authorization": token_type + " " + access_token, 
        "Content-Type": "application/json"
    }
    params = {
        "judul_film": judul_film
    }
    response_movie = request("POST", url_movie, headers=headers, json = params)
    result_movie= response_movie.json()
    judul = result_movie["Title"]

    list_of_dict_values = list(judul.values())
    df_movie = pd.DataFrame (list_of_dict_values, columns = ['Film'])

    df_movie['Year'] = df_movie['Film'].str[-5:-1].astype(int)

    df1_movie = df_movie['Year']

    listTahun_movie = df1_movie
        
    # API Music Recommender
    url_music = "https://musicrecommendationtst.azurewebsites.net/token"
    data = {
        "username": "divya",
        "password": "mysecret"
    }
    
    response_music = request("POST", url_music, data=data)

    #Akses token
    access_token = response_music.json()["access_token"]
    token_type = response_music.json()["token_type"]

    # Membuat request
    url_music = f"https://musicrecommendationtst.azurewebsites.net/musicrecommendation"
    headers = {
        "accept": "application/json",
        "Authorization": token_type + " " + access_token, 
        "Content-Type": "application/json"
    }
    params = {
        "name": judul_lagu,
        "year": tahun_lagu 
    }


    response_music = request("POST", url_music, headers=headers, json=params)
    result_music = response_music.json()
    df_music= pd.DataFrame.from_dict(result_music, orient="columns")
    df1_music = df_music['year']
    listTahun_music = df1_music

    listTahun_music = 2010
    averageYear = (sum(listTahun_movie+listTahun_music))//20
    data_boy = df_babyname.loc[(df_babyname['year']== averageYear),['male']]
    data_girl = df_babyname.loc[(df_babyname['year']== averageYear),['female']]
    # if jenis_kelamin == "L":
    #     f = open('lakilaki.txt','w')
    #     write_to_file = data_boy.values
    #     f.write(write_to_file)
    #     f.close()
    # elif jenis_kelamin == "M":
    #     f = open('perempuan.txt','w')
    #     write_to_file = data_girl.values
    #     f.write(write_to_file)
    #     f.close()       
    # else :
    #     pass
    np.savetxt(r'lakilaki.txt', data_boy.values, fmt='%s')
    np.savetxt(r'perempuan.txt', data_girl.values, fmt='%s')
    return initial(jenis_kelamin, jumlah_huruf_minimal, jumlah_huruf_maksimal, jumlah_nama)