# PBA-Website-Scraper

## How to Run
Activate pipenv
```
pipenv shell
python3 pba.py
```

## Step by Step Process of the Script
1. Get needed team links to be scrape
2. Get needed individual player links to be scraped
3. Pass the links as input to the get details functions for teams(Downloads the logo img as well) and players.
4. Run the functions Asynchrounously using concurrent.futures

## Simple Process
get links -> execute functions asynchronously -> transform data to DataFrame -> CSV
