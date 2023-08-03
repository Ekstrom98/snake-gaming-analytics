import psycopg2, configparser
class database:
    def __init__(self):
        # Read configuration from 'config.cfg' file
        config = configparser.ConfigParser()
        config.read('config.cfg')

        self.POSTGRES_USER = config['POSTGRES']['POSTGRES_USER']
        self.POSTGRES_PASSWORD = config['POSTGRES']['POSTGRES_PASSWORD']
        self.POSTGRES_DB = config['POSTGRES']['POSTGRES_DB']
        self.HOST = config['POSTGRES']['HOST']
        self.PORT = config['POSTGRES']['PORT']
        self.connection = None

    def connect(self, return_connection = False):
        if return_connection:

            try:
                print("Initializing connection to database...")
                self.connection = psycopg2.connect(
                user=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.HOST,
                port=self.PORT,
                database=self.POSTGRES_DB
            )
                print("Connection successful!")
                return self.connection
            except Exception as e:
                print("Failed to connect to the database.")
                print("Error: " + str(e))
        else:
            try:
                print("Initializing connection to database...")
                self.connection = psycopg2.connect(
                user=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.HOST,
                port=self.PORT,
                database=self.POSTGRES_DB
                )
                print("Connection successful!")
            except Exception as e:
                print("Failed to connect to the database.")
                print("Error: " + str(e))

    def disconnect(self):
        try:
            print("Disconnecting from database...")
            self.connection.close()
            if(self.connection.closed): 
                print("Successfully disconnected from database.")
            else:
                 print("Couldn't successfully close the connection to the database.")
        except Exception as e:
            print("Failed to disconnect from database.")
            print("Error: " + str(e))

    def execute_sql_script(self, sql_script_path):
        cursor = self.connection.cursor()
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

 # Test code
# test = database()
# a = test.connect()
# print(a)
# results = test.execute_sql_script("./sql/top_3.sql")
# print(results)
# test.disconnect()
