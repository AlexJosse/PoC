from mysql.connector import Error

def create_database(connection, db_name):
    query = f"CREATE DATABASE IF NOT EXISTS {db_name}"
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        return f"Database {db_name} created successfully"
    except Error as e:
        return str(e)
