import os
import sys
import json
import sqlite3
from pathlib import Path
import selenium
from selenium import webdriver
from bs4 import BeautifulSoup

URLS = {
        'advanced-search-results': "http://www.muskingumcountyauditor.org/Results.aspx?SearchType=Advanced&Criteria=20g%2byYTTdkDKRrEbpO1sLV9b36Zp5GCYSiEbzYPtPXU%3d",
        'parcel-id-data-fmt': "http://muskingumcountyauditor.org/Data.aspx?ParcelID={parcel_id}"
    }

TABLE_NAME = 'parcel_numbers'
TABLE_SCHEMA = 'CREATE TABLE {} (number TEXT UNIQUE)'.format(TABLE_NAME)

def handle_error(err):
    """Prints error to the screen, with '[ERROR]' prepended to the message.
    Then, it exits the program.

    Parameters
    ----------
    err (exception) : Inherited exception class.

    """
    print('[ERROR] {}'.format(err))
    sys.exit()

def find_project_path(project_name):
    """Returns the full path for the project given that the project name is
    exactly how it is in the user's files and is in the path tree from the
    directory for which this function is called.

    Example
    --------
    If the project name is 'Project1', and the current directory that this
    function is '/home/zach/Documents/Project1/src/module1' then this function
    will return '/home/zach/Documents/Project1'.

    Parameters
    ----------
    project_name (str) : Name of the project, exactly how it is for the folder.

    Returns
    -------
    project_path (str) : The absolute path for the project if found; otherwise,
        error is printed to screen and program exited.

    """
    curr_dir = Path(os.getcwd())
    path_parts = curr_dir.parts

    try:
        project_part_index = path_parts.index(project_name)
    except ValueError as err:
        handle_error(err)
    else:
        project_path = os.path.join(*path_parts[:project_part_index+1])

    return project_path

def setup_database(database_file_path):
    """Given the path, a SQLite is created with a simple one column table if
    one doesn't already exist; otherwise, it simply connects to the existing
    database file. Returns the sqlite3 connection object.

    Parameters
    ----------
    database_file_path (str) : Path string pointing to the SQLite database file.
    table_schema (str) : SQL string to set up database table.

    Returns
    -------
    connection_obj (sqlite3.Connection) : Connection object to the database.

    """
    #if not os.path.exists(database_file_path):
    connection_obj = sqlite3.connect(database_file_path)
    cursor = connection_obj.cursor()
    try:
        cursor.execute(TABLE_SCHEMA)
    except sqlite3.OperationalError as err:
        if str(err) == 'table {} already exists'.format(TABLE_NAME):
            pass
        else:
            handle_error(err)
    else:
        connection_obj.commit()
    finally:
        cursor.close()

    return connection_obj

def prepare_search_page_webdriver(project_path):
    """Prepares the search page session for retrieving the parcel numbers
    for the City of Zanesville.

    Parameters
    ----------
    project_path (str) : Path of the Git project folder.

    Returns
    -------
    search_page_driver (selenium.webdriver) : Webdriver using PhantomJS, and
        is set to the advanced search results for the auditor's website for
        the City of Zanesville.

    """
    # Create a link to the PhantomJS API file and set up a webdriver
    phantomjs_path = os.path.join(project_path, 'resources', 'phantomjs')
    search_page_driver = webdriver.PhantomJS(executable_path=phantomjs_path)

    # Navigate to the page with the parcel numbers
    search_page_driver.get(URLS['advanced-search-results'])

    # If there is a disclaimer, use the necessary JavaScript to press
    # the 'Accept' button (read if you have not done so first)
    button_css_id = 'ContentPlaceHolder1_btnDisclaimerAccept'
    js_fmt_code = "document.getElementById('{}').click();"
    js_code = js_fmt_code.format(button_css_id)
    try:
        search_page_driver.execute_script(js_code)
    except Exception as err:
        handle_error(err)

    # Return the prepared webdriver object
    return search_page_driver

def store_parcel_numbers(database_path, parcel_numbers):
    """Stores the scraped parcel numbers into a SQLite database, where the
    table consists of just one column for unique parcel numbers.

    Parameters
    ----------
    database_path (str) : Path to the SQLite database
    parcel_numbers (list) : List of strings of parcel numbers scraped from
        the advanced search webpage.

    Returns
    -------
    database_path (str) : Path to the SQLite database file.

    """
    # Set up the SQLite database file for the parcel numbers
    parcel_conn = setup_database(database_path)

    # Insert parcel numbers iteratively so that we can catch when a
    # parcel number is not unique and quietly dismiss
    fmt_insert_stmt = "INSERT INTO parcel_numbers VALUES (?)"
    parcel_cursor = parcel_conn.cursor()
    for parcel_number in parcel_numbers:
        try:
            parcel_cursor.execute(fmt_insert_stmt, parcel_numbers)
        except sqlite3.IntegrityError:
            pass

    # Commit the inserts to the database
    parcel_conn.commit()

    # Tear down
    parcel_cursor.close()
    parcel_conn.close()

    return database_path

def scrape_parcel_numbers(search_page_driver):
    """Shell function to understand the process."""
    parcel_numbers = ['1234']
    return parcel_numbers

def main():
    # Set up
    project_name = 'zanesville-oh-housing-data'
    project_path = find_project_path(project_name)
    raw_data_path = os.path.join(project_path, 'data', 'raw')
    database_name = 'parcel.sqlite'
    database_path = os.path.join(raw_data_path, database_name)

    # Setup the webdriver to the search page
    search_page_driver = prepare_search_page_webdriver(project_path)

    # Scrape as many parcel numbers as we can
    parcel_numbers = scrape_parcel_numbers(search_page_driver)

    # Store the results in a SQLite database
    database_path = store_parcel_numbers(database_path, parcel_numbers)

    # Test
    parcel_conn = setup_database(database_path)
    parcel_cursor = parcel_conn.cursor()
    parcel_cursor.execute('SELECT * FROM {}'.format(TABLE_NAME))
    print(parcel_cursor.fetchone())

    # Tear down
    parcel_cursor.close()
    parcel_conn.close()

if __name__ == '__main__':
    main()
