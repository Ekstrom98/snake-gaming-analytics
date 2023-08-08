import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Snake Gaming Analytics",
    page_icon="🐍",
    layout="centered",
)

st.title("Snake Gaming Analytics")
st.markdown("---")

all_games = pd.read_csv("./query_results/get_all_games.csv", 
                        usecols=[0, 1, 2, 3, 4], header=None)
all_games.columns = ['Player', 'Score', 'Collision Type', 'Duration', 'Datetime']


#--------------------------------------------------CREATE TWO COLUMNS--------------------------------------------------#
col1, col2 = st.columns(2)

#---------------PLAYER SELECTION BOX---------------#
# Create a list of player names with an "All Players" option
player_options = ["All players"] + list(all_games['Player'].unique())
# Create a select box with the player options
selected_player = col2.selectbox('Select a player:', player_options)

# Filter the dataframe based on the selected player, unless "All Players" is selected
if selected_player == "All players":
    filtered_games = all_games
else:
    filtered_games = all_games[all_games['Player'] == selected_player]
#--------------------------------------------------#

#-------------------SCORE SLIDER-------------------#
min_score, max_score = col2.slider('Select a score range', 
                                   min_value=all_games['Score'].min(), 
                                   max_value=all_games['Score'].max(), 
                                   value=(all_games['Score'].min(), all_games['Score'].max()))
filtered_games = filtered_games[(filtered_games['Score'] >= min_score) & (filtered_games['Score'] <= max_score)]
#--------------------------------------------------#

#---------------COLLISION TYPE SELECTION BOX---------------#
# Create a list of collision types with an "All Collisions" option
collision_options = ["All collision types"] + list(all_games['Collision Type'].unique())
# Create a select box with the collision type options
selected_collision = col2.selectbox('Select a collision type:', collision_options)

# Filter the dataframe based on the selected player, unless "All Players" is selected
if selected_collision == "All collision types":
    # Show everything (i.e, don't filter the data)
    filtered_games=filtered_games
else:
    filtered_games = filtered_games[filtered_games['Collision Type'] == selected_collision]
#----------------------------------------------------------#

col1.dataframe(filtered_games)
#----------------------------------------------------------------------------------------------------------------------#

st.markdown('---')
st.header(f'Metrics for {selected_player}')
st.text(f"Filtered by\ncollision type: {selected_collision}\nand\nscore range: {min_score} to {max_score} points")

col3, col4, col5 = st.columns(3)

avg_score_selected = round(filtered_games['Score'].mean(),1)
avg_score_all = round(all_games['Score'].mean(),1)
std_selected = round(filtered_games['Score'].std(),1)
std_all = round(all_games['Score'].std(),1)
max_selected = int(filtered_games['Score'].max())
max_all = int(all_games['Score'].max())

col3.metric('Average score', avg_score_selected, round(avg_score_selected-avg_score_all,1))
col4.metric('Standard deviation of score',std_selected, round(std_selected-std_all,1), delta_color="inverse")
col5.metric('Top score', max_selected, max_selected-max_all)

col6, col7, col8 = st.columns(3)

games_played = int(len(filtered_games))
games_played_total = int(len(all_games))
played_games_percent = str(round(games_played/games_played_total*100,1)) + "%"
time_played_average = filtered_games['Duration'].mean()
time_played_total = filtered_games['Duration'].sum()

col6.metric('Games played', games_played)
if time_played_average < 60:
    col7.metric('Average game duration', str(int(round(time_played_average, 0))) + " sec")
else:
    col7.metric('Average game duration', str(round(time_played_average/60, 1)) + " min")

if time_played_total < 60:
    col8.metric('Total playing time', str(int(round(time_played_total, 0))) + " sec")
else:
    col8.metric('Total playing time', str(round(time_played_total/60, 1)) + " min")