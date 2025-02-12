import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg for non-GUI backend
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from io import BytesIO
import base64

class PriceDropPredictor:
    def __init__(self, dataset):
        self.model = None
        self.scaler = None
        self.train_model(dataset)

    def clean_price(self, price):
        """Clean the price string and convert it to a float."""
        if isinstance(price, str):  # Check if the price is a string
            price = price.replace('₹', '').replace(',', '').strip()  # Remove currency symbol and commas
        return float(price)  # Convert to float

    def train_model(self, data):
        # Prepare data
        prices = data.iloc[:, 3:].values  # Assuming price columns start from index 3
        labels = []

        # Create labels: 1 if the price drops at least once, else 0
        for price_row in prices:
            price_changes = np.diff([self.clean_price(price) for price in price_row if pd.notna(price)])
            labels.append(1 if any(change < 0 for change in price_changes) else 0)

        # Convert to numpy arrays
        labels = np.array(labels)

        # Use only the last price and the average change as features
        feature_list = []
        for row in prices:
            cleaned_prices = [self.clean_price(price) for price in row if pd.notna(price)]
            if len(cleaned_prices) < 5:
                continue
            recent_price = cleaned_prices[-1]
            avg_change = np.mean(np.diff(cleaned_prices))
            feature_list.append([recent_price, avg_change])

        # Convert to numpy arrays and handle NaN values
        X = np.array(feature_list)
        y = labels[:len(X)]

        # Remove any samples with NaN values
        mask = np.all(~np.isnan(X), axis=1)
        X = X[mask]
        y = y[mask]

        # Split the dataset into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale features
        self.scaler = StandardScaler()
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)

        # Create and train the model
        self.model = LogisticRegression()
        self.model.fit(X_train, y_train)

    def predict_price_drop_probability(self, prices):
        # Clean prices before processing
        cleaned_prices = [self.clean_price(price) for price in prices if pd.notna(price)]

        if len(cleaned_prices) < 5:
            return "Insufficient data"

        # Prepare features
        recent_price = cleaned_prices[-1]
        avg_change = np.mean(np.diff(cleaned_prices))

        features = np.array([[recent_price, avg_change]])
        features_scaled = self.scaler.transform(features)

        # Use the trained model to predict
        probability = self.model.predict_proba(features_scaled)[0][1]
        return round(probability * 100)

    def create_price_plot(self, low_price, current_price, high_price):
    # Clean prices using the clean_price method
        low_price = self.clean_price(low_price)
        current_price = self.clean_price(current_price)
        high_price = self.clean_price(high_price)

        # Cap the current price within the range if it exceeds limits
        capped_price = min(max(current_price, low_price), high_price)

        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(6, 2))

        # Plot the low and high price bars with different colors
        ax.barh(0.5, high_price - low_price, left=low_price, color='#e0e0e0', edgecolor='black', linewidth=1, height=0.3, alpha=0.7, label='Price Range')
        
        # Add a rectangle for the low part (low price to current price)
        ax.barh(0.5, capped_price - low_price, left=low_price, color='#4caf50', edgecolor='black', linewidth=1, height=0.3, alpha=0.7, label='Low Price')
        
        # Add a rectangle for the high part (current price to high price)
        if capped_price < high_price:
            ax.barh(0.5, high_price - capped_price, left=capped_price, color='#f44336', edgecolor='black', linewidth=1, height=0.3, alpha=0.7, label='High Price')

        # Scatter the current price as a dot
        ax.scatter(capped_price, 0.5, color='#1565c0', s=200, zorder=2)  # Blue dot for current price

        # Add annotations
        ax.text(low_price, 0.6, f'Low ₹{low_price}', fontsize=12, verticalalignment='center')
        ax.text(high_price, 0.6, f'High ₹{high_price}', fontsize=12, verticalalignment='center', horizontalalignment='right')
        ax.text(capped_price, 0.4, f'Current Price: ₹{int(current_price)}', fontsize=12, verticalalignment='center', color='#1565c0', horizontalalignment='center')

        # Set the limits for a clean look
        ax.set_xlim(low_price - 10, high_price + 10)  # Add some padding to the limits
        ax.set_ylim(0, 1)  # Set y limits

        # Remove the axes for a clean look
        ax.set_axis_off()

        # Save the plot to a BytesIO object to send to the HTML page
        img = BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)  # Rewind the data
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')  # Convert to base64 string
        plt.close()  # Close the plot to free up memory
        return plot_url

