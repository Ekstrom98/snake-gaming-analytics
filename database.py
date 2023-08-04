import psycopg2, configparser
class database:
    def __init__(self):
        # Read configuration from 'config.cfg' file
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')

        self.POSTGRES_USER = self.config['POSTGRES']['POSTGRES_USER']
        self.POSTGRES_PASSWORD = self.config['POSTGRES']['POSTGRES_PASSWORD']
        self.POSTGRES_DB = self.config['POSTGRES']['POSTGRES_DB']
        self.HOST = self.config['POSTGRES']['HOST']
        self.PORT = self.config['POSTGRES']['PORT']
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
    
    def backup_data(self):
        import subprocess
        
        connection_str = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.HOST}:{self.PORT}/{self.POSTGRES_DB}"
        
        with open('./sql/data_backup.sql', 'r') as file:
            sql_commands = file.read().split(';')

        for command in sql_commands:
            try:
                if command.strip() != '':
                    table = command.split(' ')[1]
                    print(f"Copying table {table}...")
                    backup_path = self.config['BACKUP'][f'{table.upper()}']
                    command = command.format(path=backup_path)
                    result = subprocess.run(['psql', connection_str], input=command.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    if result.returncode != 0:
                        print(f"Command failed: {result.stderr.decode()}")
                    else:
                        print(result.stdout.decode())
                        print(f"The table {table} has been successfully copied.")

            except Exception as e:
                 print(f"Command skipped: {str(e)}")