# All logic for DB operations
import psycopg2
from dotenv import load_dotenv
import os

class DB_connection:
    def __init__(self):
        # loads the env variables
        load_dotenv()
        self.db_host = os.getenv("host")
        self.db_name = os.getenv("dbname")
        self.db_port = os.getenv("port")
        self.db_user = os.getenv("user")
        self.password = os.getenv("password")
        self.connection = None
        self.cursor = None
        
    def __enter__(self):
        # runs when the class is called by a 'with' block 
        # __enter__ creates the connection 
        try:
            self.connection = psycopg2.connect(
                user=self.db_user,
                password=self.password,
                host=self.db_host,
                port=self.db_port,
                dbname=self.db_name
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(f"Connecting to database {self.db_name} failed: {e}")

        return self
    
    
    def __exit__(self, exc_type, exc_value, traceback):
        # runs when the with block ends, closes the connection
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        
    def insert_data(self, table_name: str, data_to_db: list):
        try:
            columns = list(iter(data_to_db[0])) # keys from the first dict
            columns_str = ', '.join(columns) # str for the sql query
            
            values = [] # list for value tuples
            for i in data_to_db:
                dump = []
                for j in columns:
                    dump.append(i[j])
                values.append(tuple(dump))
            
            # dynamically create the sql query
            sql_insert = f"INSERT INTO {table_name} ({columns_str}) VALUES ({('%s,' * len(columns))[:-1]})"
            
            if len(values) > 1: # executemany for multiple tuples
                self.cursor.executemany(sql_insert, values)
            else:
                self.cursor.execute(sql_insert, values)
            self.connection.commit()
            
        except Exception as e:
            print(f"Failed to insert data into {table_name}: {e}")
    
    def fetch_password_hash(self, user_email):
        try:
            sql_fetch = f"SELECT password_hash FROM users WHERE email='{user_email}'"
            self.cursor.execute(sql_fetch)
            return user_email, self.cursor.fetchone()[0]
        
        except Exception as e:
            print(f"An exception occured while fetching passwordhash: {e}")
    