from pathlib import Path
from datetime import datetime
from tqdm import tqdm 
import os
import re 
import pandas as pd
import shutil
from PIL import Image
import piexif
import pytz

# Set location variables
location = Path(__file__)
location_parent = location.parent.parent / 'input'
os.chdir(location_parent)

class MediaEditor:
    def __init__(self, location_parent):
        self.location_parent = location_parent
        self.output_folder = location_parent.parent / 'output'

    def convert_date_format(self, input_date, pic_name, year):
        '''
        Function that takes in a string date of format Month-dd and converts it to MM_DD
        It seems to fail with February 29, so that will return an exception
        '''
        try:
            date_object = datetime.strptime(input_date, "%B-%d")

            # Format the date as mm_dd
            formatted_date = date_object.strftime("%m_%d")

            return formatted_date
        
        except Exception as e:
            print(f"Error converting date on {pic_name} in folder {year}. Error message")

    def custom_sort(self, value):
        '''
        Allows pandas sort function to work propely and sort alphanumeric fields ascending 
        '''
        parts = value.split('-')
        
        # Extract the non-numeric and numeric parts
        non_numeric = '_'.join(parts[:-1])
        numeric = int(parts[-1]) if parts[-1].isdigit() else 0
        
        return (non_numeric, numeric)

    def process_videos(self):
        '''
        Searches through all year folders, gets names of pictures, extracts the date and executes
        the date conversion function and creates a dataframe with the following columns:
        1) old name
        2) new name
        3) year
        '''
        # get a list of all files in the parent folder
        files = os.listdir(location_parent)

        pattern = r"^(January|February|March|April|May|June|July|August|September|October|November|December)-(\d{2})(.*)(\.jpg|\.mp4)"

        # filer this list for only folders and not actual files
        folders = [file for file in files if not os.path.isfile(location_parent / file)]

        pic_list = []

        for folder in folders:
            
            # Gets a list of all pictures in the folder
            pictures_names = os.listdir(location_parent / folder)

            # Loop through each picture. Extract the date. Create a new file name with the converted date 
            for pic in pictures_names:
                if pic.endswith('.mp4'):
                    match = re.match(pattern, pic)
                    if match:
                        original_date = f"{match.group(1)}-{match.group(2)}"
                        new_date = f"{folder}_{self.convert_date_format(original_date, pic, folder)}"
                        ending = match.group(4)
                        new_pic = f"{new_date}{ending}"
                        # print(new_pic)
                        
                        # Append the info into a list
                        all_info = []
                        all_info.append(pic)
                        all_info.append(new_pic)
                        all_info.append(folder)

                        # Append each picture's info into an overarching list of all pictures
                        pic_list.append(all_info)
                    else:
                        continue
        
        # Convert to a df
        return pd.DataFrame(pic_list, columns=['old', 'new', 'year'])

    def renumber_videos(self, df):
        '''
        Create a row number that will increment when there are multiple rows with the same new file name
        This will sort based on the old file name ascending 
        This method is being used as I deleted some pics when I cleaned up these memories
        So there are files tagged with _1 that are the only file from that day
        This will make sure that every date starts at 00 
        '''

        # Create a sort key column using custom sort function
        df['sort_key'] = df['old'].apply(self.custom_sort)

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

    def rename_and_output_videos(self, row):
        '''
        Renames and copies the files into an Output folder
        '''
        output_folder = location_parent.parent / 'output'
        try:
            os.makedirs(output_folder,  exist_ok=True)
            new_path = os.path.join(output_folder, row['new_path'])

            shutil.copy(row['old_path'], new_path)
            # print(f"Renamed {row['old']} to {row['new_path']}")
        except Exception as e:
            print(f"Error {e}")

    def convert_utc_to_est(self, utc_time_bytes):

        utc_time_str = utc_time_bytes.decode('utf-8')
        # Parse the UTC time string to a datetime object
        utc_time = datetime.strptime(utc_time_str, '%Y:%m:%d %H:%M:%S')

        # Create a timezone object for UTC
        utc_timezone = pytz.timezone('UTC')

        # Localize the UTC time to UTC timezone
        utc_time = utc_timezone.localize(utc_time)

        # Convert to Eastern Time (EST)
        est_timezone = pytz.timezone('US/Eastern')
        est_time = utc_time.astimezone(est_timezone)

        return est_time

    def process_exif(self, pic, folder, save=False, new_path = ''):
        try:
            image = Image.open(location_parent / folder / pic)
            exif_dict = piexif.load(image.info['exif'])
            original_utc_date = exif_dict['Exif'].get(piexif.ExifIFD.DateTimeOriginal)

            # Convert UTC to EST
            est_date = self.convert_utc_to_est(original_utc_date)
            # print(pic)
            # print(f"Original Date Taken (UTC): {original_utc_date}")
            # print(f"Converted Date Taken (EST): {est_date}")
            # # print(f'{pic} date is {exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]}')
            # print('---------------')
            exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = est_date.strftime('%Y:%m:%d %H:%M:%S')

            # Convert the edited Exif data back to bytes
            exif_bytes = piexif.dump(exif_dict)

            if save == True:
                image.save(new_path, exif=exif_bytes)
            return est_date, exif_bytes
        
        except (KeyError, FileNotFoundError) as e:
            print(f"Error reading Exif data: {e}")
            return None, None

    def process_pictures(self):
        files = os.listdir(location_parent)

        # filter this list for only folders and not actual files
        folders = [file for file in files if not os.path.isfile(location_parent / file)]

        pic_list = []

        for folder in folders:
            
            # Gets a list of all pictures in the folder
            pictures_names = os.listdir(location_parent / folder)

            # Loop through each picture. Extract the date. Create a new file name with the converted date 
            for pic in pictures_names:
                if pic.endswith('.jpg'):
                    pic_data = []
                    est_date, exif_bytes = self.process_exif(pic=pic, folder=folder)
                    pic_data.append(pic)
                    pic_data.append(est_date.strftime('%Y_%m_%d'))
                    pic_data.append(est_date)
                    pic_data.append(folder)
                    pic_list.append(pic_data)
                    # Save the image with the updated Exif data
                    # image.save(output_folder / pic, exif=exif_bytes)

        return pd.DataFrame(pic_list, columns=['old', 'new', 'timestamp', 'year']) 

    def renumber_pics(self, df):
        
        output_folder = location_parent.parent / 'output'
        os.makedirs(output_folder,  exist_ok=True)
        df['row_number'] = df.sort_values(['timestamp'], ascending=[True]).groupby('new').cumcount() + 1

        # Create a padded row number 
        df['adjusted_row_number'] = (df['row_number'] - 1).apply(lambda x: str(x).zfill(2))

        # Sort the df 
        df = df.sort_values(by=['new', 'row_number'], ascending=[True, True])

        # Create new paths
        df['old_path'] = df.apply(lambda row: os.path.join(location_parent, row['year'], row['old']), axis=1)
        df['new_path'] = df.apply(lambda row: os.path.join(output_folder, f'{row['new']}_{row['adjusted_row_number']}.jpg'), axis=1)

        df = df.drop(['adjusted_row_number', 'row_number'], axis=1)

        return df
    
    def rename_and_output_pics(self, df):
        for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing, Changing Metadata Time, and Renaming Pictures"):
            est_date, exif_bytes = self.process_exif(row['old'], row['year'], True, row['new_path'])
            


# # def main():

# #     df = process_videos()
# #     df = renumber_videos(df=df)

# #     tqdm.pandas(desc="Renaming Files", unit="row")
# #     df.progress_apply(lambda row: rename_and_output_videos(row), axis=1)

# # if __name__ == "__main__":
# #     main()

# edit = MediaEditor(location_parent=location_parent)

# df = edit.process_pictures()
# df = edit.renumber_pics(df)
# edit.rename_and_output_pics(df=df)
