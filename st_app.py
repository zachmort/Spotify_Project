import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
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
    # client_id = st.secrets["client_id"]
    # client_secret = st.secrets["client_secret"]
    # uri = st.secrets["uri"]
    uri = "http://localhost:8501/"
    # client_id = "xxxxxx"
    # client_secret = "xxxxxx"
    client_id = "1a03d057b2754e71a51fb53f7ea86a89"
    client_secret = "4cda91e66f034fabbe4da84727015f3c"
    # set scope and establish connection
    scopes = " ".join(["user-read-private",'user-library-read', 'user-top-read'])
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
            login_button = st.button('Login with Spotify', link_html, type="primary")
        with col3 : pass
    # login_button = st.button('Login with Spotify', link_html, type="primary")
        if login_button==True:
            col1, col2, col3 = st.columns(3)
            with col1: pass
            with col2:
                st.markdown(link_html, unsafe_allow_html=True)
            with col3 : pass
            st.divider()


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
    time.sleep(2)
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


    if token == None:    
        sp=spotipy.Spotify(st.session_state["cached_token"])
    else:
        sp=spotipy.Spotify(token)
        user= sp.current_user()
        user_name = user["display_name"]
        st.header(f"Hello! {user_name}")

    # try: 
    #     if token == None:    
    #         sp=spotipy.Spotify(st.session_state["cached_token"])
    # except Exception as e:
    #     sp=spotipy.Spotify(token)
    #     user= sp.current_user()
    #     user_name = user["display_name"]
    #     st.header(f"Hello! {user_name}")

######################################################################################################################################################
# DATA GATHERING
######################################################################################################################################################

    def generate_chunks():
        chunkList = []
        # for i in range(0, 5001, 50):
        for i in range(0, 201, 50):
            chunkList.append(i)
        return chunkList

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
                placeholer.text(f"{int(percent_complete)}%")
            time.sleep(1)
            placeholer.empty()
            my_bar.empty()
            return full_list
        except Exception as e:
            print("error with processing")

    # def run_api_call():
    #     try:
    #         incs_50 = generate_chunks()
    #         p = Pool(processes=4)
    #         results = p.map(loopthrough, incs_50)
    #         return results
    #     except Exception as e:
    #         print(e)

    # data = run_api_call()
    # st.write(data)
        


    def load_user_saved_tracks_data():
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


    def summary_metrics(df: pd.DataFrame):
        """ Provides summary stats for user liked songs playlist"""
        total_playlist_length_hours = round((df["song_length_seconds"].sum())/(1000),1) 
        distinct_artist_count = len(df['unique_artist_id'].unique())
        total_songs = len(df)
        df_explicit = ((df.groupby(['song_explicit']).count()/len(df))*100).reset_index()
        df_explicit = df_explicit.rename(columns={'added_to_playlist_time':'explicit_%'})
        df_explicit['explicit_%'] = round(df_explicit['explicit_%'], 1)

        return (total_playlist_length_hours, distinct_artist_count, total_songs, df_explicit)

    # Throw all of this into a container that houses each section of my page
    with st.container():
        st.markdown("""<style>
                        div[data-testid="column"]:nth-of-type(1)
                        {text-align: center;} 
                        div[data-testid="column"]:nth-of-type(2)
                        {text-align: center;}
                        div[data-testid="column"]:nth-of-type(3)
                        {text-align: center;
                        div[data-testid="column"]:nth-of-type(4)
                        {text-align: center;
                        div[data-testid="column"]:nth-of-type(5)
                        {text-align: center;
                        }     </style>""",unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.subheader(summary_metrics(track_details_df)[0])
        c2.subheader(summary_metrics(track_details_df)[1])
        c3.subheader(f"total_songs {summary_metrics(track_details_df)[2]}")
        c4.subheader(summary_metrics(track_details_df)[3])
        c5.subheader(summary_metrics(track_details_df)[1])

    # tuple_metrics = summary_metrics(dataframe_temp)
    # total_playlist_length_hours = tuple_metrics[0]
    # col1, col2, col3 = st.columns(3)
    # col1.metric("Playlist Length (hours)", f"{total_playlist_length_hours}")
    # col2.metric("Total Distinct Artists", f"{distinct_artist_count}")
    # col3.metric("Total Songs", f"{total_songs}")

    # #Plotting most recent artists on page
    # st.write("## Most Recently Added Artists!")
    # most_recent_5_songs = df.loc[:50,['artist_name','artist_image']]
    # st.image(list(most_recent_5_songs.artist_image.unique()[0:5]), caption=list(most_recent_5_songs.artist_name.unique()[0:5]))


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
        # top_5_dict = {k:f"{v}%" for k, v in top_5_dict.items()}
        return top_5_dict
    
    long_df = pd.DataFrame(genre_metrics(results_top_user_items_long_dict), index=[0])
    short_df = pd.DataFrame(genre_metrics(results_top_user_items_short_dict), index=[0])


    with st.container():
        fig = make_subplots(
        cols = 2, rows = 1,column_widths = [1, 1],
        subplot_titles = ("Short term Artist Genre Stats" ,"Long term Artist Genre Stats"),
        specs = [[{'type': 'treemap', 'rowspan': 1}, {'type': 'treemap'}]])

        fig.add_trace(go.Treemap(
            # TODO 
            # DONE # make text in each box bigger
            # DONE #  add "%" sign to each number
            # Add description to the top of this section
            # DONE #Add section to a container
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

        fig.update_layout(  width=1500,height=750 
                            ,margin=dict(l=20, r=20, t=20, b=20)
                            ,     font=dict(family="Courier New, monospace",
                                                size=18)
                            , yaxis_tickformat = '%'
                                )
        st.plotly_chart(fig, use_container_width=True)


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
                                st.image(artist_image[index], width=250 )
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
        tab_formatting(top10_artists_images, top10_artists_names, top10_artists_rating)

    with tab2:
        st.header("You have stuck with these artists throughout your listening journey")
        tab_formatting(common_10_images, common_10_names, common_10_pop_rating)



############ IDEAS #############
#TODO DONE
# top 20 artists all time (grid with pics)
#TODO DONE
# (do a comparision of the top 20 artists from long term vs short term (show pics of the artists that appear in both and write a little description that tsalks about how consistent or nostalgic these artists are for you))
#TODO DONE
# Most recent moods for music  ()

# Most recently played tracks (count freq of top 200 and see what people are listening to the most)
    # Artist pop (highest 5 lowest 5)
#

# # song explicit % of all songs with a true and false banner with %s below each
# st.write(df_explicit.loc[:, ['song_explicit', 'explicit_%']])
# bar_chart_explicit= px.bar(data_frame=df_explicit, x='song_explicit', y='explicit_%', template="ggplot2")
# st.plotly_chart(bar_chart_explicit)
# # st.bar_chart(data=df_explicit, x='song_explicit', y='explicit_%')



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
