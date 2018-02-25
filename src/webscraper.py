import re
import time
from functools import partial
from collections import namedtuple
import selenium

ADV_SEARCH_PAGE_URL = "http://www.muskingumcountyauditor.org/Results.aspx?" + \
                      "SearchType=Advanced&Criteria=" + \
                      "20g%2byYTTdkDKRrEbpO1sLV9b36Zp5GCYSiEbzYPtPXU%3d"

PARCEL_DATA_FMT_URL = "http://muskingumcountyauditor.org/Data.aspx?ParcelID={}"

def check_for_disclaimer(driver):
    button_id = "ContentPlaceHolder1_btnDisclaimerAccept"

    try:
        driver.find_element_by_id(button_id).click()
    except selenium.common.exceptions.NoSuchElementException as noid:
        pass
    except Exception as err:
        driver.quit()
        raise err
    else:
        print("Disclaimer 'Accept' button clicked")

def redirect_url(driver, url):
    driver.get(url)
    time.sleep(1)

    check_for_disclaimer(driver)

    return driver

def scrape_parcel_ids_from_search_page(driver):
    even_rows = driver.find_elements_by_class_name("rowstyle")
    odd_rows = driver.find_elements_by_class_name("alternatingrowstyle")
    rows = even_rows + odd_rows

    parcel_ids = [row.find_element_by_tag_name("td").text for row in rows]

    return parcel_ids

def get_parcel_data_url(parcel_id):
    if re.match(r"(\d{2}-){4}\d{3}", parcel_id):
        return PARCEL_DATA_FMT_URL.format(parcel_id)
    else:
        print("[-] Wrong format for Parcel ID. Should be XX-XX-XX-XX-XXX")

def prepare_parcel_data_id(tab, middle, id):
    data_id_fmt = "ContentPlaceHolder1_{}_fvData{}_{}"
    return(data_id_fmt.format(tab, middle, id))

def scrape_data_by_id(driver, id):
    try:
        data = driver.find_element_by_id(id).text
    except selenium.common.exceptions.NoSuchElementException as noid:
        print('[-] {} not found on page'.format(id))
    except Exception as err:
        driver.quit()
        raise err
    else:
        return data

def scrape_valuation_tab(driver):
    valuation_tab_js = "__doPostBack('ctl00$ContentPlaceHolder1$mnuData','2')"
    driver.execute_script(valuation_tab_js)
    time.sleep(2)

    address_id = prepare_parcel_data_id("Valuation", "Profile", "AddressLabel")
    valuation_id = prepare_parcel_data_id("Valuation", "Valuation", "Label1")

    address = scrape_data_by_id(driver, address_id)
    valuation = scrape_data_by_id(driver, valuation_id)

    return (address, valuation)

def scrape_residential_tab(driver):
    resident_tab_js = "__doPostBack('ctl00$ContentPlaceHolder1$mnuData', '8')"
    driver.execute_script(resident_tab_js)
    time.sleep(2)

    resident_parcel_data_id = partial(prepare_parcel_data_id,
                                      tab = "Residential",
                                      middle = "Residential")
    num_stories_id = resident_parcel_data_id(id="Label2")
    year_built_id = resident_parcel_data_id(id="YearBuiltLabel")
    num_bed_id = resident_parcel_data_id(id="NumberOfBedroomsLabel")
    num_full_bath_id = resident_parcel_data_id(id="NumberOfFullBathsLabel")
    num_half_bath_id = resident_parcel_data_id(id="NumberOfHalfBathsLabel")
    living_area_id = resident_parcel_data_id(id="FinishedLivingAreaLabel")
    basement_id = resident_parcel_data_id(id="Label1")
    basement_area_id = resident_parcel_data_id(id="Label4")

    num_stories = scrape_data_by_id(driver, num_stories_id)
    year_built = scrape_data_by_id(driver, year_built_id)
    num_bed = scrape_data_by_id(driver, num_bed_id)
    num_full_bath = scrape_data_by_id(driver, num_full_bath_id)
    num_half_bath = scrape_data_by_id(driver, num_half_bath_id)
    living_area = scrape_data_by_id(driver, living_area_id)
    basement = scrape_data_by_id(driver, basement_id)
    basement_area = scrape_data_by_id(driver, basement_area_id)

    return (num_stories, year_built, num_bed, num_full_bath,
            num_half_bath, living_area, basement, basement_area)

def create_data_row(parcel_id, valuation_data, resident_data):
    colnames = ["parcelNumber", "address", "appraisedValue", "numStories", 
                "yearBuilt", "numBedrooms", "numFullBaths", "numHalfBaths", 
                "livingArea", "basement", "basementArea"]
    data_row = namedtuple('Row', colnames)

    if len([parcel_id, *valuation_data, *resident_data]) == len(colnames):
        row = data_row(parcel_id, *valuation_data, *resident_data)
        return row
    else:
        msg = "[-] Missing necessary data. Expected data for: {}"
        print(msg.format(', '.join(colnames)))
        return
