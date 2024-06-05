# Library imports
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Setup driver and get page
print("Setting up connection...")
driver = webdriver.Firefox()
driver.get("https://sante-infobase.canada.ca")

# Wait until page DOM is loaded
print("Waiting for load...")
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "ul#all_articles"))
)

# Find all article cards
print("Scraping articles...")
articles = driver.find_elements(By.CSS_SELECTOR, "ul#all_articles li")
output = []

# Start scraping info
for article in articles:
    link = article.find_element(By.CSS_SELECTOR, "div.col-md-10>h3>a")
    title = link.text.strip()
    url = link.get_attribute("href")

    description = article.find_element(By.CSS_SELECTOR, "div.col-md-10>p.mrgn-tp-md").text.strip()
    date = article.find_element(By.CSS_SELECTOR, "div.col-md-10>p.small").text.strip()
    date = date.split(' ')[-1]

    topics = article.find_elements(By.CSS_SELECTOR, "div.col-md-10>div.labelContainer>div.label-info")
    topics = ", ".join([topic.text.strip() for topic in topics])
    formats = article.find_elements(By.CSS_SELECTOR, "div.col-md-10>div.labelContainer>div.label-default")
    formats = ", ".join([format.text.strip() for format in formats])
    
    icon = article.find_element(By.CSS_SELECTOR, "div.col-md-2>img").get_attribute("src")
    icon = icon.split("/")[-1]

    # Append to output
    output.append({
        "title": title,
        "link": url,
        "description": description,
        'date': date,
        'topic': topics,
        'format': formats,
        'icon': icon,
        'org': 'PHAC'
    })

# Close driver and write to file
print("Saving to file...")
driver.quit()

with open("./fr/unprocessed/articles.json", "w") as f:
    json.dump(output, f, indent=4)