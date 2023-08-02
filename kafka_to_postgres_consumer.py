import psycopg2, configparser, json
from kafka import KafkaConsumer
from datetime import datetime

# Read configuration from 'config.cfg' file
config = configparser.ConfigParser()
config.read('config.cfg')

POSTGRES_USER = config['POSTGRES']['POSTGRES_USER']
POSTGRES_PASSWORD = config['POSTGRES']['POSTGRES_PASSWORD']
POSTGRES_DB = config['POSTGRES']['POSTGRES_DB']
HOST = config['POSTGRES']['HOST']
PORT = config['POSTGRES']['PORT']

bootstrap_server = config['KAFKA']['bootstrap_server']

initialization_consumer = KafkaConsumer('initializations', bootstrap_servers=bootstrap_server, auto_offset_reset='earliest', consumer_timeout_ms=1000)
food_positions_consumer = KafkaConsumer('food_positions', bootstrap_servers=bootstrap_server, auto_offset_reset='earliest', consumer_timeout_ms=1000)
snake_head_positions_consumer = KafkaConsumer('snake_head_positions', bootstrap_servers=bootstrap_server, auto_offset_reset='earliest', consumer_timeout_ms=6000)
events_consumer = KafkaConsumer('events', bootstrap_servers=bootstrap_server, auto_offset_reset='earliest', consumer_timeout_ms=1000)
scores_consumer = KafkaConsumer('scores', bootstrap_servers=bootstrap_server, auto_offset_reset='earliest', consumer_timeout_ms=1000)
game_overs_consumer = KafkaConsumer('game_overs', bootstrap_servers=bootstrap_server, auto_offset_reset='earliest', consumer_timeout_ms=1000)

try:
    connection = psycopg2.connect(
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=HOST,
    port=PORT,
    database=POSTGRES_DB
)
    print("Connection successful!")
except Exception as e:
    print("Failed to connect to the database.")
    print("Error: " + str(e))

cursor = connection.cursor()

def insert_data(cursor, connection, insert_query, data_to_insert):
    try:
        cursor = connection.cursor()

        # Execute the INSERT query with the data
        cursor.execute(insert_query, data_to_insert)

        # Commit the changes to the database
        connection.commit()
    except Exception as e:
        print("Failed to insert data.")
        print("Error: " + str(e))
try:
    for msg in initialization_consumer:
            #print(msg.topic, msg.offset, type(msg))
            # Decoding the bytes to a string
            data_string = msg.value.decode('utf-8')

            # Parsing the JSON string
            data_json = json.loads(data_string)

            # Extracting the data
            game_id = data_json['game_id']
            player = data_json['player']
            screen_width = data_json['screen_width']
            screen_height = data_json['screen_height']
            platform = data_json['platform']
            init_time = data_json['init_time']
            # Convert Unix timestamp to a Python datetime object
            init_time = datetime.utcfromtimestamp(init_time)
            # Convert the datetime object to a string representation in PostgreSQL's timestamp format
            init_time = init_time.strftime("%Y-%m-%d %H:%M:%S.%f")

            # Define insert query
            insert_query = "INSERT INTO initializations (game_id, player, screen_width, screen_height, platform, init_time) VALUES (%s, %s, %s, %s, %s, %s)"

            # Data to be inserted 
            data_to_insert = (f'{game_id}', f'{player}', f'{screen_width}', f'{screen_height}', f'{platform}', f'{init_time}')

            insert_data(cursor, connection, insert_query, data_to_insert)
    print("Data from the topic initializations transferred successfully.")
except Exception as e:
    print("Data could not be transferred correctly from the topic initializations.")
    print("Error: " + str(e))

try:  
    for msg in food_positions_consumer:
            # Decoding the bytes to a string
            data_string = msg.value.decode('utf-8')

            # Parsing the JSON string
            data_json = json.loads(data_string)

            # Extracting the data
            game_id = data_json['game_id']
            food_x = data_json['food_x']
            food_y = data_json['food_y']
            time = data_json['time']

            # Convert Unix timestamp to a Python datetime object
            time = datetime.utcfromtimestamp(time)
            # Convert the datetime object to a string representation in PostgreSQL's timestamp format
            time = time.strftime("%Y-%m-%d %H:%M:%S.%f")

            # Define insert query
            insert_query = "INSERT INTO food_positions (game_id, food_x, food_y, time) VALUES (%s, %s, %s, %s)"

            # Data to be inserted 
            data_to_insert = (f'{game_id}', f'{food_x}', f'{food_y}', f'{time}')

            insert_data(cursor, connection, insert_query, data_to_insert)
    print("Data from the topic food_positions transferred successfully.")
