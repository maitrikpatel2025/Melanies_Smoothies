# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# App Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Establish connection to Snowflake

import streamlit as st

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

import requests
smoothiefroot_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
st.text(smoothiefroot_response)

# If selected, display and insert
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)
    st.write(f"Your smoothie will contain: {ingredients_string}")

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')"""

    if ingredients_list:
        ingredients_string = ''
        st.subheader(fruit_chosen + 'Nutrition Information' )
        for fruit_chosen in ingredients_list:
            ingredients_string += fruit_chosen + ' '
            smoothiefroot_response = requests.get("https://fruityvice.com/api/fruit"+ fruit_chosen)
            sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
