import os
import sys
import time
from selenium import webdriver
from utils import prepare_webscraper, HousingData
from data import PARCEL_DATA_CSS_IDS

class ParcelDataScraper:
    URL = "http://muskingumcountyauditor.org/Data.aspx?ParcelID={}"
    
    def __init__(self, parcel_id=None):
        self.base_tab_js = "__doPostBack('ctl00$ContentPlaceHolder1$mnuData', '1')"
        self.valuation_tab_js = "__doPostBack('ctl00$ContentPlaceHolder1$mnuData','2')"
        self.residential_tab_js = "__doPostBack('ctl00$ContentPlaceHolder1$mnuData','8')"

        if parcel_id:
            self.set_parcel_id(parcel_id)
        else:
            self.set_parcel_id('')

    def set_parcel_id(self, parcel_id):
        if type(parcel_id) == "str":
            self.parcel_id = parcel_id
            self._redirect_driver_to_parcel_data()
        else:
            print("[ERROR] parcel_id must be a string")
        
    def _redirect_driver_to_parcel_id(self):
        if self.parcel_id is not None:
            url = ParcelDataScraper.URL.format(self.parcel_id)
            self.driver = prepare_webscraper(url)
        else:
            print("[ERROR] parcel_id has not been given yet.")

    def _scrape_base_tab(self):
        # Navigate to 'Base' tab and wait a couple of seconds 
        self.driver.execute_script(self.base_tab_js)
        time.sleep(2)

        # Scrape data off of page
        try:
            address = self.driver.find_element_by_id(address_id).text
        except Exception as err:
            address = None

        return address

    def _scrape_valuation_tab(self):
        # Navigate to 'Valuation' tab and wait a couple of seconds
        self.driver.execute_script(self.valuation_tab_js)
        time.sleep(2)

        # Scrape data off page
        try:
            valuation = self.driver.find_element_by_id(valuation_id).text
        except Exception as err:
            valuation = None

        return valuation

    def _scrape_residential_tab(self):
        # Navigate to 'Residential' tab and wait a couple of seconds
        self.driver.execute_script(self.residential_tab_js)
        time.sleep(2)

        # Scrape data off of page
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
            num_stories = None
            year_built = None
            num_bed = None
            num_full_bath = None
            num_half_bath = None
            living_area = None
            basement = None
            basement_area = None

        residential_data = {
                'numStories': num_stories,
                'yearBuilt': year_built,
                'numBed': num_bed,
                'numFullBath': num_full_bath,
                'numHalfBath': num_half_bath,
                'livingArea': living_area,
                'basement': basement,
                'basementArea': basement_area
            }
        return residential_data

    def scrape_data(self):
        address = self._scrape_base_tab()
        valuation = self._scrape_valuation_tab()
        residential_data = self._scrape_residential_tab()

        row = HousingData(
                    parcelNumber   = self.parcel_id,
                    address        = address,
                    appraisedValue = valuation,
                    numStories     = residential_data['numStories'],
                    yearBuilt      = residential_data['yearBuilt'],
                    numBedrooms    = residential_data['numBed'],
                    numFullBaths   = residential_data['numFullBath'],
                    numHalfBaths   = residential_data['numHalfBath'],
                    livingArea     = residential_data['livingArea'],
                    basement       = residential_data['basement'],
                    basementArea   = residential_data['basementArea']
                )

        return row

