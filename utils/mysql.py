import pandas as pd
import mysql.connector
from mysql.connector import Error

def mysql_sample_query():
    try: 
        conn = mysql.connector.connect(
            host="3.142.123.247",
            user="hoyoul",
            password="1111",
            database='hello_world',
            charset="utf8mb4")
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM hello_world.hello_world;"        
        cursor.execute(sql)
        res = cursor.fetchall()
        cursor.close()
        df= pd.DataFrame(res)
        return df
    except mysql.connector.Error as error:
        print("Failed to execute stored procedure: {}".format(error))
    finally:
        if (conn.is_connected()):
            cursor.close()
            conn.close()
            print("MySQL connection is closed")      
            