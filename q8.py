import pandas as pd
import os
from groq import Groq

# Set the Groq API key (replace 'your_api_key_here' with your actual API key)
os.environ['GROQ_API_KEY'] = 'ENTER_YOUR_API_KEY_HERE'

# Load the CSV file
csv_path = r"D:\Engineer ABDUL QAVI\OutFitRecommender\zara.csv"
inventory = pd.read_csv(csv_path, sep=';')

# Function to filter and select products based on user preferences
def get_matching_clothes(user_preferences, inventory):
    # Filter the inventory based on category, seasonality, and any other preferences
    filtered_inventory = inventory[
        (inventory['Product Category'].str.lower() == user_preferences['category'].lower()) &
        (inventory['Seasonal'].str.lower() == user_preferences['seasonal'].lower()) &
        (inventory['Promotion'].str.lower() == user_preferences.get('promotion', 'Yes').lower()) &
        (inventory['section'].str.lower() == user_preferences['section'].lower())
    ]
   
    return filtered_inventory

# Example user preferences (this would be derived from the user's input via LLM)
user_preferences = {
    'category': 'Clothing',
    'seasonal': 'Yes',
    'section': 'WOMAN',
    'promotion': 'Yes'
}

# Fetch matching clothes
matching_clothes = get_matching_clothes(user_preferences, inventory)

# Check if we have matching clothes
if matching_clothes.empty:
    print("No matching clothes found. Please adjust your preferences.")
else:
    print(f"Found {len(matching_clothes)} matching items.")
    
    try:
        # Connect with Groq and make the completion request
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        
        # Prepare the inventory information (limit to 2 items for brevity)
        inventory_info = matching_clothes.head(2).apply(
            lambda row: f"- {row['name']}: {row['Product Category']} - {row['description']} "
                        f"(Brand: {row['brand']}, Price: {row['price']} {row['currency']})",
            axis=1
        ).str.cat(sep="\n")
        
        # Prepare the request to Groq
        completion = client.chat.completions.create(
            model="llama3-groq-70b-8192-tool-use-preview",
            messages=[
                {
                    "role": "user",
                    "content": "I am looking for a summer casual outfit for a beach party. Could you recommend something from my store's inventory?"
                },
                {
                    "role": "assistant",
                    "content": f"Based on your inventory, here are some outfit recommendations for a summer beach party:\n{inventory_info}"
                }
            ]
        )

        # Debugging: Check what is actually being returned from Groq
        print("API Response:", completion)

        # Safely extract the response content
        for chunk in completion:
            if hasattr(chunk, 'choices') and hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                print(chunk.choices[0].delta.content or "", end="")
            else:
                print("Unexpected response format from Groq API")

    except Exception as e:
        print(f"An error occurred while communicating with the Groq API: {str(e)}")
        print("\nHere are the first two matching items from your inventory:")
        print(matching_clothes[['name', 'Product Category', 'description', 'brand', 'price', 'currency']].head(2).to_string(index=False))

