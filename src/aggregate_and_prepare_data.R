# Aggregating housing data and finding geolocations

library(readr)
library(dplyr)
library(purrr)

# Set Up ####
#
src.dir <- getwd()
data.dir <- file.path(src.dir, '..', 'data', 'processed')
consume.data.dir <- file.path(src.dir, '..', 'data', 'consume')

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

# Geolocation ####
#
library(ggmap)

# Create a new column with the city and state appended to the address
housing.data.df <- housing.data.df %>% 
  mutate(fullAddress = paste(address, ", Zanesville OH", sep=""))

# Fetch the address for each address
housing.data.geocodes <- housing.data.df %>%
  #filter(row_number() < 50) %>% 
  select(fullAddress) %>% 
  transpose() %>% 
  map(function(row) {
    address.geocode <- geocode(row$fullAddress)
    Sys.sleep(0.2)
    return(address.geocode)
  })

# Add the latitude and longitude to the dataset
housing.data.df$latitude <-sapply(housing.data.geocodes, function(geo) geo$lat)
housing.data.df$longitude <- sapply(housing.data.geocodes, function(geo) geo$lon)

# Distance from Warehouse ####
#
library(geosphere)

warehouse.address <- "1525 PERSHING RD, Zanesville OH"
warehouse.geocode <- geocode(warehouse.address)  # Currently exceeded queries

# Let's manually find the latitude and longitude
warehouse.lat <- 39.925579
warehouse.long <- -82.026608

dist.from.warehouse.meters <- housing.data.df %>% 
  select(latitude, longitude) %>% 
  transpose() %>% 
  map(function(row) {
    dist <- distHaversine(c(warehouse.long, warehouse.lat), 
                          c(row$longitude, row$latitude))
    return(dist)
  }) %>% 
  unlist()

housing.data.df$distanceFromWarehouseMeters <- dist.from.warehouse.meters


# Save the prepared data ####
#
write_csv(housing.data.df,
          file.path(consume.data.dir, "zanesville_oh_housing_data.csv"),
          col_names = TRUE)
