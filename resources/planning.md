# Planning: one week sprints

The following document will provide a running task list for the remainder of
the project.

## January 1st, 2018 - January 7th, 2018

* (Wasn't necessary) Add functionality to get cookies from the main website.
* (Complete) Get the rough draft script in shape to scrape the parcel numbers from the
  first results page.
* (~Complete) With the abbreviated parcel numbers, ensure that the requisite data can be
  scraped for each individual parcel number.


## January 8th, 2018 - January 14th, 2018

* Scrape the manually extract parcel numbers CSV file (website provided functionality to export).
* Refine logic to scrape data for parcel numbers, and add requisite exception handling when data is not given.


## January 15th, 2018 - January 21st, 2018

* Develop R script to aggregate and validate the housing data.
* Develop R script (or use the one above) to further prepare the data by geolocating the parcel
  number based on the address, and calculating the Great Circle distance from the warehouses.