except Exception as e:
     print("Data could not be transferred correctly from the topic food_positions.")
     print("Error: " + str(e))

try: 
    for msg in snake_head_positions_consumer:
            # Decoding the bytes to a string
            data_string = msg.value.decode('utf-8')

            # Parsing the JSON string
            data_json = json.loads(data_string)

            # Extracting the data
            game_id = data_json['game_id']
            head_x = int(data_json['head_x'])
            head_y = int(data_json['head_y'])
            time = data_json['time']
            
            # Convert Unix timestamp to a Python datetime object
            time = datetime.utcfromtimestamp(time)
            # Convert the datetime object to a string representation in PostgreSQL's timestamp format
            time = time.strftime("%Y-%m-%d %H:%M:%S.%f")

            # Define insert query
            insert_query = "INSERT INTO snake_head_positions (game_id, head_x, head_y, time) VALUES (%s, %s, %s, %s)"

            # Data to be inserted 
            data_to_insert = (f'{game_id}', f'{head_x}', f'{head_y}', f'{time}')

            insert_data(cursor, connection, insert_query, data_to_insert)
    print("Data from the topic snake_head_positions transferred successfully.")
except Exception as e:
     print("Data could not be transferred correctly from the topic snake_head_positions.")
     print("Error: " + str(e))

try:
    for msg in events_consumer:
            # Decoding the bytes to a string
            data_string = msg.value.decode('utf-8')

            # Parsing the JSON string
            data_json = json.loads(data_string)

            # Extracting the data
            game_id = data_json['game_id']
            event_key = data_json['event_key']
            time = data_json['time']
            
            # Convert Unix timestamp to a Python datetime object
            time = datetime.utcfromtimestamp(time)
            # Convert the datetime object to a string representation in PostgreSQL's timestamp format
            time = time.strftime("%Y-%m-%d %H:%M:%S.%f")

            # Define insert query
            insert_query = "INSERT INTO events (game_id, event_key, time) VALUES (%s, %s, %s)"

            # Data to be inserted 
            data_to_insert = (f'{game_id}', f'{event_key}', f'{time}')
            
            insert_data(cursor, connection, insert_query, data_to_insert)
    print("Data from the topic events transferred successfully.")
except Exception as e:
     print("Data could not be transferred correctly from the topic events.")
     print("Error: " + str(e))


try:
    for msg in scores_consumer:
            # Decoding the bytes to a string
            data_string = msg.value.decode('utf-8')

            # Parsing the JSON string
            data_json = json.loads(data_string)

            # Extracting the data
            game_id = data_json['game_id']
            score = data_json['score']
            time = data_json['time']
            
            # Convert Unix timestamp to a Python datetime object
            time = datetime.utcfromtimestamp(time)
            # Convert the datetime object to a string representation in PostgreSQL's timestamp format
            time = time.strftime("%Y-%m-%d %H:%M:%S.%f")

            # Define insert query
            insert_query = "INSERT INTO scores (game_id, score, time) VALUES (%s, %s, %s)"

            # Data to be inserted 
            data_to_insert = (f'{game_id}', f'{score}', f'{time}')
            
            insert_data(cursor, connection, insert_query, data_to_insert)
    print("Data from the topic scores transferred successfully.")
except Exception as e:
     print("Data could not be transferred correctly from the topic scores.")
     print("Error: " + str(e))

try:
    for msg in game_overs_consumer:
            # Decoding the bytes to a string
            data_string = msg.value.decode('utf-8')

            # Parsing the JSON string
            data_json = json.loads(data_string)

            # Extracting the data
            game_id = data_json['game_id']
            collision_type = data_json['collision_type']
            score = data_json['score']
            time = data_json['time']
            
            # Convert Unix timestamp to a Python datetime object
            time = datetime.utcfromtimestamp(time)
            # Convert the datetime object to a string representation in PostgreSQL's timestamp format
            time = time.strftime("%Y-%m-%d %H:%M:%S.%f")

            # Define insert query
            insert_query = "INSERT INTO game_overs (game_id, collision_type, score, time) VALUES (%s, %s, %s, %s)"

            # Data to be inserted 
            data_to_insert = (f'{game_id}', f'{collision_type}', f'{score}', f'{time}')
            
            insert_data(cursor, connection, insert_query, data_to_insert)
    print("Data from the topic game_overs transferred successfully.")
except Exception as e:
     print("Data could not be transferred correctly from the topic game_overs.")
     print("Error: " + str(e))


cursor.close()
connection.close()