################# imports ################################
import pyrebase
import streamlit as st 
from datetime import datetime 
import streamlit as st, os, json   
from streamlit_lottie import st_lottie  
from streamlit_option_menu import option_menu 

from utils import load_lottie, give_it_here
from playlist import SemanticSearch  

######################### Utili functions #####################################
def super(query, dataframe): 
  se = SemanticSearch(query, dataframe)
  timing, yt_links = se.search()
  for i in range(len(yt_links)): 
    st.caption(f"Video: {i + 1}")
    st.video(yt_links[i], start_time = timing[i])

@st.cache(show_spinner = False)
def si(): 
  from single import DFMaker, SingleFileTranscript
  single_transcript = SingleFileTranscript(link).get_transcript() 
  single_dataframe = DFMaker(single_transcript).df()
  st.session_state.single_dataframe = single_dataframe 
  return single_dataframe

@st.cache(show_spinner = False)
def pi(): 
  from playlist import DFMaker, TranscriptSaverPlaylist 
  playlist_transcript = TranscriptSaverPlaylist([link]).get_transcript()
  playlist_dataframe = DFMaker(playlist_transcript).df()
  st.session_state.single_dataframe = playlist_dataframe 
  return playlist_dataframe

@st.cache(show_spinner = False)
def ci(): 
  from channel import DFMaker, TranscriptSaverChannel
  channel_transcripts = TranscriptSaverChannel(link).get_transcript()
  channel_dataframe = DFMaker(channel_transcripts).df()
  st.session_state.single_dataframe = channel_dataframe 
  return channel_dataframe 

########################### Page Configuraiton ###############################
page_title = "Smart Search"
page_icon = '🔥'
st.set_page_config(page_title = page_title, page_icon = page_icon)

######################### Database Configuration ##############################
firebaseConfig = {
  'apiKey': "AIzaSyChLR2Dfjzww5tgtri1nRBcuiAT9o3AAeA",
  'authDomain': "streamlit-authenication.firebaseapp.com",
  'projectId': "streamlit-authenication",
  'databaseURL': 'https://streamlit-authenication-default-rtdb.firebaseio.com/', 
  'storageBucket': "streamlit-authenication.appspot.com",
  'messagingSenderId': "916564037182",
  'appId': "1:916564037182:web:868fb16ec71be9ecc10b6f",
  'measurementId': "G-TS7SKV5YQC", 
  
}

firebase = pyrebase.initialize_app(firebaseConfig)  # initialize firebase 
auth = firebase.auth() # intialize aunthentication 
db = firebase.database()  # initialize database 
storage = firebase.storage()  # initialize storage 

# authentication for the user
choice = st.sidebar.selectbox('login/singup', ['Login', 'Sign up'])
email = st.sidebar.text_input("Please enter your email address") 
password = st.sidebar.text_input("please enter your password", type = 'password')
#st.sidebar.image('https://i.pinimg.com/736x/4e/2f/80/4e2f808cd07610cea05ffdac6244871d.jpg')

# sign up configuration 
if choice == 'Sign up': 
  handle = st.sidebar.text_input("Please input your handle name", placeholder = 'Enter your username')
  submit = st.sidebar.button('Create my account!')

  if submit: 
    user = auth.create_user_with_email_and_password(email, password)  # creating a account with username and password 
    st.success("Your account is created succesfully!")

    # sign in 
    user = auth.sign_in_with_email_and_password(email, password)
    db.child(user['localId']).child("Handle").set(handle)
    db.child(user['localId']).child("ID").set(user['localId'])
    
    st.title("Welcome " + handle)
    st.info("Your account succesfully created. Now you can login!")

if choice == 'Login':
    login = st.sidebar.checkbox('Login')
    if login:
        user = auth.sign_in_with_email_and_password(email,password)
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)  # it writes in horizontal way instead of vertical way! 

        #################################### APP ####################################
        H, S, C = st.tabs(['HOME', 'SMART SEARCH', 'CONTACT'])  # creating tab 

        with H: 
          pass 

        with C: 
          pass 

        with S: 
            link = st.text_input('The URL link') 
            st.session_state.result = give_it_here(link)

            if st.session_state.result == True: 
              if st.session_state.result == 'Your link is not proper!': 
                st.error("Check the link") 

            if st.checkbox('Start the Engine!'): 
              if st.session_state.result == 'SINGLE': 
                single_dataframe = si()
              if st.session_state.result == 'CHANNEL': 
                single_dataframe = ci()
              if st.session_state.result == 'PLAYLIST': 
                single_dataframe = pi()

            st.session_state.s_q = st.text_area("Enter the Query/ Question")

            if st.button('process'): super(st.session_state.s_q, single_dataframe)
            
