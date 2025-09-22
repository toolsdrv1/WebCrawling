import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import io

st.title("Croma Product Scraper")

st.markdown("""
Upload a CSV containing product URLs in a column named `URL`. 
The app will scrape Title, Product ID, SKU, MRP, and Price for each product.
""")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"Loaded {len(df)} URLs from CSV")

    if st.button("Start Scraping"):
        st.info("Scraping in progress... Browser window will open.")

        # Selenium setup (no headless)
        driver = webdriver.Chrome()

        # Prepare lists
        product_ids = []
        titles = []
        skus = []
        mrps = []
        prices = []

        for url in df['URL']:
            driver.get(url)
            time.sleep(5)  # wait for JS

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

            # Convert price and MRP to float
            if price != "N/A":
                price = float(re.sub(r'[^\d.]', '', price.replace(',', '')))
            if mrp != "N/A":
                mrp = float(re.sub(r'[^\d.]', '', mrp.replace(',', '')))

            # Append
            product_ids.append(product_id)
            titles.append(title)
            skus.append(sku)
            mrps.append(mrp)
            prices.append(price)

            st.write(f"Scraped: {title}")

        driver.quit()

        # Update DataFrame
        df['Product ID'] = product_ids
        df['Title'] = titles
        df['SKU'] = skus
        df['MRP'] = mrps
        df['Price'] = prices

        st.success("Scraping completed!")

        # Display updated table
        st.dataframe(df)

        # Download updated CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="Download Updated CSV",
            data=csv_buffer.getvalue(),
            file_name="products_data_updated.csv",
            mime="text/csv"
        )
