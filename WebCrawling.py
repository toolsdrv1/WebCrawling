# %%
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re

# Load the existing CSV (assume URLs are in column 'URL' or column A)
input_csv = "products_data.csv"
df = pd.read_csv(input_csv)

# Initialize Selenium driver
driver = webdriver.Chrome()

# Prepare lists to store scraped data
product_ids = []
titles = []
skus = []
mrps = []
prices = []

for url in df['URL']:  # Adjust column name if needed
    driver.get(url)
    time.sleep(5)  # wait for JS to load

    # ---- Extract Data ----
    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1").text
    except:
        title = "N/A"

    try:
        product_id = re.search(r"/p/(\d+)", driver.current_url).group(1)
    except:
        product_id = "N/A"

    try:
        price = driver.find_element(By.CSS_SELECTOR, "span.amount").text
    except:
        price = "N/A"

    try:
        mrp = driver.find_element(
            By.XPATH,
            "/html/body/main/div/div[3]/div/div[1]/div[2]/div[1]/div/div/div/div[3]/div/ul/li[1]/section[1]/div[2]/span[1]"
        ).text
    except:
        mrp = "N/A"

    try:
        sku = driver.find_element(
            By.XPATH, "//td[contains(text(),'Model Number')]/following-sibling::td"
        ).text
    except:
        match = re.search(r"\((.*?)\)", title)
        sku = match.group(1) if match else "N/A"

    #extract numbers from price and mrp
    if price != "N/A":
        price = float(re.sub(r'[^\d.]', '', price.replace(',', '')))
    if mrp != "N/A":
        mrp = float(re.sub(r'[^\d.]', '', mrp.replace(',', '')))
    

    # Append to lists
    product_ids.append(product_id)
    titles.append(title)
    skus.append(sku)
    mrps.append(mrp)
    prices.append(price)

    print(f"Scraped: {title}")

driver.quit()

# ---- Add new columns to the DataFrame ----
df['Product ID'] = product_ids
df['Title'] = titles
df['SKU'] = skus
df['MRP'] = mrps
df['Price'] = prices

output_csv = "products_data_updated.csv"
# ---- Save back to the same CSV ----
df.to_csv(output_csv, index=False)
print(f"Updated CSV saved: {input_csv}")



