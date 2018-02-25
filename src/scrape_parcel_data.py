import os
import csv
from itertools import chain
from functools import partial
from selenium import webdriver
from utils import find_project_path
from webscraper import redirect_url
from webscraper import get_parcel_data_url
from webscraper import scrape_valuation_tab
from webscraper import scrape_residential_tab
from webscraper import create_data_row

def scrape_parcel_data(parcel_id, driver):
    print(parcel_id)
    parcel_id_data_url = get_parcel_data_url(parcel_id)
    print(parcel_id_data_url)
    driver = redirect_url(driver, parcel_id_data_url)

    valuation_data = scrape_valuation_tab(driver)
    residential_data = scrape_residential_tab(driver)
    data_row = create_data_row(parcel_id, valuation_data, residential_data)

    return data_row

def main():
    # Set up
    project_name = 'zanesville-oh-housing-data'
    project_path = find_project_path(project_name)
    data_dir = os.path.join(project_path, 'data')
    raw_data_dir = os.path.join(data_dir, 'raw')
    processed_data_dir = os.path.join(data_dir, 'processed')
    
    # Get processed parcel IDs
    parcel_ids_csv = os.path.join(processed_data_dir, 'parcel-numbers.csv')
    with open(parcel_ids_csv) as f:
        reader = csv.reader(f)
        colnames, *data = [row for row in reader]
    parcel_ids = chain(*data)

    # Set up a Firefox webdriver to use for scraping
    driver = webdriver.Firefox()

    # Partially fill function with driver
    prepped_scrape_parcel_data = partial(scrape_parcel_data, driver=driver)

    parcel_ids = list(parcel_ids)[:5]

    data_rows = map(prepped_scrape_parcel_data, parcel_ids)

    print(list(data_rows))

    # Tear down
    driver.quit()

if __name__ == '__main__':
    main()
