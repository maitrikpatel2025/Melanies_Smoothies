# Import required packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# App Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("my_example_connection", type="snowflake")
session = cnx.session()

# Pull fruit data including SEARCH_ON
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)
pd_df = my_dataframe.to_pandas()

# For debugging or inspection
# st.dataframe(pd_df)
# st.stop()

# Dropdown selection
fruit_list = pd_df['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# When ingredients are selected
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)
    st.write(f"Your smoothie will contain: {ingredients_string}")

    # For each selected fruit
    for fruit_chosen in ingredients_list:
        try:
            # Lookup search term from SEARCH_ON
            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

            # Nicely written lookup message
            st.markdown(f"🔎 The search value for **{fruit_chosen}** is **{search_on}**.")

            # Nutrition info header
            st.subheader(f"{fruit_chosen} Nutrition Information")

            # Call API
            response = requests.get(f"https://fruityvice.com/api/fruit/{search_on.lower()}")

            if response.status_code == 200:
                st.dataframe(response.json(), use_container_width=True)
            else:
                st.error(f"❌ Could not retrieve nutrition info for {fruit_chosen}.")

        except Exception as e:
            st.error(f"⚠️ Error retrieving data for {fruit_chosen}: {e}")

    # Submit to orders table
    if st.button('Submit Order'):
        try:
            insert_stmt = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            session.sql(insert_stmt).collect()
            st.success(f'✅ Your Smoothie is ordered, {name_on_order}!')
        except Exception as e:
            st.error(f"❌ Failed to submit order: {e}")
