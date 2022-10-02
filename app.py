import pyrebase, requests 
import streamlit as st 
import streamlit as st, os, json, re   
from streamlit_lottie import st_lottie  
from streamlit_option_menu import option_menu  ##

from utils import load_lottie, give_it_here
from playlist import SemanticSearch  

def super_(query, dataframe): 
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

def check_email(email):
  regex = r'\b[A-Za-z0-9._%+-]+@gmail.com'
  if(re.fullmatch(regex, email)):
    return True 
  else: return False

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

#st.sidebar.image('https://i.pinimg.com/736x/4e/2f/80/4e2f808cd07610cea05ffdac6244871d.jpg', width = 130)
st.sidebar.subheader('Main Menu')

st.sidebar.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7bcf,#2e7bcf);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True,
)

# authentication for the user
choice = st.sidebar.selectbox('login/singup', ['Login', 'Sign up'])
email = st.sidebar.text_input("Please enter your email address") 

# checking email is proper or not! 
if email: 
  if check_email(email) == False:  
    st.error('Please enter valid email address!')
    st.stop()

password = st.sidebar.text_input("please enter your password", type = 'password')


# sign up configuration 
if choice == 'Sign up': 
  handle = st.sidebar.text_input("Please input your handle name", placeholder = 'Enter your username')
  submit = st.sidebar.button('Create my account!')

  if submit: 
    # handling user sign in 
    try: 
      user = auth.create_user_with_email_and_password(email, password)  # creating a account with username and password 
      st.success("Your account is created succesfully!")
    except requests.HTTPError as exception:
      if "WEAK_PASSWORD" in str(exception): 
        st.info("Your password is too weak. Try different password")
        st.markdown("If you have doubt in creating strong password. Visit this [website](https://1password.com/password-generator/)", True)
        st.stop()

    # sign in 
    user = auth.sign_in_with_email_and_password(email, password)
    db.child(user['localId']).child("Handle").set(handle)
    db.child(user['localId']).child("ID").set(user['localId'])
    
    st.title("Welcome " + handle)
    st.info("Your account succesfully created. Now you can login!")

if choice == 'Login':
    login = st.sidebar.checkbox('Login')
    if login:

        try: 
          user = auth.sign_in_with_email_and_password(email,password)
        except requests.HTTPError as exception:
          go = str(exception)

          if "INVALID_PASSWORD" in go: 
            st.error('Password in In-Correct ⚠️')
            st.caption('If you forgot try contact us otherwise many attempt lead your account to be disabled for safety purpose!')
            st.stop()
            


        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)  # it writes in horizontal way instead of vertical way! 

        #################################### APP ####################################
        H, S, C = st.tabs(['HOME', 'SMART SEARCH', 'CONTACT'])  # creating tab 

        with H: 
          st.header("Smart Search Home Page!")
          load_lottie('https://assets1.lottiefiles.com/packages/lf20_M9p23l.json', height = 500, width = 500)
          st.markdown("""<p> Welcome to Smart Search, this app helps you to search through the videos.</p> 
                         <p> Go to smart search section and start searching.</p> 
                         <b>If you have any query you can specify that in contact section </b>""", True) 

        with C: 
          st.header(":mailbox: Get Touch With Us!")
          contact_form = """
          <form action="https://formsubmit.co/quickzam.ai@gmail.com" method="POST">
               <input type="hidden" name="_captcha" value="false">
               <input type="text" name="name" placeholder="Your name" required>
               <input type="email" name="email" placeholder="Your email" required>
               <textarea name="message" placeholder="Your message here"></textarea>
               <button type="submit">Send</button>
          </form>
          """
          st.markdown(contact_form, unsafe_allow_html=True)
          def local_css(file_name):
            with open(file_name) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

          local_css("style/style.css")

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

            if st.button('process'): 
              try: 
                super_(st.session_state.s_q, single_dataframe)
              except NameError: 
                st.error("Try to toggle on Start Engine Button! This is because you off the start engine button!")
