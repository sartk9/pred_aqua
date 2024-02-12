import streamlit as st
import requests
import pandas as pd

st.title("Image Classification")
st.header("Upload Images for Classification")

# Input field for user to enter their name
create_by = st.text_input("Enter your name")

# Allow exactly five images to be uploaded
uploaded_files = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
if uploaded_files and len(uploaded_files) == 5:  # Ensure exactly five images are uploaded
    img_paths = [file.name for file in uploaded_files]  # Get image paths
    data = {"image_paths": img_paths, "create_by": create_by}  # Include create_by in the data
    if st.button("Submit"):
        response = requests.post("http://localhost:8000/classify", json=data)
        if response.status_code == 200:
            st.write(response.json())
        else:
            st.error(f"Error: {response.status_code} - {response.reason}")

        # Print the data received in the POST request
        st.write("Data received in POST request:")
        st.json(data)  # Display the JSON data

        if st.button("Fetch Table Data"):
            response = requests.get("http://localhost:8000/get_combined_data")
            if response.status_code == 200:
                data = response.json()["data"]
                df = pd.DataFrame(data["individual_data"])
                st.write(df)
            else:
                st.error(f"Error: {response.status_code} - {response.reason}")
else:
    st.warning("Please upload exactly five images.")

