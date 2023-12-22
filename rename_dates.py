from pathlib import Path
from datetime import datetime
from tqdm import tqdm 
import os
import re 
import pandas as pd
import shutil

# Set location variables
location = Path(__file__)
location_parent = location.parent
os.chdir(location_parent)


def convert_date_format(input_date, pic_name, year):
    # Parse the input date string
    try:
        date_object = datetime.strptime(input_date, "%B-%d")

        # Format the date as mm_dd
        formatted_date = date_object.strftime("%m_%d")

        return formatted_date
    
    except Exception as e:
        print(f"Error converting date on {pic_name} in folder {year}. Error message")

def get_all_pics():
    # get a list of all files in the parent folder
    files = os.listdir(location_parent)

    pattern = r"^(January|February|March|April|May|June|July|August|September|October|November|December)-(\d{2})(.*)(\.jpg|\.mp4)"

    # filer this list for only folders and not actual files
    folders = [file for file in files if not os.path.isfile(location_parent / file)]

    pic_list = []

    for folder in folders:

        pictures_names = os.listdir(location_parent / folder)

        for pic in pictures_names:
            match = re.match(pattern, pic)
            if match:
                original_date = f"{match.group(1)}-{match.group(2)}"
                new_date = f"{folder}_{convert_date_format(original_date, pic, folder)}"
                # ending = str.replace(match.group(3), '-short', '')
                # ending = str.replace(ending, '-', '_')
                ending = match.group(4)
                new_pic = f"{new_date}{ending}"
                # print(new_pic)
                
                all_info = []
                all_info.append(pic)
                all_info.append(new_pic)
                all_info.append(folder)
                pic_list.append(all_info)
            else:
                continue
        
    return pd.DataFrame(pic_list, columns=['old', 'new', 'year'])

def custom_sort(value):
    '''
    Allows pandas sort function to work propely and sort alphanumeric fields ascending 
    '''
    parts = value.split('-')
    
    # Extract the non-numeric and numeric parts
    non_numeric = '_'.join(parts[:-1])
    numeric = int(parts[-1]) if parts[-1].isdigit() else 0
    
    return (non_numeric, numeric)

def create_path(value):
    '''
    Generates a string path
    '''

    return os.path.join(location_parent, value['year'], )

def renumber_files(df):

    # Create a sort key column using custom sort function
    df['sort_key'] = df['old'].apply(custom_sort)

    # Create a row number that will increment when there are multiple rows with the same new file name
    # This will sort based on the old file name ascending 
    # This method is being used as I deleted some pics when I cleaned up these memories
    # So there are files tagged with _1 that are the only file from that day
    # This will make sure that every date starts at 00 
    df['row_number'] = df.sort_values(['new', 'sort_key'], ascending=[True, True]).groupby('new').cumcount() + 1

    # Create a padded row number 
    df['adjusted_row_number'] = (df['row_number'] - 1).apply(lambda x: str(x).zfill(2))

    # Sort the df 
    df = df.sort_values(by=['new', 'row_number'], ascending=[True, True])

    # Create new paths
    df['old_path'] = df.apply(lambda row: os.path.join(location_parent, row['year'], row['old']), axis=1)
    df['new_path'] = df.apply(lambda row: f"{row['new'].split('.')[0]}_{row['adjusted_row_number']}.{row['new'].split('.')[1]}", axis=1)
    
    df = df.drop(['sort_key', 'adjusted_row_number', 'row_number'], axis=1)
    #Uncomment the below if you want to test that the row number is working properly 
    #filtered_df = df[df.groupby('new')['row_number'].transform('max') > 1].sort_values(by=['new', 'row_number'], ascending=[True, True])

    return df

def rename_files(row):
    output_folder = location_parent / 'Output'
    try:
        os.makedirs(output_folder,  exist_ok=True)
        new_path = os.path.join(output_folder, row['new_path'])

        shutil.copy(row['old_path'], new_path)
        # print(f"Renamed {row['old']} to {row['new_path']}")
    except Exception as e:
        print(f"Error {e}")


df = get_all_pics()
df = renumber_files(df=df)

tqdm.pandas(desc="Renaming Files", unit="row")
df.progress_apply(lambda row: rename_files(row), axis=1)
        


