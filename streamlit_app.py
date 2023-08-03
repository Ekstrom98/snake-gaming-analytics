import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Snake Gaming Analytics",
    page_icon="🐍",
    layout="centered",
)

st.title("Snake Gaming Analytics")


all_games = pd.read_csv("./query_results/get_all_games.csv", 
                        usecols=['Player', 'Collision Type','Datetime'],
                        header=None)
st.dataframe(all_games)

# st.title("Best Player")
# col1, col2, col3 = st.columns(3)
# col1.metric("Best Score", f"{best_player_score}")
# col2.metric("Player", f"{best_player_name}")
# col3.metric("Date", f"{best_player_date}")