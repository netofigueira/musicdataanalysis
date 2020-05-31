#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 11:49:39 2020

@author: neto
"""

#get artist uri on spotify

#step1 make request to get artist data

#step2 use pickle to dont worry about token expiration all the time 

#step3 manipulate data to obtain artist uri 

import requests
import pickle
import json 
import secrets
import pandas as pd
from PIL import Image 

#this function access spotify api to get artists info,
#we are going to use artist's id to access album informations later.
spotify_token = "BQCJNaqMThhrt7JK_mlYkebUdA_4uEEKV-etuAPP6v2T8cR4kLFxJ9jSFsr398oYE2JGxTQ9rGeTV9GjKw7Z4Vv7K2GzxyCbLXiW3DtCz4F9Iax1A1fz4g4k5NvcQVyC3OJjYVuDLyn_DmE_bmAjPTWeea9nIsk"
spotify_user = "09498uosdol9l0w8nwar9r1yz"
artist_name = 'Death Grips'

def spotify_request(user, token, artist_name):
    query = "https://api.spotify.com/v1/search?q={}&type=artist".format(artist_name)
    #make the request to spotify api using requests library
    r = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(token)
            }
        )
    
    #transform the requested object (dictionary) into a pickle object
    #this way we dont need to go back to make same request again
    pickle_out = open("spotify_dict.pickle","wb")
    pickle.dump(r.json(), pickle_out)
    pickle_out.close()


#function to get artist uri and id

def spotify_artist_uri():
    #here we open the pickle file and start working on it
    pickle_in = open("spotify_dict.pickle","rb")
    spotify_dict = pickle.load(pickle_in)
    
    #get the items needed from the artist dictionary
    artist_uri = spotify_dict['artists']['items'][0]['uri']
    artist_id = spotify_dict['artists']['items'][0]['id']
   
    return artist_uri, artist_id


#function that get an artist album data
def spotify_artist_album(token,artist_id):
    query = "https://api.spotify.com/v1/artists/{}/albums".format(artist_id)
    r = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(token)
            }
        )
    
    #transform the requested object (dictionary) into a pickle object
    pickle_out = open("spotify_album.pickle","wb")
    pickle.dump(r.json(), pickle_out)
    pickle_out.close()

#get data from the album
def spotify_album_data():
    #here we open the pickle file and start working on it
    pickle_in = open("spotify_album.pickle","rb")
    spotify_album_dict = pickle.load(pickle_in)
    return spotify_album_dict

#create a dataframe with the albums names and urls from cover art and Id
#takes the album_dictionary as argument.
def spotify_album_df(album_dict):
    album_title = []
    album_cover_url = []
    album_id = []
    for album in album_dict['items']:
        album_title.append(album['name'])
        album_id.append(album['id'])
        album_cover_url.append(album['images'][0]['url'])
    
    data = [album_title, album_id, album_cover_url]
    df = pd.DataFrame(data)
    df = df.transpose()
    df.columns = ["title", "id", "coverUrl"]    
    return df



#funciton to get all tracks of an album
#takes the data frame of the album


#this funcition is responsible for getting track names and id by album
#it takes the album dictionary as argument and return a dictionary 
#this dictionary has its keys as albums names, and the value for each key 
#are a list of list. each element of the list is the track name followed by the track id
def get_album_tracks(album_dict):
    albumTracks_dict = {}
    for i in range(len(album_dict['items'])):
        query = "https://api.spotify.com/v1/albums/{}/tracks".format(album_dict['items'][i]['id'])
        r = requests.get(
                query,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(spotify_token)
                }
            )
        
        d_json = r.json()
        #produce a list of dictionaies, each dict contains track name and id and more.
        tracks_list = d_json['items']
        
        
        tracklist = []
        for item in tracks_list:
            tracklist.append(list((item['name'], item['id'])) )
            
        
        
        albumTracks_dict[album_dict['items'][i]['name']] = tracklist
    return albumTracks_dict


#preparing the data frame tha will handle all infos of tracks


def generate_tracks_df(tracks_dict):
    #first loop trough the tracks dictinonary and put values into lists
    
    track_names = []
    track_ids = []
    track_albums = []
    album_cover = []
    for keys, values in tracks_dict.items():
        for i in range(len(values)):
            track_names.append(values[i][0])
            track_albums.append(keys)
            track_ids.append(values[i][1])
            
    df = pd.DataFrame({'track_name':track_names, 'track_id':track_ids, 'track_album': track_albums})

    return df


def get_track_features(tracks_df, album_df):
    
    #fist we produce a new data frame with albums names as index
    
    aux_df = tracks_df.copy()
    aux_df.set_index('track_album', inplace=True)
    
    #now we produce an string with ids to pass to spotify request
    
    albums_list = list(album_df['title'])
    #this is the data frame that will receive all tracks information
    big_df = pd.DataFrame()
    for album in albums_list:
        #produce the  ids list
        ids_list = list(aux_df.loc[album]['track_id'])
        ids = ','.join(ids_list)
        
        query = "https://api.spotify.com/v1/audio-features?ids={}".format(ids)
        #make the request to spotify api using requests library
        r = requests.get(
                query,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(spotify_token)
                }
            )
        
        r_json = r.json()
        #print(r_json)
        aux_df2 = pd.DataFrame(r_json['audio_features'])
        big_df = big_df.append(aux_df2)
        ids_list = []
        ids = ''
    return big_df





spotify_request(spotify_user, spotify_token, artist_name)

uri, artist_id = spotify_artist_uri()


spotify_artist_album( spotify_token, artist_id)
album_dict = spotify_album_data()

#datafrmae with album infos
album_df = spotify_album_df(album_dict)


tracks_dict = get_album_tracks(album_dict)

tracks_df = generate_tracks_df(tracks_dict)
tracks_features_df = get_track_features(tracks_df, album_df)

df_aux = tracks_df.merge(tracks_features_df, how='inner', left_on='track_id', right_on='id')
df_final = df_aux.merge(album_df, how='inner', left_on='track_album', right_on='title')
df_final.to_csv('{}.csv'.format(artist_name))
#pickle_out = open("final_df.pickle","wb")
#pickle.dump(df_final, pickle_out)
#pickle_out.close()