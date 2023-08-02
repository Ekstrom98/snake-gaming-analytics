import psycopg2, configparser

# Read configuration from 'config.cfg' file
config = configparser.ConfigParser()
config.read('config.cfg')

POSTGRES_USER = config['POSTGRES']['POSTGRES_USER']
POSTGRES_PASSWORD = config['POSTGRES']['POSTGRES_PASSWORD']
POSTGRES_DB = config['POSTGRES']['POSTGRES_DB']
HOST = config['POSTGRES']['HOST']
PORT = config['POSTGRES']['PORT']




try:
    connection = psycopg2.connect(
    user=POSTGRES_USER +"a",
    password=POSTGRES_PASSWORD+"a",
    host=HOST,
    port=PORT,
    database=POSTGRES_DB
)
    cursor = connection.cursor()
    # Perform database operations here
    cursor.close()
    connection.close()
    print("Connection successful!")
except Exception as e:
    print("Failed to connect to the database.")
    print("Error: " + str(e))

