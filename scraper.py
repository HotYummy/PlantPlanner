from bs4 import BeautifulSoup
import requests
import math
import pymysql
from concurrent.futures import ThreadPoolExecutor
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options to run in headless mode
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

# Set up the WebDriver with the desired options
driver = webdriver.Chrome(options=chrome_options)

categories = ["Barrväxter", "Blomsterlök", "Bärbuskar", "Fruktträd", "Häckväxter", "Höstväxter", "Klängväxter", "Kryddväxter", "Medelhavsväxter", "Perenner", "Prydnadsbuskar", "Prydnadsträd", "Rosor", "Sommarplantor", "Vårblommor"]

# Establish a connection to the MariaDB database
conn = pymysql.connect(host='DESKTOP-N9CNRBA.local', user='dbadm', password='BAsse123//', db='blomsterlandet', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

def execute_sql_from_file(filename):
    # Get the directory of the current script
    current_directory = os.path.dirname(__file__)

    # Construct the absolute path to the SQL filei know that the data is 
    file_path = os.path.join(current_directory, filename)

    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"File '{filename}' does not exist.")
        return

    # Read SQL queries from the file
    with open(file_path, "r") as file:
        sql_queries = file.read()

    # Split SQL queries by semicolon to execute them individually
    queries = sql_queries.split(";")

    # Remove any empty or whitespace-only queries
    queries = [query.strip() for query in queries if query.strip()]

    # Execute each query
    with conn.cursor() as cursor:
        for query in queries:
            cursor.execute(query)
            conn.commit() 

def insert_data(batch_data):
    with conn.cursor() as cursor:
        # Insert new data
        sql = "INSERT INTO plants (name, latin_name, price, category, url, color, flowering_season, min_height, max_height, light, image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(sql, batch_data)
        
    # Commit the transaction
    conn.commit()

def scrape_plant_info(category):
    print(category)
    url = "https://www.blomsterlandet.se/produkter/vaxter/utomhus/"
    page_url = url + category.lower().replace("å", "a").replace("ä", "a").replace("ö", "o")
    page = requests.get(page_url)
    soup = BeautifulSoup(page.text, "html.parser")
    max_pages = math.ceil(int(soup.find("span", class_="PaginationComponentstyled__ResultText-sc-159t29c-2 fjLQRb").text.split(" ")[3]) / int(soup.find("span", class_="PaginationComponentstyled__ResultText-sc-159t29c-2 fjLQRb").text.split(" ")[1]))
    url = page_url + f"/?page={max_pages}&sorting=Name"
    driver.get(url)
    
    wait = WebDriverWait(driver, 50)
    wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ProductCardHeadstyled__ImageBox-sc-u1bzzj-1 dfUUPC']")))

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    
    images = soup.find("ul", class_ = "ProductListingBlockstyled__Container-sc-1krehu1-1 jLurqn").find_all("img")
    final_images = []
    for image in images:
        if "pollinator" not in image["src"]:
            final_images.append(image["src"])
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    plants = soup.find_all("a", class_="ProductCardBigstyled__Action-sc-1wubhum-1 eEFATJ")

    # Initialize a list to store batch insert data
    batch_data = []
    image_index = 0
    for plant in plants:
        url = "https://www.blomsterlandet.se" + plant['href']
        
        page = requests.get(url)
        plant_soup = BeautifulSoup(page.text, "html.parser")
        name = plant.find("div", class_ = "ProductCardBigstyled__Details-sc-1wubhum-5 iGehpc details").find("h2", class_="ProductCardBigstyled__Name-sc-1wubhum-6 ffvnpm").text if plant.find("div", class_ = "ProductCardBigstyled__Details-sc-1wubhum-5 iGehpc details").find("h2", class_="ProductCardBigstyled__Name-sc-1wubhum-6 ffvnpm") else None
        latin_name = plant.find("p", class_="ProductCardBigstyled__ScientificName-sc-1wubhum-7 fIovQu").text if plant.find("p", class_="ProductCardBigstyled__ScientificName-sc-1wubhum-7 fIovQu") else None
        price = plant.find("span", class_="ProductCardPricestyled__Normal-sc-1jcbqm3-2 idQXDB").text if plant.find("span", class_="ProductCardPricestyled__Normal-sc-1jcbqm3-2 idQXDB") else None
        image = final_images[image_index]
        data = plant_soup.find_all("div", class_ = "KeyValueListItemstyled__Item-sc-1ehnfjc-0 dZbsFt")
        color = None
        min_height = None
        max_height = None
        light = None
        flowering_season = None
        
        for subdata in data:
            if subdata.find("dt", class_ = "KeyValueListItemstyled__Key-sc-1ehnfjc-3 iLBqwu").text == "Blomningstid":
                flowering_season = subdata.find("dd", class_ = "KeyValueListItemstyled__Value-sc-1ehnfjc-4 bopNhI").text
                continue
            if subdata.find("dt", class_ = "KeyValueListItemstyled__Key-sc-1ehnfjc-3 iLBqwu").text == "Blomfärg":
                color = subdata.find("dd", class_ = "KeyValueListItemstyled__Value-sc-1ehnfjc-4 bopNhI").text
                continue
            if subdata.find("dt", class_ = "KeyValueListItemstyled__Key-sc-1ehnfjc-3 iLBqwu").text == "Läge":
                light = subdata.find("dd", class_ = "KeyValueListItemstyled__Value-sc-1ehnfjc-4 bopNhI").text
                continue
            if subdata.find("dt", class_ = "KeyValueListItemstyled__Key-sc-1ehnfjc-3 iLBqwu").text == "Förväntad sluthöjd":
                min_height = subdata.find("dd", class_ = "KeyValueListItemstyled__Value-sc-1ehnfjc-4 bopNhI").text.split(" ")[0]
                max_height = subdata.find("dd", class_ = "KeyValueListItemstyled__Value-sc-1ehnfjc-4 bopNhI").text.split(" ")[2]
            if subdata.find("dt", class_ = "KeyValueListItemstyled__Key-sc-1ehnfjc-3 iLBqwu").text == "Leveranshöjd":
                min_height = subdata.find("dd", class_ = "KeyValueListItemstyled__Value-sc-1ehnfjc-4 bopNhI").text.split(" ")[0]
                max_height = subdata.find("dd", class_ = "KeyValueListItemstyled__Value-sc-1ehnfjc-4 bopNhI").text.split(" ")[2]
        image_index = image_index + 1
        
        # Append data to batch_data list , color, page_url, flowering_season
        batch_data.append((name, latin_name, price, category, url, color, flowering_season, min_height, max_height, light, image))

        # Check if batch_data reaches a certain size
        if len(batch_data) >= 100:  # Adjust the batch size as needed
            # Submit batch insert task to thread pool executor
            with ThreadPoolExecutor() as executor:
                executor.submit(insert_data, batch_data)

            # Clear batch_data list for the next batch
            batch_data = []

    # Insert any remaining data in batch_data
    if batch_data:
        # Submit remaining batch insert task to thread pool executor
        with ThreadPoolExecutor() as executor:
            executor.submit(insert_data, batch_data)

if __name__ == '__main__':
    start_time = time.time()  # Record the start time
    
    execute_sql_from_file("create_database.sql")
    
    for category in categories:
        scrape_plant_info(category)
    # Close the database connection
    conn.close()
    end_time = time.time()  # Record the end time
    execution_time = end_time - start_time  # Calculate the execution time
        
    print(f"Program execution time: {execution_time} seconds")
