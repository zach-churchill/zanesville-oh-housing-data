library(readr)
library(dplyr)
library(purrr)
library(cowplot)

src.dir <- getwd()
data.dir <- file.path(src.dir, '..', 'data', 'processed')
consume.data.dir <- file.path(src.dir, '..', 'data', 'consume')

prepared.housing.data.file <- file.path(consume.data.dir, 
                                        "zanesville_oh_housing_data.csv")

housing.df <- read_csv(prepared.housing.data.file)

# First, let's see how many records contain NA in the row
rows.contains.na <- apply(is.na(housing.df),
                         FUN = function(row) ifelse(TRUE %in% row, 1, 0),
                         MARGIN = 1) %>% 
                    sum()
sprintf("The are %d rows that contain a NA value", rows.contains.na)

housing.detail.contains.na <- housing.df %>% 
  transpose() %>% 
  map(function(row) {
    row.vector <- unlist(row)
    ifelse(all(is.na(row.vector[4:9])), 1, 0)
  }) %>% 
  unlist() %>% 
  sum()
sprintf("There %d rows where the housing detail contain a NA value",
        housing.detail.contains.na)

# Let's see if we can fix the missing lat and long data
library(ggmap)

found.missing.geocodes <- housing.df %>%
  filter(is.na(latitude)) %>% 
  select(fullAddress) %>% 
  transpose() %>% 
  map(function(row) {
    address.geocode <- geocode(row$fullAddress)
    Sys.sleep(0.2)
    return(address.geocode)
  })

housing.df$latitude[is.na(housing.df$latitude)] <- sapply(found.missing.geocodes, 
                                                          function(geo) geo$lat)
housing.df$longitude[is.na(housing.df$longitude)] <- sapply(found.missing.geocodes, 
                                                          function(geo) geo$lon)  

# Now, fix the missing distance data
dist.from.warehouse.meters <- housing.df %>% 
  filter(is.na(distanceFromWarehouseMeters)) %>% 
  select(latitude, longitude) %>% 
  transpose() %>% 
  map(function(row) {
    dist <- distHaversine(c(warehouse.long, warehouse.lat), 
                          c(row$longitude, row$latitude))
    return(dist)
  }) %>% 
  unlist()

missing.distances <- is.na(housing.df$distanceFromWarehouseMeters)
housing.df$distanceFromWarehouseMeters[missing.distances] <- dist.from.warehouse.meters

# Write the data to be safe!
write_csv(housing.df,
          prepared.housing.data.file,
          col_names = TRUE)


# Data Munging ####
#
# Let's check how many appraisedValue entries are missing
sum(is.na(housing.df$appraisedValue))  # There are 11 missing appraised values - Fix by hand?

# Yep, fix by hand:
found.missing.appraised.values <- c("$93,300.00", "$122,500.00", "$25,700.00",
                                   "$8,800.00", "$3,900.00", "$900.00", "$400.00",
                                   "$300.00", "$200.00", "70,900.00", NA)
housing.df$appraisedValue[is.na(housing.df$appraisedValue)] <- found.missing.appraised.values

# Also, parcel number 81-60-03-29-000 was missing detail
parcel.nb.idx <- which(housing.df$parcelNumber == "81-60-03-29-000")
housing.df$numStories[parcel.nb.idx] <- 2
housing.df$yearBuilt[parcel.nb.idx] <- 1920
housing.df$numBedrooms[parcel.nb.idx] <- 3
housing.df$numFullBaths[parcel.nb.idx] <- 1
housing.df$numHalfBaths[parcel.nb.idx] <- 1
housing.df$livingArea[parcel.nb.idx] <- 1288
housing.df$basement[parcel.nb.idx] <- "YES"
housing.df$basementArea[parcel.nb.idx] <- 644

# Now, scrub the appraisedValues column and reassign as doubles
scrubbed.appraised.values <- as.double(gsub("^\\$|\\,", "", housing.df$appraisedValue))
sum(is.na(scrubbed.appraised.values))  # Ensure only one is missing
housing.df$appraisedValue <- scrubbed.appraised.values

# Write the data to be safe!
write_csv(housing.df,
          prepared.housing.data.file,
          col_names = TRUE)
