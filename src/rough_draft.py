import os
from utility import find_project_path
from database import setup_database

def main():
    project_name = 'zanesville-oh-housing-data'
    project_path = find_project_path(project_name)

    # With the project path, set up paths to necessary folders
    raw_data_path = os.path.join(project_path, 'data', 'raw')
    resources_path = os.path.join(project_path, 'resources')

    # Set up the SQLite database file for the parcel numbers
    database_name = 'parcel.sqlite'
    database_path = os.path.join(raw_data_path, database_name)
    table_schema = 'CREATE TABLE parcel_numbers (number TEXT UNIQUE)'

    if os.path.exists(database_path):
        os.remove(database_path)
        parcel_conn = setup_database(database_path, table_schema)
    else:
        parcel_conn = setup_database(database_path, table_schema)

    # Simple test
    parcel_cursor = parcel_conn.cursor()
    parcel_cursor.execute("INSERT INTO parcel_numbers VALUES ('1234')")
    parcel_conn.commit()

    parcel_cursor.execute('SELECT * FROM parcel_numbers')
    print(parcel_cursor.fetchone())

    # Tear down
    parcel_cursor.close()
    parcel_conn.close()

if __name__ == '__main__':
    main()
