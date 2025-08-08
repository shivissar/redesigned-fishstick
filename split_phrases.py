
import pandas as pd
import os

# Load the csv file
df = pd.read_csv("/Users/shiv/new-project/tamil_buddy_streamlit_project_v2/data/decks/phrases.csv", header=None)
df.columns = ["id", "category", "tamil", "translit", "english", "difficulty"]

# Get unique categories
categories = df["category"].unique()

# Create a new csv file for each category
for category in categories:
    # Filter the dataframe by category
    category_df = df[df["category"] == category].copy()
    
    # Reset the index and drop the old index
    category_df.reset_index(drop=True, inplace=True)
    
    # Create a new id column starting from 1
    category_df["id"] = category_df.index + 1
    
    # Drop the difficulty column
    category_df.drop(columns=["difficulty"], inplace=True)
    
    # Save the new dataframe to a csv file
    category_df.to_csv(f"/Users/shiv/new-project/tamil_buddy_streamlit_project_v2/data/decks/{category}.csv", index=False)

# Delete the original file
os.remove("/Users/shiv/new-project/tamil_buddy_streamlit_project_v2/data/decks/phrases.csv")
