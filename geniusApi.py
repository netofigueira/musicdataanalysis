#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 13:06:32 2020

@author: neto
"""


import requests
import pandas as pd
from bs4 import BeautifulSoup
import pickle 
import nltk
import os 
import nltk.corpus
import string
from nltk.corpus import stopwords
from nltk import word_tokenize
from nrclex import NRCLex
import time
from selenium import webdriver

#genius scrapper

token = '+++++++++'


token2 = token
artist_name = 'CHOOSE ARTIST'


def get_artist_id(artist_name):
    query = 'https://api.genius.com/search?q={}'.format(artist_name)
    
    response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(token)
            }
        )
    
    r_dict = response.json()
    
    artist_id = r_dict['response']['hits'][0]['result']['primary_artist']['id']
    return artist_id


def get_songs_lyrics_url(artist_id, token):
    aux = 1
    song_url = []
    song_title = []
    
    while aux >= 1:
        query2 = 'https://api.genius.com/artists/{}/songs?per_page=50&page={}'.format(artist_id, aux)
        
        response2 = requests.get(
                query2,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(token)
                }
            )
        
        
        r_dict2 = response2.json()
        
        songs_list = r_dict2['response']['songs']
        
        
        
        for i in range(len(songs_list)):
            song_url.append(songs_list[i]['url'])
            song_title.append(songs_list[i]['title'])
        if(r_dict2['response']['next_page'] != None):
            aux = r_dict2['response']['next_page']
        else:
            break
        
    

    return song_title, song_url

artist_id = get_artist_id(artist_name)

#name_list, url_list = get_songs_lyrics_url(artist_id, token)



def get_lyrics(url_list, name_list):
    lyrics = []
    driver = webdriver.Chrome()
    driver.maximize_window()
    for i in range(len(url_list)):
        #r = requests.get(url_list[i])
        
        driver.get(url_list[i])
        content = driver.page_source.encode('utf-8').strip()
        soup = BeautifulSoup(content, 'html.parser')
        x = soup.find('div', class_='lyrics')
        if (x != None ):
            lyrics.append( [ name_list[i], x.get_text()]  )
    
    driver.close()
    df = pd.DataFrame(lyrics)
    df.rename(columns= {0:'track_name', 1:'track_lyrics'}, inplace=True)
    return df

#lyrics_df = get_lyrics(url_list, name_list)

def pickle_lyrics(lyrics_df):
    pickle_out = open("lyrics.pickle","wb") 
    pickle.dump(lyrics_df, pickle_out)
    pickle_out.close()


#pickle_lyrics(lyrics_df)


pickle_in = open("lyrics.pickle","rb")
lyrics_df = pickle.load(pickle_in)




# def filter_out_punctuation(lyrics_list):
#         """receive list of lyrics, tokenize and filter punctuation and remove stop words"""
#         aux = []
#         for i in range(len(lyrics_list)):
#            aux.append(word_tokenize(lyrics_list[i]))
     
#         """this loop filter the punctuations """
#         for i in range(len(aux)):
#             aux[i] = [word for word in aux[i] if word.isalpha()]
            
#         """this loop get everything in lowercase"""
#         for i in range(len(aux)):
#             aux[i] = [w.lower() for w in aux[i]]

#         stop_words = set(stopwords.words('english'))
        
#         for i in range(len(aux)):
#             aux[i] = [w for w in aux[i] if not w in stop_words]


#         return aux


def filter_lyrics_df(lyrics_df):
    df = lyrics_df.copy(deep=True)
    """receive dataframe, tokenize and filter punctuation and remove stop words"""
    
    
    df['track_lyrics'] = df.track_lyrics.str.replace('[^a-zA-Z]', ' ')
    
    df['track_lyrics'] = df.track_lyrics.str.replace('Chorus', '')
    
    df['track_lyrics'] = df.track_lyrics.str.replace('Verse', '')
    
    df['track_lyrics'] = df.track_lyrics.str.replace('Intro', '')
    
    df['track_lyrics'] = df.track_lyrics.str.lower()
    
    
    df['track_lyrics'] = df['track_lyrics'].apply(word_tokenize)
       
    stop = set(stopwords.words('english'))
    
    df['track_lyrics'] = df['track_lyrics'].apply(lambda x: [item for item in x if item not in stop])
    
    for i in range(len(df['track_lyrics'])):
        df['track_lyrics'][i] = ' '.join(df['track_lyrics'][i])
    return df



def get_lyrics_affects(df):
    """use NRCLex library to get the words affecs frequencies."""    
    df['nrc']  = df['track_lyrics'].apply(NRCLex)
    
    for i in range(len(df)):
       df['nrc'][i] = df['nrc'][i].affect_frequencies
    
    df2  = df['nrc'].apply(pd.Series)
    
    df_final = pd.concat([df, df2], axis=1)
    
    return df_final

df = filter_lyrics_df(lyrics_df)
dfl_final = get_lyrics_affects(df)
dfl_final = dfl_final[dfl_final.track_lyrics != 'instrumental']
dfl_final.to_csv('{}_lyrics.csv'.format(artist_name))
