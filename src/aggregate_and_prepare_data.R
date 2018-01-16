# Aggregating housing data and finding geolocations

library(readr)
library(dplyr)
library(purrr)

# Set Up ####
#
src.dir <- getwd()
data.dir <- file.path(src.dir, '..', 'data', 'processed')


# Load Data ####
#
# Fetch all of the files associated with the housing data and the 
# parcel numbers CSV file.
data.dir.files <- list.files(data.dir)
parcel.numbers.file <- data.dir.files[grep("parcel", data.dir.files)]
housing.data.files <- data.dir.files[-grep("parcel", data.dir.files)]

# Load in the parcel numbers so we can check if we scraped all of 
# the necessary data.
parcels.df <- read_csv(file.path(data.dir, parcel.numbers.file))

housing.data.df <- housing.data.files %>% 
  # Load the data with the file name
  map(function(housing.data.file) {
    housing.data.df <- read_csv(file.path(data.dir, housing.data.file))
    return(housing.data.df)
  }) %>% 
  # Convert the list of data.frames into one data.frame
  bind_rows()

# Now check that all of the parcel numbers are represented in the 
# scraped housing data.frame
parcels <- parcels.df %>% 
  distinct(Parcels) %>% 
  pull()

scraped.parcels <- housing.data.df %>% 
  distinct(parcelNumber) %>% 
  select(parcelNumber) %>% 
  pull()

# Define simple function
"%ni%" <- Negate("%in%")

any(parcels %ni% scraped.parcels)  # Returns FALSE, so all is good!
