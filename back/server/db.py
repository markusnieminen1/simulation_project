# All logic for DB operations
import psycopg2
from dotenv import load_dotenv
import os
from typing import Optional, Dict

class DB_Connection:
    _instance = None
    _ref_count = 0

    def __new__(cls, *args, **kwargs): # only one instance at a time
        if not cls._instance:
            cls._instance = super(DB_Connection, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            load_dotenv()
            self.db_host = os.getenv("host")
            self.db_name = os.getenv("dbname")
            self.db_port = os.getenv("port")
            self.db_user = os.getenv("user")
            self.password = os.getenv("password")
            self.connection = None
            self.cursor = None
            self.initialized = True

    def __enter__(self): 
        # Runs when entering a with block.
        # Doesn't create another connection to the db if one exists
        if not self.connection or self.connection.closed != 0:
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
        DB_Connection._ref_count += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback): 
        # Runs when the with block ends
        # If there's other with blocks running at the same time, exit will not close the connection
        
        DB_Connection._ref_count -= 1
        if DB_Connection._ref_count == 0:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
        
    def insert_data(self, table_name: str, data_to_db: list) -> bool:
        """ # Description
        Takes the keys from the first dict on the list to use as columns. 
        Then parses the values into tuples that are sent to the db using cursor.executemany()/execute()
        
        Args:
            table_name (str): table_name(in a predefined db)
            data_to_db (list): format needs to be 
                                [
                                    {"column1":1, "column2":1}, 
                                    {"column1":2, "column2":2}, 
                                    {"column1":3, "column2":3}...
                                    ]
                                where the keys (and the dict lenghts) are identical to eachother. 
                                
        """
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
                self.cursor.execute(sql_insert, values[0])
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"Failed to insert data into {table_name}: {e}")
            return False
    
    def fetch_password_hash(self, user_email:str) -> Optional[str]:
        """ # Description
        Fetch the user password hash by taking user email (username) as a parameter

        Args:
            user_email (str)

        Returns:
            Optional[str]: returns str if found. None if something goes wrong or not found
        """
        try:
            sql_fetch = f"SELECT password_hash FROM users WHERE username=(%s)"
            self.cursor.execute(sql_fetch, (user_email,))
            hash = self.cursor.fetchone()
            if hash:
                return hash[0]
            else:
                return None
        
        except Exception as e:
            print(f"exception, fetching hashed pwd: {e}")
            return None
            
    def fetch_user(self, user_email: str) -> Optional[Dict]:
        """# Description
        Fetch the user by taking user email (username) as a parameter

        Args:
            user_email (str)

        Returns:
            Optional[Dict]: Returns a dictionary where keys with None values are deleted. 
                            If user not found or Exception -> None 
        """
        try:
            sql_fetch = "SELECT username, password_hash, disabled, permission_level, simulation_ids FROM users WHERE username=%s"
            self.cursor.execute(sql_fetch, (user_email,))
            column_names = [desc[0] for desc in self.cursor.description]
            row = self.cursor.fetchone()
            if row:
                user_dict =  dict(zip(column_names, row))
                none_v_keys = []
                for k, v in user_dict.items():
                    if v is None:
                        none_v_keys.append(k)
                for k in none_v_keys:
                    del user_dict[k]
                return user_dict # parsed dict
            
            return None # if the user doesn't exist in the db
        except Exception as e:
            print(f"Exception occurred: {e}")
            return None
    