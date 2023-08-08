from database import database
import csv
import subprocess

db = database()
db.connect(return_connection=False)

# Execute script for finding the top 3 best games and write to a csv file
top_3_results = db.execute_sql_script("./sql/top_3.sql")
with open('./query_results/top_3_results.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    # Write the results to the CSV file
    for result in top_3_results:
        writer.writerow(result)

# Execute script fetching all games that have been played and write to a csv file
get_all_games = db.execute_sql_script("./sql/get_all_games.sql")
with open('./query_results/get_all_games.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    # Write the results to the CSV file
    for result in get_all_games:
        writer.writerow(result)

# Execute script to obtain csv file with all game durations
time_played = db.execute_sql_script("./sql/time_played.sql")
with open('./query_results/time_played.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    # Write the results to the CSV file
    for result in time_played:
        writer.writerow(result)

db.disconnect()

# Adding the specified folder
subprocess.run(['git', 'add', 'query_results'])

# Committing with the specified message
subprocess.run(['git', 'commit', '-m', 'updated data'])

# Pushing the changes
subprocess.run(['git', 'push'])