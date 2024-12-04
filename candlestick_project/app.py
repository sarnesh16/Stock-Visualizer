import os
import yfinance as yf
import mplfinance as mpl
import pandas as pd
from flask import Flask, request, render_template, send_from_directory

#Initializes the Flask application
#where __name__ refers to the current module. This is necessary for Flask to identify the app and manage routing
app = Flask(__name__)

# Directory to save charts
CHARTS_DIR = 'static/charts'
os.makedirs(CHARTS_DIR, exist_ok=True)

#@app.route('/', methods=['GET', 'POST']): This creates the main route of the application (/). It can handle both GET (for initially loading the page) and POST (for when the form is submitted).
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form['ticker']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        try:
            # Fetch stock data
            stock_data = yf.download(ticker, start=start_date, end=end_date, group_by='ticker')
            
            # Check if data is empty
            if stock_data.empty:
                raise ValueError("No data found for the given ticker or date range.")
            
            # Debugging step: Print data structure
            print(stock_data.head())  # Check the first few rows
            print(stock_data.columns)  # Inspect the column names
            
            # Flatten MultiIndex columns and keep only the second level
            stock_data.columns = stock_data.columns.droplevel(0)
            
            # Rename columns for mplfinance compatibility
            stock_data.rename(columns={
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Close': 'Close',
                'Volume': 'Volume'
            }, inplace=True)
            
            # Ensure required columns exist
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in stock_data.columns for col in required_columns):
                raise ValueError("Required columns (Open, High, Low, Close, Volume) are missing or incorrectly named.")
            
            # Drop rows with missing values
            stock_data.dropna(inplace=True)

            # Generate candlestick chart
            chart_path = os.path.join(CHARTS_DIR, f'{ticker}_chart.png')
            mpl.plot(
                stock_data,
                type='candle',
                volume=True,
                style='yahoo',
                title=f'{ticker.upper()} Candlestick Chart',
                figratio=(16, 9),
                mav=(10, 50),
                savefig=dict(fname=chart_path, dpi=100, bbox_inches="tight")
            )
            
            return render_template('index.html', chart_path=chart_path, ticker=ticker.upper())
        
        except Exception as e:
            return render_template('index.html', error=str(e))
    
    return render_template('index.html')

@app.route('/charts/<filename>')
def serve_chart(filename):
    return send_from_directory(CHARTS_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
