'''
Copyright (c) 2025 S V SUDHARSHAN a.k.a PriceCatch.
visit http://github.com/PriceCatch for more code and info.
Watch my technical analysis videos at https://www.youtube.com/@PriceCatch

Licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/.

Attribution:
- The first two lines must be placed in comments at the header of your code.

- purpose: An example to extract previous 3H Breakout stocks from Chartink Atlas public Dashboard
- Dashboard URL: https://chartink.com/dashboard/318199
- The code uses Selenium to load the page, waits for the table to load, saves the page source,
  and then uses BeautifulSoup and pandas to parse and save the data to a CSV file with cleaned headers.
- first run at 9.18 AM and repeat every 3 minutes till 9.45 AM. This will capture stocks breaking out in the previous 3H candle
  
'''

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from bs4 import BeautifulSoup
from io import StringIO  # Added import for StringIO

# Setup Edge browser
options = Options()
# Uncomment to run headless if desired
options.add_argument("--headless")
driver = webdriver.Edge(options=options)  # Ensure msedgedriver is in PATH

url = "https://chartink.com/dashboard/318199"

OUTPUT_FILE_PATH = "/Users/svsud/Downloads/prev3H_BO_stocks_from_atlas.csv"

try:
    # Load the dashboard
    driver.get(url)
    print("Page loaded. Waiting for tables to appear...")

    # Wait for at least one vgt-table to be present (up to 30 seconds)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'vgt-table')]"))
    )
    print("Tables found. Waiting for data to populate...")
    time.sleep(5)  # Allow data to load

    # Save page source to file
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved page source to 'page_source.html'.")

except Exception as e:
    print(f"Error during page load: {e}")
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved page source to 'page_source.html' for debugging.")

finally:
    driver.quit()

# Step 2: Read and process the saved page_source.html
try:
    with open("page_source.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Find all vgt-tables
    tables = soup.find_all("table", class_="vgt-table")
    print(f"Found {len(tables)} vgt-table instances in page_source.html.")

    if tables:
        # Select the last table
        last_table = tables[-1]

        # Extract clean headers from <th> elements (only the <span> text)
        headers = [th.find("span").text.strip() for th in last_table.find_all("th")]
        print("Cleaned headers:", headers)

        # Convert to HTML string for pandas
        table_html = str(last_table)

        # Parse with pandas, using StringIO to avoid FutureWarning
        df = pd.read_html(StringIO(table_html))[0]
        # Assign clean headers
        df.columns = headers

        # Sort by Change Percent in descending order
        df = df.sort_values(by="Chngprcntprvclose", ascending=False)
        print("Table data extracted and sorted by Symbol (ascending). Sample:")
        print(df.head())

        # Save to CSV
        df.to_csv(OUTPUT_FILE_PATH, index=False)
        print(f"Data saved to {OUTPUT_FILE_PATH} with cleaned headers and sorted by Change %.")
    else:
        print("No vgt-table found in page_source.html.")

except Exception as e:
    print(f"Error processing page_source.html: {e}")

# EOF.
