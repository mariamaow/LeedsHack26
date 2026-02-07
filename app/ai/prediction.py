import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from datetime import timedelta
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

def create_dataset():

    # ------------------------------
    # Parameters
    # ------------------------------
    np.random.seed(42)
    num_days = 180  # 6 months of data
    start_date = pd.to_datetime('2025-09-01')

    # ------------------------------
    # Generate dates
    # ------------------------------
    dates = pd.date_range(start=start_date, periods=num_days)

    # ------------------------------
    # Initialize arrays
    # ------------------------------
    base_stock = 200
    stock = [base_stock]
    donations_received = []
    volunteers_available = []

    for date in dates:
        day_of_week = date.dayofweek  # 0 = Monday, 6 = Sunday
        
        # Daily consumption (10-30 units/day)
        daily_consumption = np.random.randint(10, 31)
        
        # Donations: higher on weekends
        if day_of_week >= 5:  # Saturday or Sunday
            donation = np.random.choice([0, np.random.randint(80, 201)], p=[0.4, 0.6])
        else:
            donation = np.random.choice([0, np.random.randint(50, 151)], p=[0.7, 0.3])
        donations_received.append(donation)
        
        # Volunteers: more on weekends
        if day_of_week >= 5:
            volunteers = np.random.randint(10, 25)
        else:
            volunteers = np.random.randint(5, 15)
        volunteers_available.append(volunteers)
        
        # Seasonal trend: slightly higher stock in fall (Sep-Nov)
        month = date.month
        seasonal_adjustment = 0
        if month in [9, 10, 11]:
            seasonal_adjustment = np.random.randint(0, 10)
        
        # Update stock
        new_stock = max(stock[-1] - daily_consumption + donation + seasonal_adjustment, 0)
        stock.append(new_stock)

    # Drop first dummy initial stock
    stock = stock[1:]

    # ------------------------------
    # Build DataFrame
    # ------------------------------
    data = pd.DataFrame({
        'date': dates,
        'stock_level': stock,
        'donations_received': donations_received,
        'volunteers_available': volunteers_available
    })

    # ------------------------------
    # Save to CSV
    # ------------------------------
    data.to_csv('food_bank_data.csv', index=False)
    print("food_bank_data.csv with realistic patterns generated successfully!")
    print(data.head(10))

def predict_stock():
    # ------------------------------
    # 1. Load your historical data
    # Example CSV structure:
    # date,stock_level,donations_received,volunteers_available
    # ------------------------------
    create_dataset()

    # ------------------------------
    # 1. Load data
    # ------------------------------
    data = pd.read_csv('food_bank_data.csv', parse_dates=['date'])

    # 2. Prepare features and target
    # We'll predict next day's stock
    data['next_stock'] = data['stock_level'].shift(-1)
    data = data.dropna()

    X = data[['stock_level', 'donations_received', 'volunteers_available']]  # features
    y = data['next_stock']  # target

    # 3. Split into train/test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 5. Make predictions
    y_pred = model.predict(X_test)



    # Get latest data
    latest = data.iloc[-1][['stock_level', 'donations_received', 'volunteers_available']].values

    # Use average historical donations and volunteers for future prediction
    avg_donations = data['donations_received'].mean()
    avg_volunteers = data['volunteers_available'].mean()

    predicted_stock = []

    current_stock = latest[0]
    for day in range(7):
        # Prepare input: [stock_level, donations, volunteers]
        X_future = np.array([[current_stock, avg_donations, avg_volunteers]])
        next_stock = model.predict(X_future)[0]
        predicted_stock.append(next_stock)
        current_stock = next_stock  # update stock for next day

    description = f"Predicted stock for the next 7 days:"
    for i, stock in enumerate(predicted_stock, 1):
        description += f"\nDay {i}: {stock:.0f}"

    # Optional: check if restock is needed
    restock_threshold = 5400
    restock_needed = False
    for i, stock in enumerate(predicted_stock, 1):
        if stock < restock_threshold:
            description += f"\n⚠️ Restock needed by day {i}!"
            restock_needed = True
    return restock_needed, description
        