from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import logging
import time
import re

# Configure logging
logging.basicConfig(level=logging.INFO, filename='scraper.log',
                    format='%(asctime)s:%(levelname)s:%(message)s')

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headlessly (no GUI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_amazon_product(url):
    driver = create_driver()
    product_details = {}

    try:
        logging.info(f"Navigating to Amazon URL: {url}")
        driver.get(url)
        
        wait = WebDriverWait(driver, 0.1)
        name_tag = wait.until(EC.presence_of_element_located((By.ID, 'productTitle')))
        product_details['name'] = name_tag.text.strip()
        logging.info(f"Product Name: {product_details['name']}")

        try:
            price_tag = driver.find_element(By.CSS_SELECTOR, 'span.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay')
            product_details['price'] = price_tag.text.strip()
            logging.info(f"Price: {product_details['price']}")
        except:
            try:
                price_tag = driver.find_element(By.ID, 'priceblock_dealprice')
                product_details['price'] = price_tag.text.strip()
                logging.info(f"Price: {product_details['price']}")
            except:
                product_details['price'] = 'N/A'
                logging.warning("Price element not found.")

        try:
            image_tag = driver.find_element(By.ID, 'landingImage')
            product_details['image'] = image_tag.get_attribute('src')
            logging.info(f"Image URL: {product_details['image']}")
        except:
            product_details['image'] = 'N/A'
            logging.warning("Image element not found.")

        try:
            rating_tag = driver.find_element(By.XPATH, '//a[@class="a-popover-trigger a-declarative"]/span[@class="a-size-base a-color-base"]')
            star_rating = rating_tag.text.strip()  # Extracting the star rating
            product_details['star_rating'] = star_rating + " out of 5 stars"
            logging.info(f"Star Rating: {product_details['star_rating']}")
        except:
            product_details['star_rating'] = 'N/A'
            logging.warning("Star rating element not found.")

        # Extracting the total number of reviews
        try:
            reviews_tag = driver.find_element(By.ID, 'acrCustomerReviewText')
            product_details['reviews'] = reviews_tag.text.strip()
            logging.info(f"Reviews: {product_details['reviews']}")
        except:
            product_details['reviews'] = 'N/A'
            logging.warning("Reviews element not found.")

        product_details['link'] = url

    except Exception as err:
        logging.error(f"An error occurred while scraping Amazon: {err}")
    finally:
        driver.quit()

    return product_details

def find_flipkart_link(product_name):
    words = product_name.split()[:5]
    query = '+'.join(words)
    url = f'https://www.flipkart.com/search?q={query}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        logging.info("Flipkart search request successful!")
        soup = BeautifulSoup(response.content, 'html.parser')
    
        logging.info(f"{url}")

        for link in soup.find_all('a', href=True):
            if 'p/' in link['href']:
                product_link = 'https://www.flipkart.com' + link['href']
                logging.info(f"Found Flipkart product link: {product_link}")
                return product_link

        logging.warning("No product links found on Flipkart.")
        return None
    else:
        logging.error(f"Failed to retrieve the Flipkart search page. Status code: {response.status_code}")
        return None

def scrape_flipkart_product(url):
    driver = create_driver()
    product_details = {}

    try:
        logging.info(f"Navigating to Flipkart URL: {url}")
        driver.get(url)
        wait = WebDriverWait(driver, 0.1)

        try:
            close_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'✕')]")))
            close_button.click()
            logging.info("Login pop-up closed.")
        except:
            logging.info("No login pop-up detected.")

        name_tag = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.VU-ZEz')))
        product_details['name'] = name_tag.text.strip()
        logging.info(f"Product Name: {product_details['name']}")

        try:
            price_tag = driver.find_element(By.CSS_SELECTOR, 'div.Nx9bqj.CxhGGd')
            product_details['price'] = price_tag.text.strip()
            logging.info(f"Price: {product_details['price']}")
        except:
            product_details['price'] = 'N/A'
            logging.warning("Price element not found.")

        try:
            image_tag = driver.find_element(By.CSS_SELECTOR, 'img._396cs4')
            product_details['image'] = image_tag.get_attribute('src')
            logging.info(f"Image URL: {product_details['image']}")
        except:
            product_details['image'] = 'N/A'
            logging.warning("Image element not found.")

        product_details['link'] = url
            
    except Exception as err:
        logging.error(f"An error occurred while scraping Flipkart: {err}")
    finally:
        driver.quit()

    return product_details

def get_first_product_details(query):
    driver = create_driver()
    product_details = {}

    try:
        # Format the search query for Reliance Digital
        words = query.split()[:7]
        limited_query = '%20'.join(words)
        limited_query = re.sub(r'[(){}[\]]', '', limited_query)
        url = f"https://www.reliancedigital.in/search?q={limited_query}:relevance"
        logging.info(f"Visiting Reliance Digital URL: {url}")
        driver.get(url)
        time.sleep(5)  # Wait for the page to load

        wait = WebDriverWait(driver, 1)  # Increase wait time to 10 seconds

        # Wait for the product elements to be present
        try:
            # Adjust selector for the product title
            title_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "p.sp__name"))  # Selector for product name
            )
            product_details['name'] = title_element.text.strip()
            logging.info(f"Product Title: {product_details['name']}")
        except Exception as e:
            product_details['name'] = 'N/A'
            logging.warning("Product title element not found.")

        # Extract price
        try:
            # Updated selector for price
            price_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.StyledPriceBoxM__PriceWrapper-sc-1l9ms6f-0 span:nth-of-type(2)"))  # Select the second span containing the price
            )
            product_details['price'] = price_element.text.strip()
            logging.info(f"Price: {product_details['price']}")
        except Exception as e:
            product_details['price'] = 'N/A'
            logging.warning("Price element not found.")
        
        try:
            # Selector for product link
            link_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.sp a[href*='/']"))  # Adjusted to find the link in the correct div
            )
            product_details['link'] = f"{link_element.get_attribute('href').strip()}"  # Complete the URL
            logging.info(f"Product Link: {product_details['link']}")
        except Exception as e:
            product_details['link'] = 'N/A'
            logging.warning("Product link element not found.")

    except Exception as e:
        logging.error("Error occurred while scraping Reliance Digital: " + str(e))

    finally:
        driver.quit()

    return product_details
