import pandas as pd
import streamlit as st

# Load the data from Excel files
inflation_data = pd.read_excel('Inflation_event_stock_analysis_resultsOct.xlsx')
income_data = pd.read_excel('Inflation_IncomeStatement_correlation_results.xlsx')
interest_rate_data = pd.read_excel('interestrate_event_stock_analysis_resultsOct.xlsx')
interest_rate_income_data = pd.read_excel('interestrate_IncomeStatement_correlation_results.xlsx')

# Set up Streamlit app
st.title('Stock Analysis Based on Economic Events')

# Create a sidebar for user input
st.sidebar.header('Search for a Stock')
event_type = st.sidebar.selectbox('Select Event Type:', ['Inflation', 'Interest Rate'])
stock_name = st.sidebar.text_input('Enter Stock Symbol:', '')

# User input for expected upcoming rate
expected_rate = st.sidebar.number_input('Enter Expected Upcoming Rate (%):', value=3.65, step=0.01)

# User chooses calculation method
calc_method = st.sidebar.selectbox('Select Calculation Method:', ['Simple', 'Dynamic'])

# Function to fetch details for a specific stock based on the event type
def get_stock_details(stock_symbol, event_type):
    if event_type == 'Inflation':
        event_row = inflation_data[inflation_data['Symbol'] == stock_symbol]
        income_row = income_data[income_data['Stock Name'] == stock_symbol]
    else:  # Interest Rate
        event_row = interest_rate_data[interest_rate_data['Symbol'] == stock_symbol]
        income_row = interest_rate_income_data[interest_rate_income_data['Stock Name'] == stock_symbol]

    if not event_row.empty and not income_row.empty:
        event_details = event_row.iloc[0]
        income_details = income_row.iloc[0]

        st.subheader(f'Details for {stock_symbol}')
        
        # Display event data
        st.write(f"### {event_type} Event Data")
        st.write(event_row)

        # Display income statement data
        st.write("### Income Statement Data")
        st.write(income_row)

        # Generate projections based on expected rate
        projections = generate_projections(event_details, income_details, expected_rate, event_type, calc_method)
        
        # Display projections
        st.write(f"### Projected Changes Based on Expected {event_type}")
        st.dataframe(projections)

        # Additional interpretations
        if event_type == 'Inflation':
            interpret_inflation_data(event_details)
        else:
            interpret_interest_rate_data(event_details)
        interpret_income_data(income_details)
    else:
        st.warning('Stock symbol not found in the data. Please check the symbol and try again.')

# Function to generate projections based on expected rate
def generate_projections(event_details, income_details, expected_rate, event_type, method):
    projections = pd.DataFrame(columns=['Parameter', 'Current Value', 'Projected Value', 'Change'])
    
    # Check if 'Latest Close Price' exists
    if 'Latest Close Price' in event_details.index:
        latest_close_price = pd.to_numeric(event_details['Latest Close Price'], errors='coerce')
        
        if method == 'Dynamic':
            rate_change = expected_rate - pd.to_numeric(income_details['Latest Event Value'], errors='coerce')
            price_change = event_details['Event Coefficient'] * rate_change
        else:  # Simple calculation
            price_change = latest_close_price * (expected_rate / 100)

        projected_price = latest_close_price + price_change
        
        new_row = pd.DataFrame([{
            'Parameter': 'Projected Stock Price',
            'Current Value': latest_close_price,
            'Projected Value': projected_price,
            'Change': price_change
        }])
        projections = pd.concat([projections, new_row], ignore_index=True)

    # Project changes in new income statement items
    for column in income_details.index:
        if column != 'Stock Name':
            current_value = pd.to_numeric(income_details[column], errors='coerce')
            if pd.notna(current_value):  # Check if the conversion was successful
                if method == 'Dynamic':
                    correlation_factor = event_details[column] if column in event_details.index else 0
                    projected_value = current_value + (current_value * correlation_factor * (expected_rate / 100))
                else:  # Simple calculation
                    projected_value = current_value * (1 + (expected_rate / 100))
                
                change = projected_value - current_value

                new_row = pd.DataFrame([{
                    'Parameter': column,
                    'Current Value': current_value,
                    'Projected Value': projected_value,
                    'Change': change
                }])
                projections = pd.concat([projections, new_row], ignore_index=True)

    return projections

# Check if user has entered a stock symbol and selected an event
if stock_name and event_type:
    get_stock_details(stock_name, event_type)
