import pickle
from pathlib import Path
import streamlit as st
from PIL import Image
from PIL import ExifTags
import pandas as pd
import streamlit_authenticator as stauth

st.set_page_config(layout="wide")

#Load logo
image = Image.open('IronSkyLogo.png')

#Columns for logo (only col2 being used)
col1, col2, col3 = st.columns(3)
with col2:
    st.image(image, caption='', width=500) #load logo to streamlit

#define users
names = ["Peter Parker", "Rebecca Miller"]
usernames = ["pparker", "rmiller"]

#encrypted passwords 
file_path = "hashed_pw.pkl"

#Initialize hashed_passwords
hashed_passwords = None
with open(file_path, "rb") as file:
    hashed_passwords = pickle.load(file)

#load each user with its own info
credentials = {
    'usernames': {
        'pparker': {
            'name': names[0],
            'password': hashed_passwords[0]
        },
        'rmiller': {
            'name': names[1],
            'password': hashed_passwords[1]
        }
    }
}

#Authenticator
authenticator = stauth.Authenticate(credentials, "mycookies", "mycookieskey", 0)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("User/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status: #true
   #converting coordinates
    def find_location_on_map(image):
        try:
            exif = {ExifTags.TAGS[k]:v
                    for k, v in image._getexif().items()
                    if k in ExifTags.TAGS
                    }
            gps_info = exif['GPSInfo']
            north = gps_info[2]
            east = gps_info[4]
            lat = ((((north[0] * 60) + north[1]) * 60) + north[2]) /60 /60 
            lang = ((((east[0] * 60) + east[1]) * 60) + east[2]) /60 /60
            return float(lat), float(lang) 
        except:
            return None, None


    st.markdown(f"<h1 style='text-align: center; color: white;'> Photo GPS Locator Tool </h1>",
                            unsafe_allow_html=True)

    uploaded_image = st.file_uploader("Upload an Image", accept_multiple_files=True)

    image_col, action_col, map_col = st.columns([2.5,2,3])

    with image_col:
        if len(uploaded_image) != 0:
            st.image(uploaded_image, caption=['' for _ in uploaded_image], width=400)

    with action_col:
        st.markdown(
            f"<h5 style='text-align: left; color: white;'> Please follow the steps below:  </h5>",
            unsafe_allow_html=True)
        st.markdown(
            f"<h5 style='text-align: left; color: white;'> 1. Upload an image or multiple images  </h5>",
            unsafe_allow_html=True)
        st.markdown(f"<h5 style='text-align: left; color: white;'> 2. Click on the button below  </h5>",
                    unsafe_allow_html=True)
        genearate_button = st.button('Find on map')

    if genearate_button:
        with map_col:
            if len(uploaded_image) != 0:
                lat = []
                lang = []
                for i in range(len(uploaded_image)):
                    img2 = Image.open(uploaded_image[i])
                    _lat, _lang = find_location_on_map(img2)
                    lat.append(_lat)
                    lang.append(_lang)
                if lat:
                    df = pd.DataFrame({'lat': lat, 'lon':lang})
                    df = df.dropna()
                    st.map(df, size=20)
                    if len(uploaded_image) != len(df):
                          st.markdown(
                        f"<h5 style='text-align: left; color: white;'> ⚠️ GPS info is missing  </h5>",
                        unsafe_allow_html=True)
    
    authenticator.logout("Logout", "main")

