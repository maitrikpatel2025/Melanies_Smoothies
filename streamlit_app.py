# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Establish connection to Snowflake
cnx = st.connection("my_example_connection", type="snowflake")
session = cnx.session()

# Query fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Select ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# If selected, display and insert
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)
    st.write(f"Your smoothie will contain: {ingredients_string}")

    # Show nutrition info per fruit
    for fruit_chosen in ingredients_list:
        st.subheader(f'{fruit_chosen} Nutrition Information')
        try:
            response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen.lower()}")
            if response.status_code == 200:
                st.dataframe(data=response.json(), use_container_width=True)
            else:
                st.error(f"Could not retrieve nutrition info for {fruit_chosen}.")
        except Exception as e:
            st.error(f"Error retrieving data: {e}")

    # Insert into orders table
    if st.button('Submit Order'):
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')"""
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
