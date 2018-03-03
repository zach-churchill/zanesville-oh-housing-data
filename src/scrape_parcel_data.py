import os
import csv
import itertools
from functools import partial
from selenium import webdriver
from utils import find_project_path
from webscraper import redirect_url
from webscraper import get_parcel_data_url
from webscraper import scrape_valuation_tab
from webscraper import scrape_residential_tab
from webscraper import create_data_row

def scrape_parcel_data(parcel_id, driver):
    print("Parcel ID: {}".format(parcel_id))
    parcel_id_data_url = get_parcel_data_url(parcel_id)
    driver = redirect_url(driver, parcel_id_data_url)

    valuation_data = scrape_valuation_tab(driver)
    residential_data = scrape_residential_tab(driver)
    data_row = create_data_row(parcel_id, valuation_data, residential_data)

    return data_row

def save_mini_batch(raw_data_dir, mini_batch_idx, mini_batch):
    mini_batch_filename = "mini_batch_{}.csv".format(mini_batch_idx)
    mini_batch_file = os.path.join(raw_data_dir, mini_batch_filename)

    column_names = mini_batch[0]._fields   # Assumes len > 0

    print("Writing mini-batch {}".format(mini_batch_idx))
    with open(mini_batch_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(column_names)
        writer.writerows(mini_batch)

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

    # Prepare the data into a list of Parcel ID strings
    parcel_ids_iter = itertools.chain(*data)
    parcel_ids = list(parcel_ids_iter)

    # Set up a Firefox webdriver to use for scraping
    driver = webdriver.Firefox()

    # Partially fill function with driver
    prepped_scrape_parcel_data = partial(scrape_parcel_data, driver=driver)

    # Scrape the data in mini-batches to allow for iterative saving
    mini_batch_size = 10
    for mini_batch_idx in range(0, len(parcel_ids), mini_batch_size):
        mini_batch = parcel_ids[mini_batch_idx:mini_batch_idx+mini_batch_size]
        try:
            data_rows = map(prepped_scrape_parcel_data, mini_batch)
        except Exception as err:
            driver.quit()
            raise err
        else:
            save_mini_batch(raw_data_dir, mini_batch_idx, list(data_rows))

    # Tear down
    driver.quit()

if __name__ == '__main__':
    main()
