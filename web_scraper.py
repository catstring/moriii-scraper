from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Automatically install and set up ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Function to scrape products from a single category
def scrape_category(category_url):
    category_product_names = []
    driver.get(category_url)
    
    while True:
        # Wait for the product listings to load on the page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h6[itemprop="name"]'))
        )
        
        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find all product names
        products = soup.find_all('h6', itemprop='name')
        for product in products:
            product_name = product.text.strip()
            category_product_names.append(product_name)
            print(product_name)
        
        # Check if there is a next page and navigate to it
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'a.next.page-numbers')
            next_button.click()
            WebDriverWait(driver, 10).until(
                EC.staleness_of(next_button)
            )  # Wait until the old page is gone and the new page is loaded
        except Exception:
            print("No more pages in this category.")
            break
    
    return category_product_names

# Navigate to the main product page
driver.get("https://www.moriii.com/#products")

# Wait for the products section to load
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="product-category"]'))
)

# Find all product category links
category_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="product-category"]')

# Store URLs of already processed categories
processed_categories = set()

all_product_names = []

# Iterate through each category
for i, link in enumerate(category_links):
    # Re-fetch the category links on each iteration to avoid stale elements
    category_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="product-category"]')
    category_url = category_links[i].get_attribute('href')
    
    # Skip this category if it has already been processed
    if category_url in processed_categories:
        continue
    
    # Mark this category as processed
    processed_categories.add(category_url)
    
    print(f"Scraping category: {category_url}")
    
    # Scrape products from the current category
    category_product_names = scrape_category(category_url)
    
    # Add the category's products to the overall list
    all_product_names.extend(category_product_names)
    
    # Navigate back to the main product page before moving to the next category
    driver.get("https://www.moriii.com/#products")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="product-category"]'))
    )
    print(f"Finished scraping category: {category_url}")

# Close the WebDriver
driver.quit()

# Print all collected product names
print("Collected all product names:")
for name in all_product_names:
    print(name)
