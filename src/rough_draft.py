import os
import sys
import time
import functools
from pathlib import Path
from collections import namedtuple
import pandas as pd
from selenium import webdriver

CommercialData = namedtuple('CommRow', ['parcelNumber', 'commDescription', 
                                        'commYearBuilt', 'commYearRemodeled',
                                        'commSectionArea', 'commNumStories'])

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

def scrape_comm_data(row, driver):
    parcel_number = row['parcelNumber']
    parcel_dict = {'parcel_id': parcel_number}
    parcel_url = URLS['parcel-id-data-fmt'].format(**parcel_dict)
    driver.get(parcel_url)

    # Define data IDs
    data_table_id = 'ContentPlaceHolder1_Commercial_gvDataCommercial'

    # Define JavaScript code for navigating tabs
    commercial_tab = "__doPostBack('ctl00$ContentPlaceHolder1$mnuData','10')"

    # Wait a couple seconds before navigating to the 'Commercial' tab
    time.sleep(2)

    # Navigate to 'Valuation' tab and scrape data
    driver.execute_script(commercial_tab)
    time.sleep(2)
    try:
        data_table = driver.find_element_by_id(data_table_id)
        commercial_data_cols = data_table.find_elements_by_tag_name("td")
    except Exception as err:
        print("\nNo commercial data.\n")
    else:
        commercial_data = []
        for commercial_data_col in commercial_data_cols:
           commercial_data.append(commercial_data_col.text)

    if len(commercial_data) == 5:
        return_data = CommercialData(
                parcelNumber      = parcel_number,
                commDescription   = commercial_data[0],
                commYearBuilt     = commercial_data[1],
                commYearRemodeled = commercial_data[2],
                commSectionArea   = commercial_data[3],
                commNumStories    = commercial_data[4]
            )
    else:
        print("\nNot all commercial data captured:", commercial_data, "\n")

        return_data = CommercialData(
                parcelNumber      = parcel_number,
                commDescription   = None,
                commYearBuilt     = None,
                commYearRemodeled = None,
                commSectionArea   = None,
                commNumStories    = None
            )

    return return_data

def main():
    # Set up
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

    # Create a simple variable to control flow
    flow_control = 'commercial'


    if flow_control == 'commercial':
        potential_commercial_ids_file = os.path.join(data_path,
                                                     'comm-parcel-numbers.csv')
        potential_commercial_ids = pd.read_csv(potential_commercial_ids_file)

        partial_scrape_comm_data = functools.partial(scrape_comm_data,
                                                     driver=driver)

        fmt_file_path = 'commercial_data_{}.csv'
        for idx in range(0, potential_commercial_ids.shape[0], 10):
            start_time = time.time()
            mini_batch = potential_commercial_ids.iloc[idx:idx+10,]
            commercial_data = mini_batch.apply(partial_scrape_comm_data, axis=1)
            end_time = time.time()

            # Log index and time took to scrape
            print('Index: {}'.format(idx))
            print('Took {.2f} minutes'.format((end_time - start_time) / 60))

            # Save the data with the index appended
            file_path = os.path.join(data_path, fmt_file_path.format(idx))
            pd.DataFrame(list(parcel_data)).to_csv(file_path, header=True, index=False)

    # Close the Firefox window
    driver.quit()
