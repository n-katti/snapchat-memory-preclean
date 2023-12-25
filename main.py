from functions import rename_dates as rd
from functions import rename_files as rf
from functions import extract_overlay_names as eon
from tqdm import tqdm
from pathlib import Path
import os

# Sets one location for the parent folder of the current script where photos from Snapchat Memory Downloader are placed in yearly folders
location = Path(__file__)
location_parent = location.parent / 'input'

# Set another path for the memories that were downloaded separately (as part of the caption overlay)
input = Path(r'C:\Users\nikhi\OneDrive\Documents\Python Projects\snapchat-memory-overlay\input')

def main():
    #####
    # USE CASE 1
    #####
    # Renames files downloaded directly from Snapchat to remove prefixed dates
    # rf.rename_without_date_prefix(input / 'memories')

    # Then gets a list of pics with overlays
    # eon.output_json_with_only_overlays(input=input)

    #####
    # USE CASE 2
    #####
    # For files downloaded through Snapchat Memory Downloader, this renames/renumbers the files
    edit_media = rd.MediaEditor(location_parent=location_parent)
    vids = edit_media.process_videos()
    vids = edit_media.renumber_videos(df=vids)

    pics = edit_media.process_pictures()
    pics = edit_media.renumber_pics(df=pics)
    edit_media.rename_and_output_pics(df=pics)

    tqdm.pandas(desc="Processing and Renaming Videos", unit="row")
    print('-----------------------')
    vids.progress_apply(lambda row: edit_media.rename_and_output_videos(row), axis=1)


if __name__ == "__main__":
    main()