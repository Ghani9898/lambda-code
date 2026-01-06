from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Chrome options (optional: run headless)
chrome_options = Options()
# chrome_options.add_argument("--headless")  # uncomment if you don't want browser GUI

# Initialize the driver
driver = webdriver.Chrome(options=chrome_options)
query = "Laptop"

# Open Amazon search page
driver.get(f"https://www.amazon.com/s?k={query}&crid=17ADEKT6RYTQN&sprefix={query}%2Caps%2C363&ref=nb_sb_noss_1")

# Give initial load time
time.sleep(3)

# Scroll loop
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Wait for new content to load
    time.sleep(3)
    
    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break  # No more content
    last_height = new_height

# Find product elements
elements = driver.find_elements(By.CLASS_NAME, "puisg-col")

# Print product info
for elem in elements:
    print(elem.text)
    print("-" * 50)

driver.quit()
