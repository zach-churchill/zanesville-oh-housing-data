URLS = {
        'advanced-search-results': "http://www.muskingumcountyauditor.org/Results.aspx?SearchType=Advanced&Criteria=20g%2byYTTdkDKRrEbpO1sLV9b36Zp5GCYSiEbzYPtPXU%3d"
        'fmt-parcel-data': "http://muskingumcountyauditor.org/Data.aspx?ParcelID={}"
    }

PARCEL_CSS_ID = "ContentPlaceHolder1_{}_fvData{}_{}"
PARCEL_DATA_CSS_IDS = {
    "Base_tab": {
        "address": PARCEL_CSS_ID.format("Base", "Profile", "AddressLabel")
    },
    "Valuation_tab": {
        "valuation": PARCEL_CSS_ID.format("Valuation", "Valuation", "Label1")
    },
    "Residential_tab": {
        "num_stories": PARCEL_CSS_ID.format(
                            "Residential", "Residential", "Label2"
                        ),
        "year_built": PARCEL_CSS_ID.format(
                            "Residential", "Residential", "YearBuiltLabel"
                        ),
        "num_bed": PARCEL_CSS_ID.format(
                            "Residential", "Residential",
                            "NumberOfBedroomsLabel"
                        ),
        "num_full_bath": PARCEL_CSS_ID.format(
                            "Residential", "Residential", 
                            "NumberOfFullBathsLabel"
                        ),
        "num_half_bath": PARCEL_CSS_ID.format(
                            "Residential", "Residential",
                            "NumberOfHalfBathsLabel"
                        ),
        "living_area": PARCEL_CSS_ID.format(
                            "Residential", "Residential"
                            "FinishedLivingAreaLabel"
                        ),
        "basement": PARCEL_CSS_ID.format(
                            "Residential", "Residential", "Label1"
                        ),
        "basement_area": PARCEL_CSS_ID.format(
                            "Residential", "Residential", "Label4"
                        )
    }
}
