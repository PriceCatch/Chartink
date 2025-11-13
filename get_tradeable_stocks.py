# Original Code. Benny Thadikaran. https://github.com/BennyThadikaran.
# Modified by S V SUDHARSHAN a.k.a PriceCatch. https://github.com/PriceCatch.
# Example output from ChartInk.  - Only retain stock symbol (nsecode) column from the scanner.
# [
#     {
#         "sr": 1,
#         "nsecode": "MPSLTD",
#         "name": "Mps Limited",
#         "bsecode": "532440",
#         "per_chg": 11.25,
#         "close": 2196.1,
#         "volume": 186378,
#     },
# ]

import requests
import re
import pandas as pd

# --- Constants ---
URL = "https://chartink.com/screener/process"
# --- If you want to retain below columns, remove them from this list ---
COLUMNS_TO_DROP = ['sr', 'name', 'bsecode', 'per_chg', 'close', 'volume']

# change this path as per your environment
OUTPUT_FILE_PATH = r"C:\Users\svsud\PycharmProjects\ProfitCentric\stockslist/tradeable_stocks.csv"

# Paste the scan clause copied from ChartInk below
scan_clause = '( {cash} ( ( {cash} ( market cap > 7999 and 180 days ago close > 20 ) ) ) ) '

with requests.session() as s:
    res = s.get(URL)

    if not res.ok:
        exit(f"1st req failed: {res.status_code} - {res.reason}")

    csrf_match = re.search(
        r'<meta\s+name="csrf-token"\s+content="([^"]*)"\s*/?>',
        res.text,
    )

    if csrf_match is None:
        exit("Failed to capture CSRF token")

    csrf_token = csrf_match.group(1)

    res = s.post(
        URL,
        headers={"X-CSRF-TOKEN": csrf_token},
        data=dict(scan_clause=scan_clause),
    )

    if not res.ok:
        exit(f"2nd req failed: {res.status_code} - {res.reason}")

    data = res.json()
    df = pd.DataFrame(data["data"])
    df.drop(columns=COLUMNS_TO_DROP, inplace=True)
    df.rename(columns={"nsecode": "Symbol"}, inplace=True)
    df.set_index("Symbol", inplace=True)
    df.sort_index(inplace=True)

    df.to_csv(OUTPUT_FILE_PATH)
    print(f"Scanner run successfully. {len(df)} stocks filtered.")
    print(f"Data saved to: {OUTPUT_FILE_PATH}")

# EOF.