import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np
import time
from streamlit.components.v1 import html
import os
from collections import Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from itertools import islice
from multiprocessing import Pool


######################################################################################################################################################
# Login page via spotipy module
######################################################################################################################################################

# SETTING PAGE CONFIG TO WIDE MODE AND ADDING A TITLE AND FAVICON
st.set_page_config(layout="wide", page_title="Music Metrics")

col1, col2, col3 = st.columns(3)
with col1:
    pass
with col2:
    st.title("Take a dive into your music listening metrics!")
with col3 :
    pass


def get_token(oauth, code):
    try:
        token = oauth.get_access_token(code, as_dict=False, check_cache=True)
        # return the token
        return token
    except Exception as notoken:
        st.error("token not here?")
        st.write(notoken)


def sign_in(token):
    sp = spotipy.Spotify(auth=token)
    return sp


def app_get_token():
    try:
        token = get_token(st.session_state["oauth"], st.session_state["code"])
        st.session_state["cached_token"] = token
    except Exception as e:
        st.error("An error occurred during token retrieval!")
        st.write("The error is as follows:")
        st.write(e)
    else:
        st.session_state["cached_token"] = token
    return token
        

def app_sign_in():
    try:
        token = st.session_state["cached_token"]
        sp = sign_in(token)
    except Exception as e:
        st.error("An error occurred during sign-in!")
        st.write("The error is as follows:")
        st.write(e)
    else:
        st.session_state["signed_in"] = True
        app_display_welcome()

    return sp


def app_display_welcome():
    # import secrets from streamlit deployment
    client_id = st.secrets["client_id"]
    client_secret = st.secrets["client_secret"]
    uri = st.secrets["uri"]
    # set scope and establish connection
    scopes = " ".join(["user-read-private",'user-library-read', 'user-top-read', 'playlist-read-private', 'playlist-read-collaborative'])
    # create oauth object
    oauth = SpotifyOAuth(scope=scopes,redirect_uri=uri,client_id=client_id,client_secret=client_secret)
    # store oauth in session
    st.session_state["oauth"] = oauth
    # retrieve auth url
    auth_url = oauth.get_authorize_url()
    link_html = " <a target=\"_self\" href=\"{url}\" >{msg}</a> ".format(url=auth_url,msg="Click me to authenticate!")
    if not st.session_state["signed_in"]:
    # st.markdown("<h1 style='text-align: center; color: red;'>Some title</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: pass
        with col2:
            st.write(" ".join(["No tokens found for this session. Please log in by",
                        "clicking the link below."]))
            st.write(" ".join(["If you do not have a spotify account please use the 'Example Dash' button to view what this dashboard would look like!"]))
            login_button = st.button('Login with Spotify', link_html, type="primary")
            # login_button = st.link_button('Login with Spotify', link_html, type="primary")
            exampledashbutton = st.button('Example Dash', type="primary", key="example")
        with col3 : pass            

        if login_button==True:
            col1, col2, col3 = st.columns(3)
            with col1: pass
            with col2:
                st.markdown(link_html, unsafe_allow_html=True)
            with col3 : pass
            st.divider()
        if exampledashbutton==True: pass


if "signed_in" not in st.session_state:
    st.session_state["signed_in"] = False
if "cached_token" not in st.session_state:
    st.session_state["cached_token"] = ""
if "code" not in st.session_state:
    st.session_state["code"] = ""
if "oauth" not in st.session_state:
    st.session_state["oauth"] = None

url_params = st.experimental_get_query_params()

# attempt sign in with cached token
if st.session_state["cached_token"] != "":
    sp = app_sign_in()
    # st.write("current state")
# if no token, but code in url, get code, parse token, and sign in
elif "code" in url_params:
    # all params stored as lists, see doc for explanation
    # st.write("does this get hit?")
    st.session_state["code"] = url_params["code"][0]
    sp = app_sign_in()
    token=app_get_token()
    st.session_state["cached_token"] = token
else:
    app_display_welcome()

if st.session_state["signed_in"]:
    suc = st.success("Sign in success!")
    # time.sleep(2)
    suc.empty()
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    placeholer = st.empty()

    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
        placeholer.text(f"{int(percent_complete)}%")
    placeholer.empty()
    time.sleep(1)
    my_bar.empty()

    token = None
    if token == None:    
        sp=spotipy.Spotify(st.session_state["cached_token"])
    else:
        sp=spotipy.Spotify(token)
        user= sp.current_user()
        current_user_id = user["id"]
        st.session_state["cached_current_user_id"] = current_user_id
        user_name = user["display_name"]
        st.header(f"Hello! {user_name}")

