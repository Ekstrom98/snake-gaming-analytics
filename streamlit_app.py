import streamlit as st
import psycopg2

def execute_sql_script(cursor, sql_script_path):
        # Read the .sql file
        with open(f'{sql_script_path}', 'r') as file:
                sql_file = file.read()

        # Execute the SQL commands
        sql_commands = sql_file.split(';')
        for command in sql_commands:
                try:
                        if command.strip() != '':
                                cursor.execute(command)
                except Exception as e:
                        print(f"Command skipped: {str(e)}")
        
        return cursor.fetchall()

st.set_page_config(
    page_title="Snake Gaming Analytics Dashboard",
    page_icon="🐍",
    layout="centered",
)

st.title("Hello, World!")

@st.cache_resource
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()
cursor = conn.cursor()

top_3_players = execute_sql_script(cursor=cursor, sql_script_path="./sql/top_3.sql")

best_player_score = top_3_players[0][0]
best_player_name = top_3_players[0][1]
best_player_date = top_3_players[0][2]


st.title("Best Player")
col1, col2, col3 = st.columns(3)
col1.metric("Best Score", f"{best_player_score}")
col2.metric("Player", f"{best_player_name}")
col3.metric("Date", f"{best_player_date}")