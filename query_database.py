from database import database
import csv

db = database()
db.connect(return_connection=False)

# Execute script for finding the top 3 best games
top_3_results = db.execute_sql_script("./sql/top_3.sql")
# Open a file in write mode
with open('./query_results/top_3_results.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    # Write the results to the CSV file
    for result in top_3_results:
        writer.writerow(result)

# Execute script for finding the top 3 best games
get_all_games = db.execute_sql_script("./sql/get_all_games.sql")
# Open a file in write mode
with open('./query_results/get_all_games.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    # Write the results to the CSV file
    for result in get_all_games:
        writer.writerow(result)

db.disconnect()

