import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, confusion_matrix
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import Binarizer

# Load the dataset
data = pd.read_csv('dataset.csv')

data = data.set_index('name').T

# Convert all columns to numeric, forcing errors to NaN
data = data.apply(pd.to_numeric, errors='coerce')

# Create a new DataFrame for the target variable (price drop)
price_drop_data = data.shift(-2) - data  # Price drop in 2 days

# Check for NaN values in price_drop_data
if price_drop_data.isnull().values.any():
    print("NaN values found in price drop data. Filling NaNs with 0.")
    price_drop_data = price_drop_data.fillna(0)  # Optionally fill NaNs with 0

# Create a binary target variable (1 if drop occurs, 0 otherwise)
binary_target = (price_drop_data < 0).astype(int)  # 1 if price drop, else 0

# Define features and targets
features = data.iloc[:-2]  # All data except last 2 days

# Select a specific column for regression target (e.g., the first column)
target_regression = price_drop_data.iloc[:-2, 0].squeeze()  # Select the first column and convert to 1D
target_classification = binary_target.iloc[:-2, 0].squeeze()  # Select the first column for classification

# Remove rows with NaN values
features = features.fillna(0)
target_regression = target_regression.fillna(0)
target_classification = target_classification.fillna(0)

# Split the data into training and testing sets
X_train, X_test, y_train_reg, y_test_reg, y_train_cls, y_test_cls = train_test_split(
    features, target_regression, target_classification, test_size=0.2, random_state=42
)

# Check the shapes to ensure they are 1D
print("Features Shape:", features.shape)  # Should be (n_samples, n_features)
print("Target Regression Shape:", target_regression.shape)  # Should be (n_samples,)
print("Target Classification Shape:", target_classification.shape)  # Should be (n_samples,)

# Function to evaluate regression models
def evaluate_regression_model(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    return rmse

# Compare Linear Regression
lr_model = LinearRegression()
lr_rmse = evaluate_regression_model(lr_model, X_train, X_test, y_train_reg, y_test_reg)
print(f'Linear Regression RMSE: {lr_rmse}')

# Compare Random Forest Regression
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_rmse = evaluate_regression_model(rf_model, X_train, X_test, y_train_reg, y_test_reg)
print(f'Random Forest Regression RMSE: {rf_rmse}')

# Function to evaluate classification models
def evaluate_classification_model(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    return accuracy, cm

# Compare Logistic Regression
log_model = LogisticRegression(max_iter=1000)
log_accuracy, log_cm = evaluate_classification_model(log_model, X_train, X_test, y_train_cls, y_test_cls)
print(f'Logistic Regression Accuracy: {log_accuracy}')
print(f'Logistic Regression Confusion Matrix:\n{log_cm}')
