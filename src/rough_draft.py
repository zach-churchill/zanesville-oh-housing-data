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

def scrape_parcel_data(row, driver):
    parcel_number = row['Parcel']
    parcel_dict = {'parcel_id': parcel_number}
    parcel_url = URLS['parcel-id-data-fmt'].format(**parcel_dict)
    driver.get(parcel_url)

    # Create return dictionary
    data_dict = dict(parcelNumber = parcel_number,
                     address = None,
                     appraisedValue = None,
                     numStories = None,
                     yearBuilt = None,
                     numBedrooms = None,
                     numFullBaths = None,
                     numHalfBaths = None,
                     livingArea = None,
                     basement = None,
                     basementArea = None)

    # Define data IDs
    id_fmt = "ContentPlaceHolder1_{}_fvData{}_{}"
    address_id = id_fmt.format("Base", "Profile", "AddressLabel")
    valuation_id = id_fmt.format("Valuation", "Valuation", "Label1")
    num_stories_id = id_fmt.format("Residential", "Residential", "Label2")
    year_built_id = id_fmt.format(
                        "Residential",
                        "Residential",
                        "YearBuiltLabel")
    num_bed_id = id_fmt.format(
                        "Residential",
                        "Residential",
                        "NumberOfBedroomsLabel")
    num_full_bath_id = id_fmt.format(
                        "Residential",
                        "Residential",
                        "NumberOfFullBathsLabel")
    num_half_bath_id = id_fmt.format(
                        "Residential",
                        "Residential",
                        "NumberOfHalfBathsLabel")
    living_area_id = id_fmt.format(
                        "Residential",
                        "Residential",
                        "FinishedLivingAreaLabel")
    basement_id = id_fmt.format(
                        "Residential",
                        "Residential",
                        "Label1")
    basement_area_id = id_fmt.format(
                        "Residential",
                        "Residential",
                        "Label4")

    # Define JavaScript code for navigating tabs
    valuation_tab = "__doPostBack('ctl00$ContentPlaceHolder1$mnuData','2')"
    residential_tab = "__doPostBack('ctl00$ContentPlaceHolder1$mnuData','8')"

    # Scrape data off of 'Base' tab
    try:
        address = driver.find_element_by_id(address_id).text
    except Exception as err:
        print('{}: {}'.format(parcel_number, err))
    else:
        data_dict['address'] = address

    # Navigate to 'Valuation' tab and scrape data
    driver.execute_script(valuation_tab)
    time.sleep(1)
    try:
        valuation = driver.find_element_by_id(valuation_id).text
    except Exception as err:
        print('{}: {}'.format(parcel_number, err))
    else:
        data_dict['appraisedValue'] = valuation

    # Navigate to 'Residential' tab and scrape data
    driver.execute_script(residential_tab)
    time.sleep(1)
    try:
        num_stories = driver.find_element_by_id(num_stories_id).text
        year_built = driver.find_element_by_id(year_built_id).text
        num_bed = driver.find_element_by_id(num_bed_id).text
        num_full_bath = driver.find_element_by_id(num_full_bath_id).text
        num_half_bath = driver.find_element_by_id(num_half_bath_id).text
        living_area = driver.find_element_by_id(living_area_id).text
        basement = driver.find_element_by_id(basement_id).text
        basement_area = driver.find_element_by_id(basement_area_id).text
    except Exception as err:
        print('{}: {}'.format(parcel_number, err))
    else:
        data_dict['numberStories'] = num_stories
        data_dict['yearBuilt'] = year_built
        data_dict['numBedrooms'] = num_bed
        data_dict['numFullBaths'] = num_full_bath
        data_dict['numHalfBaths'] = num_half_bath
        data_dict['livingArea'] = living_area
        data_dict['basement'] = basement
        data_dict['basementArea'] = basement_area

    return data_dict

def main():
    # Set up
    import pandas as pd
    project_name = 'zanesville-oh-housing-data'
    project_path = find_project_path(project_name)
    data_path = os.path.join(project_path, 'data', 'processed')

    # # Setup the webdriver to the search page
    # search_page_driver = prepare_webdriver(URLS['advanced-search-results'])
    #
    # # Scrape as many parcel numbers as we can
    # parcel_numbers = scrape_single_results_page(search_page_driver)
    # print(parcel_numbers)
    #
    # # Close the Firefox window
    # search_page_driver.quit()

    # Get processed parcel numbers
    parcel_numbers_csv = os.path.join(data_path, 'parcel-numbers.csv')
    parcel_numbers = pd.read_csv(parcel_numbers_csv)

    # Create a webdriver
    empty_parcel_dict = {'parcel_id': ''}
    empty_parcel_url = URLS['parcel-id-data-fmt'].format(**empty_parcel_dict)
    driver = prepare_webdriver(empty_parcel_url)

    start_time = time.time()
    parcel_numbers = parcel_numbers.iloc[:10, ]
    import functools
    partial_scrape_parcel_data = functools.partial(scrape_parcel_data,
                                                   driver=driver)
    parcel_data = parcel_numbers.apply(scrape_parcel_data,
                                       driver=driver,
                                       axis=1)
    end_time = time.time()
    print('Took {:.2f} minutes'.format((end_time - start_time) / 60))
    print('Parcel numbers processed: {}'.format(parcel_data.shape[0]))
    print(parcel_data)

    # Close the Firefox window
    driver.quit()

if __name__ == '__main__':
    main()