######################################################################################################################################################
# DATA GATHERING
######################################################################################################################################################

    def generate_chunks():
        chunkList = []
        # for i in range(0, 5001, 50):
        for i in range(0, 201, 50):
            chunkList.append(i)
        return chunkList

    @st.cache_data
    def loopthrough():
        try:
            incs_50 = generate_chunks()
            full_list = []
            progress_text = "Gathering your data! Please wait!"
            my_bar = st.progress(0, text=progress_text)
            placeholer=st.empty()
            for index, i in enumerate(incs_50):
                time.sleep(0.001)
                my_bar.progress(i/500, text=progress_text)
                results = sp.current_user_saved_tracks(offset=i, limit=50)
                full_list.append(results)
                placeholer.text(f"{i/500}%")
            time.sleep(1)
            placeholer.empty()
            my_bar.empty()
            return full_list
        except Exception as e:
            print(e, "error with processing")

###########
#TODO implement either async tasks or api calls in parallel
###########
    # def run_api_call():
    #     try:
    #         with Pool(processes=5) as p:
    #             incs_50 = generate_chunks()
    #             results = p.apply_async(loopthrough, incs_50)
    #             print(results.get(timeout=1))
    #             p.close()
    #             st.write("Process Finished")
    #         return results
    #     except Exception as e:
    #         print(e)

    # data = run_api_call()
    # st.write(data)
        

    @st.cache_data
    def load_user_saved_tracks_data():
        """
        This calls the loopthrough function and parses all of the returned data into a dictionary with the song_uri as the key for each entry
        """
        data = loopthrough()
        saved_tracks_parsed={}
        for index_i, i in enumerate(data):  
            for index_j, j in enumerate(data[index_i]["items"]):
                saved_tracks_parsed[j["track"]["uri"]] = {
                    "added_to_playlist_time":j["added_at"]
                    , "artist_name":j["track"]["album"]["artists"][0]["name"]
                    , "artist_image":j['track']['album']['images'][1]['url']
                    , "unique_artist_id": j["track"]["album"]["artists"][0]["uri"]
                    , "release_date": j["track"]["album"]["release_date"]
                    , "song_name": j["track"]["name"]
                    , "song_length_seconds": int(j["track"]["duration_ms"])/1000
                    , "song_explicit": str(j["track"]["explicit"])
                    , "song_linkId": j["track"]["external_urls"]["spotify"]
                    , "song_popularity": int(j["track"]["popularity"])
                    , "album_name": j["track"]["album"]["name"]
                    , "spotify_uri_album": j["track"]["album"]["uri"]
                    , "spotify_track_id": j["track"]["id"]  }

        return saved_tracks_parsed


    track_data_dict=load_user_saved_tracks_data()
    track_data_prep=list(track_data_dict.values())
    track_details_df =pd.DataFrame(track_data_prep)

    @st.cache_data
    def summary_metrics(df: pd.DataFrame):
        """ Provides summary stats for user liked songs playlist"""
        total_playlist_length_hours = round((df["song_length_seconds"].sum())/(1000),1) 
        distinct_artist_count = len(df['unique_artist_id'].unique())
        total_songs = len(df)
        avg_song_pop = df["song_popularity"].mean()
        df_explicit = ((df.groupby(['song_explicit']).count()/len(df))*100).reset_index()
        df_explicit = df_explicit.rename(columns={'added_to_playlist_time':'explicit_%'})
        df_explicit['explicit_%'] = round(df_explicit['explicit_%'], 1)
        explicitmetric = df_explicit.loc[: ,['explicit_%'] ]

        return (total_playlist_length_hours, distinct_artist_count, total_songs, explicitmetric, avg_song_pop)

    st.write("")
    st.write("")
    with st.container():
        st.markdown("""<style>
                        div[data-testid="column"]:nth-of-type(1)
                        {text-align: center;} 
                        div[data-testid="column"]:nth-of-type(2)
                        {text-align: center;}
                        div[data-testid="column"]:nth-of-type(3)
                        {text-align: center;}
                        div[data-testid="column"]:nth-of-type(4)
                        {text-align: center;}
                        div[data-testid="column"]:nth-of-type(5)
                        {text-align: center;}
                        div[data-testid="column"]:nth-of-type(6)
                        {text-align: center;} 
                        div[data-testid="column"]:nth-of-type(7)
                        {text-align: center;}
                        div[data-testid="column"]:nth-of-type(8)
                        {text-align: center;}
                        div[data-testid="column"]:nth-of-type(9)
                        {text-align: center;}
                        div[data-testid="column"]:nth-of-type(10)
                        {text-align: center;}
                             </style>""",unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.subheader("Playlist Length (hours)")
        c1.divider()
        c1.subheader(summary_metrics(track_details_df)[0])
        c2.subheader("Total Unique Artists")
        c2.divider()
        c2.subheader(summary_metrics(track_details_df)[1])
        c3.subheader("Total Songs")
        c3.divider()
        c3.subheader(summary_metrics(track_details_df)[2])
        c4.subheader("Explicit Song %")
        c4.divider()
        c4.subheader(f"{str(pd.DataFrame(summary_metrics(track_details_df)[3]).values[0])}%")
        c5.subheader("Avg Song Popularity")
        c5.divider()
        c5.subheader(round(summary_metrics(track_details_df)[4]))
        st.write("")
        st.write("")
        st.write("")
        st.write("")


    def get_top_user_tracks(limit, offset, length):
        data = sp.current_user_top_tracks(limit=limit, offset=offset, time_range=length)
        return data
    

    def get_top_user_artists(limit, offset, length):
        data = sp.current_user_top_artists(limit=limit, offset=offset, time_range=length)
        return data
        
    top_user_artists_long = get_top_user_artists(50, 0, "long_term")
    top_user_artists_short = get_top_user_artists(50, 0, "short_term")


    def genres_data(df):
        genre_list={i["name"]:i["genres"] for i in df['items']}
        return genre_list
    
    results_top_user_items_short_dict = genres_data(top_user_artists_short)
    results_top_user_items_long_dict = genres_data(top_user_artists_long)

    @st.cache_data
    def genre_metrics(given_dict):
        genre_sublists = given_dict.values()
        genre_list = [genre for sublist in genre_sublists for genre in sublist]
        # distinct_genres = len(set(genre_list))
        total_genres = len(genre_list)
        temp = Counter(genre_list)
        final_percs = {key:round((value/total_genres)*100,2) for key, value in temp.items()}
        final = dict(sorted(final_percs.items(), key=lambda x:x[1],  reverse=True))
        top_5_genres = [i for i in final.keys()][:10]
        top_5_dict = {k: final[k] for k in top_5_genres}
        other_dict_temp = {k: final[k] for k in final if k not in top_5_genres}
        other_dict = {"other": round(sum(other_dict_temp.values()),2) }
        top_5_dict.update(other_dict)
        return top_5_dict
    
    long_df = pd.DataFrame(genre_metrics(results_top_user_items_long_dict), index=[0])
    short_df = pd.DataFrame(genre_metrics(results_top_user_items_short_dict), index=[0])


    with st.container():
        fig = make_subplots(
        cols = 2, rows = 1,column_widths = [1, 1],
        subplot_titles = ("Short term Artist Genre Stats" ,"Long term Artist Genre Stats"),
        specs = [[{'type': 'treemap', 'rowspan': 1}, {'type': 'treemap'}]])

        fig.add_trace(go.Treemap(
            labels = short_df.columns,
            parents=["Short", "Short", "Short", "Short", "Short", "Short", "Short", "Short", "Short", "Short", "Short"],
            values = short_df.values.flatten(),
            textinfo = "label+percent parent",
            root_color="lightgrey"),row = 1, col = 1)

        fig.add_trace(go.Treemap(
            labels = long_df.columns,
            parents=["Long", "Long", "Long", "Long", "Long", "Long", "Long", "Long", "Long", "Long", "Long"],
            values = long_df.values.flatten(),
            textinfo = "label+percent parent",
            root_color="lightgrey", ),row = 1, col = 2)

        fig.update_layout(  width=1300,height=650 
                            ,margin=dict(l=20, r=20, t=20, b=20)
                            ,     font=dict(family="Courier New, monospace",
                                                size=18)
                            , yaxis_tickformat = '%'
                                )
        st.plotly_chart(fig, use_container_width=True)
        st.write("")

    @st.cache_data
    def get_top_50_artists(df):
        artist_info_dict = {}
        for i in df["items"]:
            artist_info_dict[i["uri"]] =[
              i["name"]
            , i["images"][2]["url"]
            , i["popularity"]]
        return artist_info_dict


    long_df_artists = get_top_50_artists(top_user_artists_long)
    short_df_artists = get_top_50_artists(top_user_artists_short)
    
    def take(n, iterable):
        """Return the first n items of the iterable as a list."""
        return dict(islice(iterable.items(), n))

    long_term_top_10 = take(10, long_df_artists)
    short_term_top_10 = take(10, short_df_artists)

    top10_artists_names = []
    top10_artists_rating = []
    top10_artists_images = []
    for k,v  in long_df_artists.items():
        top10_artists_names.append(v[0])
        top10_artists_rating.append(v[2])
        top10_artists_images.append(v[1])


    common_list=[]
    for i in long_term_top_10.keys():
        if i in short_term_top_10.keys():
            common_list.append(i)
    

    short_long_common_artists = {}
    for k, v in long_term_top_10.items():
        if k in common_list:
            short_long_common_artists[k] = v
    
    common_10_names = []
    common_10_images = []
    common_10_pop_rating = []
    for k,v  in short_long_common_artists.items():
        common_10_names.append(v[0])
        common_10_images.append(v[1])
        common_10_pop_rating.append(v[2])

    @st.cache_data
    def tab_formatting(artist_image: list, artist_name: list, artist_pop: list):
                with st.container():
                    st.markdown("""<style>
                        div[data-testid="column"]:nth-of-type(1)
                        {text-align: center;} 
                        div[data-testid="column"]:nth-of-type(2)
                        {text-align: center;}
                        div[data-testid="column"]:nth-of-type(3)
                        {text-align: center;
                        }     </style>""",unsafe_allow_html=True)
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c2.subheader("Artist Photo")
                    c3.subheader("Artist Name")
                    c4.subheader("Artist Popularity")
                    for index, artist in enumerate(artist_image[:5]):
                        cs1, cs2, cs3, cs4, cs5 = st.columns(5)
                        with st.container():
                            st.markdown("""<style> div[data-testid="column"]:nth-of-type(2)
                        {text-align: center;} 
                        div[data-testid="column"]:nth-of-type(3)
                        {text-align: center;}
                        div[data-testid="column"]:nth-of-type(4)
                        {text-align: center;}     </style>""",unsafe_allow_html=True)
                            with cs2: 
                                st.image(artist_image[index], width=220, )
                            with cs3:
                                st.write(" ")
                                st.write(" ")
                                st.write(" ")
                                st.write(" ")
                                st.write(" ")
                                st.subheader(artist_name[index])
                            with cs4:
                                st.write(" ")
                                st.write(" ")
                                st.write(" ")
                                st.write(" ")
                                st.write(" ")
                                st.subheader(artist_pop[index])

    tab1, tab2 = st.tabs(["Top Artists All Time","Artist You Can't Get Enough of"])

    with tab1:
        st.header("Artists you are rocking with right now")
        st.write("This is a list of the artosts you are listning to most right now!")
        tab_formatting(top10_artists_images, top10_artists_names, top10_artists_rating)

    with tab2:
        st.header("You have stuck with these artists throughout your listening journey")
        st.write("This tab takes a look at your total listening history and compares your most listened artist with the artsts you are listening to today. Any artists that appear in both get placed here!")
        tab_formatting(common_10_images, common_10_names, common_10_pop_rating)


    @st.cache_data
    def get_user_playlists():
        results = sp.current_user_playlists(offset=0, limit=50)
        df= pd.json_normalize(results["items"],
                            meta=["name", "public","collaborative", ["tracks", "total"]])

        return df

    user_playlist_data = get_user_playlists()
    # st.write(user_playlist_data)

    @st.cache_data
    def playlist_selected_metrics(playlist_name_chosen):
        selected_playlist_data = user_playlist_data.loc[user_playlist_data["name"]==playlist_name_chosen]
        name_playlist = selected_playlist_data["name"]
        public_flag_playlist = selected_playlist_data["public"]
        return selected_playlist_data

    with st.form("Playlist Form", clear_on_submit=False):
        col_playlist_dropdown, col_numeric_data_1, col_numeric_data_2 = st.columns(3)
        list_playlists = user_playlist_data["name"].unique()
        datacols = user_playlist_data.loc[ :,:]
        col_playlist_dropdown.selectbox('Select Playlist', list_playlists, key="playlist_name")
        playlist_name_chosen = str(st.session_state["playlist_name"])
        submitted = st.form_submit_button("Confirm Playlist")

        if submitted:
            playlist_results = playlist_selected_metrics(playlist_name_chosen)
            playlist_id = playlist_results.iloc[0]["id"]
            playlist_track_results = sp.playlist_items(playlist_id=str(playlist_id), limit=100, offset=0)
            st.write(playlist_track_results)


        





# ### Creating Artist Form for scatter plot data
# st.write("## Artist Choser Form")
# with st.form("entry_form", clear_on_submit=False):
#     col_artist_dropdown, col_numeric_data_1, col_numeric_data_2 = st.columns(3)
#     list_distinct_artists = df["artist_name"].unique()
#     datacols = df.loc[ :,'danceability':]
#     datacols['song_popularity'] = df['song_popularity']
#     col_artist_dropdown.selectbox('Select Artist', list_distinct_artists, key="artist_name")
#     col_numeric_data_1.selectbox('Select Data Column for X Axis', datacols.columns, key="datapoint1")
#     col_numeric_data_2.selectbox('Select Data Column for Y Axis', datacols.columns, key="datapoint2")
#     submitted = st.form_submit_button("Select Artist")
#     if submitted:
#         artist_chosen = str(st.session_state["artist_name"])
#         data_col_1_chosen = str(st.session_state["datapoint1"])
#         data_col_2_chosen = str(st.session_state["datapoint2"])
#         st.write(f"A scatter plot of my saved {artist_chosen} songs {data_col_1_chosen} and {data_col_2_chosen}!")
#         data_filtered_artist = df[df["artist_name"]== str(artist_chosen)]
#         histogram_fig = px.scatter(data_frame=data_filtered_artist, x=data_col_1_chosen
#                                                 , y=data_col_2_chosen
#                                                 , color=data_filtered_artist['album_name']
#                                                 , labels=dict(x=data_col_1_chosen, y=data_col_2_chosen))
#         histogram_fig.update_layout(height=650,width=1000, showlegend=False)
#         st.plotly_chart(histogram_fig,height=650, width=1000)
#         # st.plotly_chart(histogram_fig)


# ### Creating Artist Form for Radar Plot data
# st.write("## Artist Radar Plot Form")
# with st.form("radar_entry_form", clear_on_submit=False):
#     # TODO: #Create a form drop down that allow susers to select given artists and then plot scatter plots with color as album name
#     col_artist_dropdown_radar= st.columns(1)
#     list_distinct_artists = df["artist_name"].unique()
#     datacols = df.loc[ :,'danceability':]
#     datacols['song_popularity'] = df['song_popularity']
#     st.selectbox('Select Artist', list_distinct_artists, key="artist_name_radar")
#     submitted_radar = st.form_submit_button("Select Artist")
#     if submitted_radar:
#         artist_chosen = str(st.session_state["artist_name_radar"])
#         st.write(f"A Radar plot of {artist_chosen}'s songs VS the avg of all songs in my liked songs")
#         data_filtered_artist = df[df["artist_name"]== str(artist_chosen)]
#         data_filtered_artist_agg = data_filtered_artist.groupby(["artist_name", "unique_artist_id"]).mean(numeric_only=True).reset_index()
#         df["temp"] = "tempval"
#         data_agg = df.groupby(["temp"]).mean(numeric_only=True).reset_index()
#         data_agg_final = data_agg[['danceability', 'energy', 'speechiness','acousticness', 'instrumentalness', 'liveness', 'valence']]
#         data_filtered_artist_agg_final = data_filtered_artist_agg[['danceability', 'energy', 'speechiness','acousticness', 'instrumentalness', 'liveness', 'valence']]
#         fig = go.Figure()
#         fig.add_trace(go.Scatterpolar(
#             r=(data_filtered_artist_agg_final.values).flatten()
#             , theta=list(data_filtered_artist_agg_final.columns)
#             , fill="toself"
#             , name=f'Avg {artist_chosen} Song Metrics'
#             , marker = {'color' : 'red'}
#         ))
#         fig.add_trace(go.Scatterpolar(
#             r=(data_agg_final.values).flatten()
#             , theta=list(data_agg_final.columns)
#             , fill="toself"
#             , name='Avg Song Metrics'
#             , marker = {'color' : 'blue'}
#         ))
#         fig.update_layout(
#         polar=dict(
#             radialaxis=dict(
#             visible=True,
#             range=[0, 1]
#             )),
#         showlegend=True)
#         fig.update_layout(height=650,width=1500, showlegend=True)
#         st.plotly_chart(fig,height=650, width=1000)


# # Plotting avg time difference to add songs
# # st.write(pd.to_datetime(df['added_to_playlist_time']).dt.strftime("%Y-%m-%d"))
# # added_time = pd.to_datetime(df['added_to_playlist_time']).dt.strftime("%Y-%m-%d") 
# # release_time = pd.to_datetime(df['release_date']).dt.strftime("%Y-%m-%d")
# # st.write(pd.to_datetime(added_time) - pd.to_datetime(release_time))
# # st.write(pd.to_datetime(release_time))
