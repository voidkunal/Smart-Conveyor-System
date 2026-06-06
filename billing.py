import pandas as pd

def calculate_current_bill(detected_products):
    """Calculates the total price of all items currently visible on the belt."""
    if not detected_products:
        return 0.0
    return sum(item['price'] for item in detected_products)

def format_receipt_dataframe(detected_products):
    """Converts the list of dictionaries into a Pandas DataFrame for the Streamlit UI."""
    if not detected_products:
        
        return pd.DataFrame(columns=["Product Name", "Price (₹)"])
    
    df = pd.DataFrame(detected_products)
   
    df.columns = ["Product Name", "Price (₹)"]
    return df