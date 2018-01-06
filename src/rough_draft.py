import os
import sys
import time
from pathlib import Path
from selenium import webdriver

URLS = {
        'advanced-search-results': "http://www.muskingumcountyauditor.org/Results.aspx?SearchType=Advanced&Criteria=20g%2byYTTdkDKRrEbpO1sLV9b36Zp5GCYSiEbzYPtPXU%3d",
        'parcel-id-data-fmt': "http://muskingumcountyauditor.org/Data.aspx?ParcelID={parcel_id}"
    }

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
        print(err)
        sys.exit()
    else:
        project_path = os.path.join(*path_parts[:project_part_index+1])

    return project_path

def prepare_webdriver(url):
    """ Prepares a Selenium webdriver with Firefox for the given URL, 
    where the disclaimer button will be pressed if it appears.

    Parameters
    ----------
    url (str) : URL that will be navigated to after creating the webdriver.

    Returns
    -------
    driver (selenium.webdriver) : Webdriver using Firefox, and is set to the 
        given URL, where the URL is assumed to be pointing to a page on the
        auditor's website.

    """
    # Create a link to the Firefox API file and set up a webdriver
    driver = webdriver.Firefox()

    # Navigate to the URL and pause for the website to fully load
    driver.get(url)
    time.sleep(1) 

    # If there is a disclaimer button, then click it using the CSS ID
    button_css_id = 'ContentPlaceHolder1_btnDisclaimerAccept'
    try:
        driver.find_element_by_id(button_css_id).click()
    except Exception as err:
        print(err)

    # Return the prepared webdriver object
    return driver

def scrape_single_results_page(driver):
    """Scrapes the parcel numbers from a single advanced search page for the
    parcel numbers.

    Parameters
    ----------
    driver (selenium.webdriver) : Webdriver using Firefox, and is set to the 
        advanced search results for the auditor's website for the City of 
        Zanesville.

    Returns
    -------
    parcel_numbers (list) : List of strings of parcel numbers scraped from
        the advanced search webpage.

    """
    even_rows = driver.find_elements_by_class_name("rowstyle")
    odd_rows = driver.find_elements_by_class_name("alternatingrowstyle")
    rows = even_rows + odd_rows

    parcel_numbers = []
    for row in rows:
        # The parcel number is the first column, so only get first "td"
        parcel_number = row.find_element_by_tag_name("td").text
        parcel_numbers.append(parcel_number)
    
    return parcel_numbers

def main():
    # Set up
    project_name = 'zanesville-oh-housing-data'
    project_path = find_project_path(project_name)

    # Setup the webdriver to the search page
    search_page_driver = prepare_webdriver(URLS['advanced-search-results'])

    # Scrape as many parcel numbers as we can
    parcel_numbers = scrape_single_results_page(search_page_driver)
    print(parcel_numbers)

    # Tear down
    search_page_driver.quit()

if __name__ == '__main__':
    main()
