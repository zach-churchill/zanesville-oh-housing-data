import sqlite3

def setup_database(database_file_path, table_schema=None):
    """Creates a SQLite database file with the given file path, sets up the
    database per the table schema, and returns the connection object.

    Parameters
    ----------
    database_file_path (str) : Path string pointing to the SQLite database file.
    table_schema (str) : SQL string to set up database table.

    Returns
    -------
    connection_obj (sqlite3.Connection) : Connection object to the database.

    """
    connection_obj = sqlite3.connect(database_file_path)

    cursor = connection_obj.cursor()
    try:
        if table_schema:
            cursor.execute(table_schema)
    except sqlite3.OperationalError as err:
        print('[ERROR] Table schema for database is incorrect.')
    else:
        connection_obj.commit()
    finally:
        cursor.close()

    return connection_obj
