import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

fruit_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
    .to_pandas()
)

st.dataframe(fruit_df, use_container_width=True)

fruit_names = fruit_df["FRUIT_NAME"].tolist()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_names,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        search_on = fruit_df.loc[
            fruit_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"
        ].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        if smoothiefroot_response.status_code == 200:
            sf_df = pd.json_normalize(smoothiefroot_response.json())
            st.dataframe(sf_df, use_container_width=True)
        else:
            st.error(f"Could not load data for {fruit_chosen}")

    my_insert_stmt = f"""
        insert into SMOOTHIES.PUBLIC.ORDERS (ingredients, name_on_order)
        values ('{ingredients_string.strip()}', '{name_on_order}')
    """

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")



