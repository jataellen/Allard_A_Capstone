## Scraping Methods

This directory contains the code to scrape all necessary cases from CanLII, which is all consolidated into the file `scraping.ipynb`. The file also has a step-by-step process that upon completion, would yield around 45k files that we used for this project. Each of the sub-directories in this folder are:

### 45k_formatted_cases
All of the scraped files in `.txt` format.

### 45k_scraped_html_files
All of the scraped files in `.html` format.

### case_data
The annotated `cases.csv` file, which contains the gold labels for any further model processing.

### decisions_by_year
The `.html` files that are sorted by year, and further used to scrape each individual case file by year.

### formatted_cases
All the case files that were present in the gold annotated csv file in `.txt` format.

### onltb_metadata
The folder that contains code to extract metadata through API calls.

### scraped_html_files
All the case files that were present in the gold annotated csv file in `.html` format.

### scraped_searches
Links to all the case files that were present in the gold annotated csv file, to be used to get the text.