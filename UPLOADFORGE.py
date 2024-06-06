import streamlit as st
import pandas as pd
from datetime import datetime
import re
from io import BytesIO
import openpyxl 
from collections import Counter

st.title("UploadForge")
image_path = 'upload_forge_logo.webp'  # Adjust the path to your image file
st.image(image_path, caption='UploadForge', width=500)
st.divider()
current_year = datetime.now().year
season_section_options = [1, 2, 'None']
season_section = st.selectbox('Select Session Number:', season_section_options)
############## COURSE DICTIONARY ##############
course_name = {
"The Brain: Structure, Function and Evolution": "SOS_2017_SP1_LS507",
"Climate Change": "SOS_2017_SP1_ES504",
"SOS_2024_SP2_ES504" : "SOS_2017_SP1_ES504",
"The Diversity of Fishes": "SOS_2017_SP1_LS501",
"Earth: Inside and Out": "SOS_2017_SP1_ES501",
"Ecology: Ecosystem Dynamics and Conservation": "SOS_2022_SU2_LS508",
"Evolution": "SOS_2017_SP1_LS506",
"In the Field with Spiders": "SOS_2017_SP1_LS502",
"Genetics, Genomics, Genethics": "SOS_2017_SP1_LS503",
"Dinosaurs: Evolution, Extinction, and Paleobiology": "SOS_2017_SP1_LS505",
"Marine Biology": "SOS_2022_SU1_LS509",
"The Ocean System": "SOS_2017_SP1_ES502",
"Sharks and Rays": "SOS_2017_SP1_LS504",
"The Solar System": "SOS_2017_SP1_PS502",
"Space, Time and Motion": "SOS_2017_SP1_PS501",
"Water": "SOS_2017_SP1_ES503"
}

def replace_year(course_code):
    current_year = datetime.now().year
    return re.sub(r'\d{4}', str(current_year), course_code)

def update_season(course_code):
    month = datetime.now().month
    if 5 <= month <= 8:
        current_season = "SU"
    elif 9 <= month <= 12:
        current_season = "FA"
    elif 1 <= month <= 2:
        current_season = "W"
    elif 3 <= month <= 4:
        current_season = "SP"
    
    if season_section in [1, 2]:
        current_season += str(season_section)
    elif season_section == 'None':
        pass  # Do nothing, keep the current season without a section number

    # Replace the season and section in the course code
    course_code = re.sub(r'(SU|FA|W|SP)\d?', current_season, course_code)
    return course_code

course_df = pd.DataFrame.from_dict(course_name, orient='index', columns=['course_code'])
course_df.reset_index(inplace=True)
course_df.rename(columns={'index': 'course_name'}, inplace=True)
# Apply the updates to the DataFrame
course_df['course_code'] = course_df['course_code'].apply(replace_year).apply(update_season)

# Apply extensions to the course codes

course_dict = course_df.set_index('course_name')['course_code'].to_dict()

def main():
    uploaded_file = st.file_uploader('Upload Excel file', type=['xlsx'])
    if uploaded_file is not None:
        st.write('File uploaded successfully!')
        st.write('Processing...')
        
        final_final_csv = process_excel(uploaded_file)
        csv_as_bytes = final_final_csv.to_csv(index=False).encode()
        
        st.download_button(
            label="Download CSV",
            data=csv_as_bytes,
            file_name='final_data.csv',
            mime='text/csv'
        )

def counts_odd(series):
    counts_dict = dict()
    for item in series:
        counts_dict[item] = counts_dict.get(item, 0) + 1

    # Check for values with 30 or more occurrences
    keys_to_split = [key for key, value in counts_dict.items() if value >= 35]
    
    # Iterate over keys to split occurrences
    for key in keys_to_split:
        # Find the index to split the occurrences
        split_index = counts_dict[key] // 2
        # Add one extra to the first half if the total count is odd
        if counts_dict[key] % 2 != 0:
            split_index += 1
        # Assign the first half as {f}_1 and the second half as {f}_2
        for i, item in enumerate(series):
            if item == key:
                if split_index > 0:
                    series[i] = f"{key}_1"
                    split_index -= 1
                else:
                    series[i] = f"{key}_2"

    return series

def process_excel(file):
    # Convert the dictionary to a DataFrame
    new_file = pd.read_excel(file, usecols=['People::First Name', 'People::Last Name',
                                             'People::Email 1', 'Person ID', 'Courses::Name'])
    new_file = new_file.rename(columns={'People::First Name': 'firstname', 'People::Last Name': 'lastname',
                                        'People::Email 1': 'username', 'Person ID': 'profile_field_sospersonid',
                                        'Courses::Name': 'course2'})
    new_file['department'] = 'SOS_HOME'
    new_file['course1'] = 'SOS_HOME'
    new_file['role1'] = 'student'
    new_file['email'] = new_file['username']
    new_file['password'] = 'AMNH4dinos'
    final_csv = new_file.replace({"course2": course_dict})
    final_final_csv = final_csv[['firstname', 'lastname', 'password', 'username', 'email', 'department',
                                 'profile_field_sospersonid', 'course1', 'role1', 'course2']]
    column_series = final_final_csv['course2']
    final_final_csv['course2'] = counts_odd(column_series.tolist())
    return final_final_csv


if __name__ == '__main__':
    main()