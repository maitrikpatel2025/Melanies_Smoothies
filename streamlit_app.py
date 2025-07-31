# Import required packages
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

# Query fruit options and convert to pandas for lookup
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)
df_df = my_dataframe.to_pandas()

# Prepare multiselect options
fruit_list = df_df['FRUIT_NAME'].tolist()

# Select ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# If fruits are selected
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)
    st.write(f"Your smoothie will contain: {ingredients_string}")

    # Show nutrition info for each selected fruit
    for fruit_chosen in ingredients_list:
        try:
            search_on = df_df.loc[
                df_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'
            ].iloc[0]

            st.subheader(f'{fruit_chosen} Nutrition Information')

            response = requests.get(
                f"https://fruityvice.com/api/fruit/{search_on.lower()}"
            )

            if response.status_code == 200:
                st.dataframe(data=response.json(), use_container_width=True)
            else:
                st.error(f"Could not retrieve nutrition info for {fruit_chosen}.")

        except Exception as e:
            st.error(f"Error retrieving data for {fruit_chosen}: {e}")

    # Submit order
    if st.button('Submit Order'):
        try:
            my_insert_stmt = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error(f"Failed to submit order: {e}")
