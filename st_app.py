import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go



# SETTING PAGE CONFIG TO WIDE MODE AND ADDING A TITLE AND FAVICON
st.set_page_config(layout="wide", page_title="Spotify Data")

# Loading Data
@st.cache_data
def load_data(path: str):
    data = pd.read_csv(path)
    return data

df=load_data("song_data.csv")
df2 = df.copy()
df2.columns = df2.columns.str.replace('_', ' ')
df2.columns = df2.columns.str.capitalize()

# Plotting Ttile Text on page
st.title("My Spotify Saved Songs Web App!")

# Summary Stats
total_playlist_length_hours = round((df["song_length_seconds"].sum())/(1000),1) 
distinct_artist_count = len(df['unique_artist_id'].unique())
total_songs = len(df)
col1, col2, col3 = st.columns(3)
col1.metric("Playlist Length (hours)", f"{total_playlist_length_hours}")
col2.metric("Total Distinct Artists", f"{distinct_artist_count}")
col3.metric("Total Songs", f"{total_songs}")

# song explicit % of all songs with a true and false banner with %s below each
df_explicit = ((df.groupby(['song_explicit']).count()/len(df))*100).reset_index()
df_explicit = df_explicit.rename(columns={'added_to_playlist_time':'explicit_%'})
df_explicit['explicit_%'] = round(df_explicit['explicit_%'], 1)
st.write(df_explicit.loc[:, ['song_explicit', 'explicit_%']])
bar_chart_explicit= px.bar(data_frame=df_explicit, x='song_explicit', y='explicit_%', template="ggplot2")
st.plotly_chart(bar_chart_explicit)
# st.bar_chart(data=df_explicit, x='song_explicit', y='explicit_%')


# Plotting Data frame on Page
#TODO: add a multiselect to allow users to change data views
st.dataframe(df2)


### Creating Artist Form for scatter plot data
st.write("## Artist Choser Form")
with st.form("entry_form", clear_on_submit=False):
    col_artist_dropdown, col_numeric_data_1, col_numeric_data_2 = st.columns(3)
    list_distinct_artists = df["artist_name"].unique()
    datacols = df.loc[ :,'danceability':]
    datacols['song_popularity'] = df['song_popularity']
    col_artist_dropdown.selectbox('Select Artist', list_distinct_artists, key="artist_name")
    col_numeric_data_1.selectbox('Select Data Column for X Axis', datacols.columns, key="datapoint1")
    col_numeric_data_2.selectbox('Select Data Column for Y Axis', datacols.columns, key="datapoint2")
    submitted = st.form_submit_button("Select Artist")
    if submitted:
        artist_chosen = str(st.session_state["artist_name"])
        data_col_1_chosen = str(st.session_state["datapoint1"])
        data_col_2_chosen = str(st.session_state["datapoint2"])
        st.write(f"A scatter plot of my saved {artist_chosen} songs {data_col_1_chosen} and {data_col_2_chosen}!")
        data_filtered_artist = df[df["artist_name"]== str(artist_chosen)]
        histogram_fig = px.scatter(data_frame=data_filtered_artist, x=data_col_1_chosen
                                                , y=data_col_2_chosen
                                                , color=data_filtered_artist['album_name']
                                                , labels=dict(x=data_col_1_chosen, y=data_col_2_chosen))
        histogram_fig.update_layout(height=650,width=1000, showlegend=False)
        st.plotly_chart(histogram_fig,height=650, width=1000)
        # st.plotly_chart(histogram_fig)


### Creating Artist Form for Radar Plot data
st.write("## Artist Radar Plot Form")
with st.form("radar_entry_form", clear_on_submit=False):
    # TODO: #Create a form drop down that allow susers to select given artists and then plot scatter plots with color as album name
    col_artist_dropdown_radar= st.columns(1)
    list_distinct_artists = df["artist_name"].unique()
    datacols = df.loc[ :,'danceability':]
    datacols['song_popularity'] = df['song_popularity']
    st.selectbox('Select Artist', list_distinct_artists, key="artist_name_radar")
    submitted_radar = st.form_submit_button("Select Artist")
    if submitted_radar:
        artist_chosen = str(st.session_state["artist_name_radar"])
        st.write(f"A Radar plot of {artist_chosen}'s songs VS the avg of all songs in my liked songs")
        data_filtered_artist = df[df["artist_name"]== str(artist_chosen)]
        data_filtered_artist_agg = data_filtered_artist.groupby(["artist_name", "unique_artist_id"]).mean().reset_index()
        df["temp"] = "tempval"
        data_agg = df.groupby(["temp"]).mean().reset_index()
        data_agg_final = data_agg[['danceability', 'energy', 'speechiness','acousticness', 'instrumentalness', 'liveness', 'valence']]
        data_filtered_artist_agg_final = data_filtered_artist_agg[['danceability', 'energy', 'speechiness','acousticness', 'instrumentalness', 'liveness', 'valence']]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=(data_filtered_artist_agg_final.values).flatten()
            , theta=list(data_filtered_artist_agg_final.columns)
            , fill="toself"
            , name=f'Avg {artist_chosen} Song Metrics'
            , marker = {'color' : 'red'}
        ))
        fig.add_trace(go.Scatterpolar(
            r=(data_agg_final.values).flatten()
            , theta=list(data_agg_final.columns)
            , fill="toself"
            , name='Avg Song Metrics'
            , marker = {'color' : 'blue'}
        ))
        fig.update_layout(
        polar=dict(
            radialaxis=dict(
            visible=True,
            range=[0, 1]
            )),
        showlegend=True)
        fig.update_layout(height=650,width=1500, showlegend=True)
        st.plotly_chart(fig,height=650, width=1000)


#Plotting most recent artists on page
st.write("## Most Recently Added Artists!")
most_recent_5_songs = df.loc[:50,['artist_name','artist_image']]
st.image(list(most_recent_5_songs.artist_image.unique()[0:5]), caption=list(most_recent_5_songs.artist_name.unique()[0:5]))


# Plotting avg time difference to add songs
# st.write(pd.to_datetime(df['added_to_playlist_time']).dt.strftime("%Y-%m-%d"))
added_time = pd.to_datetime(df['added_to_playlist_time']).dt.strftime("%Y-%m-%d") 
release_time = pd.to_datetime(df['release_date']).dt.strftime("%Y-%m-%d")
# st.write(pd.to_datetime(added_time) - pd.to_datetime(release_time))
# st.write(pd.to_datetime(release_time))
