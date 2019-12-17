# electiondata
Easy to use .csv results for the 2015 and 2019 Canadian Federal Elections and some simple insights from the data.

## Data
Elections Canada provides summary data for elections in .csv formats, but the schema isn't consistent from year to year and contains a lot of duplication. You can get the retrieve these files yourself from elections Canada, or use the copies we've stored here.

- `data/elections_data_2015.csv` retreivable from Elections Canada [here](https://www.elections.ca/content.aspx?section=res&dir=rep/off/42gedata&document=summary&lang=e)
- `data/elections_data_2019.csv` retrievable from Elections Canada [here](https://enr.elections.ca/National.aspx?lang=e)

The `data_operations` module contains functions to clean up and standardize this data. We've also pre-generated two csv's with this the standardized data in them so you don't have to do this everytime.

- `data/parsed_ridings_data_2015.csv`
- `data/parsed_ridings_data_2019.csv`

The new schema is as follows:

