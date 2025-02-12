from flask import Flask, render_template, request
import pandas as pd
from scraper import scrape_amazon_product, find_flipkart_link, scrape_flipkart_product, get_first_product_details
from predictor import PriceDropPredictor
from datetime import datetime

app = Flask(__name__)

# Load your dataset (assuming it's a CSV file)
dataset_path = 'amazon_data.csv'  # Update with the actual path to your dataset

# Ensure dataset is loaded globally
def load_dataset():
    return pd.read_csv(dataset_path)

dataset = load_dataset()

# Initialize the predictor
predictor = PriceDropPredictor(dataset)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    amazon_product_url = request.form['url']
    amazon_data = scrape_amazon_product(amazon_product_url)
    product_name = amazon_data['name']
    current_price = amazon_data['price']
    product_link = amazon_data['link']

    # Get the current date to add the price in the correct column
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Reload the dataset to ensure it's up-to-date
    dataset = load_dataset()

    # Check if the product name is in the dataset
    if product_name in dataset['name'].values:
        # Extract prices from the dataset for the specific product
        product_row = dataset[dataset['name'] == product_name]
        product_prices = product_row.iloc[:, 3:].values.flatten()  # Assuming price columns start from index 3
        
        # Clean the prices and convert to float
        cleaned_prices = [predictor.clean_price(price) for price in product_prices if pd.notna(price)]

        # Get predicted probability of price drop
        prediction = predictor.predict_price_drop_probability(cleaned_prices)
        
        # Get the lowest, current, and highest prices
        low_price = int(min(cleaned_prices))
        current_price = current_price
        high_price = int(max(cleaned_prices))

        # Create the price graph and return base64 plot
        plot_url = predictor.create_price_plot(low_price, current_price, high_price)
        
        flipkart_product_url = find_flipkart_link(product_name)
        flipkart_data = {}
        reliance_product_data = {}

        if flipkart_product_url:
            flipkart_data = scrape_flipkart_product(flipkart_product_url)
            reliance_product_data = get_first_product_details(product_name)
            
        # Pass low, current, and high prices to the template along with the plot
        return render_template('result.html', amazon=amazon_data, flipkart=flipkart_data, reliance=reliance_product_data, prediction=prediction, plot_url=plot_url, low_price=low_price, current_price=current_price, high_price=high_price)
    else:
        # Product not found in the dataset, so we add a new row
        new_srno = dataset['srno'].max() + 1  # Get next serial number
        new_row = {
            'srno': new_srno,
            'name': product_name,
            'link': product_link,
            today_date: current_price  # Add price under today's date column
        }

        new_row_df = pd.DataFrame([new_row])  # Convert the new row into a DataFrame

        # Concatenate the new row to the dataset
        dataset = pd.concat([dataset, new_row_df], ignore_index=True)

        # Save the updated dataset back to the CSV
        dataset.to_csv(dataset_path, index=False)

        flipkart_product_url = find_flipkart_link(product_name)
        flipkart_data = {}
        reliance_product_data = {}

        if flipkart_product_url:
            flipkart_data = scrape_flipkart_product(flipkart_product_url)
            reliance_product_data = get_first_product_details(product_name)
        
        return render_template('result.html', amazon=amazon_data, flipkart=flipkart_data, reliance=reliance_product_data)

if __name__ == '__main__':
    app.run(debug=True)
