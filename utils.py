import streamlit as st 
import json, os, requests 
from streamlit_option_menu import option_menu 
from streamlit_lottie import st_lottie
from playlist import SemanticSearch 

def load_lottieurl(url: str) -> json: 
  r = requests.get(url)
  if r.status_code != 200: 
    return None 
  return r.json()
  
def load_lottie(url: str, height : int = 200, width : int = 200): 
    lottie_playlist = load_lottieurl(url)
    st_lottie(lottie_playlist, height = height, width = width)
    
def give_it_here(link): 
  if url_checkers(check_video_url_single, link): 
    return 'SINGLE'
  if url_checkers(check_channel_url, link): 
    return 'CHANNEL'
  if url_checkers(check_playlist_url, link): 
    return 'PLAYLIST'
  
  else: 
    return 'Your link is not proper!'
    
def url_checkers(function, link): 
  if function: 
    if function(link) == True: 
      return True 
    if function(link) == False:    
      return False   
        
def check_video_url_single(url):
  url32 = url[:32]
  url11 = url[32:]

  if url32 == 'https://www.youtube.com/watch?v=' and len(url11) == 11: 
    return True 
  else: return False 
    
def check_playlist_url(link): 
  link38 = link[:38]
  link_after_38 = link[38:]

  if len(link_after_38) == 34 and str(link38) == 'https://www.youtube.com/playlist?list=': 
    return True
  else: 
    return False 
    
def check_channel_url(link): 
  link32, link26 = link[:32], link[:26]
  link_7 = link[-7:]

  if (link32 == 'https://www.youtube.com/channel/' or link26 == 'https://www.youtube.com/c/') and link_7 == '/videos': 
    return True  
  else: 
    return False 
    
def shower(query, df): 
  se = SemanticSearch(query, df)
  timing, yt_links = se.search()
  st.subheader("This are all the videos with highlited based on your Query!")

  for i in range(len(yt_links)): 
    st.caption(f"Video: {i + 1}")
    st.video(yt_links[i], start_time = timing[i])
