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
    # Renames files downloaded directly from Snapchat to remove prefixed dates
    # rf.rename_without_date_prefix(input / 'memories')

    # For files downloaded through Snapchat Memory Downloader, this renames/renumbers the files
    df = rd.get_all_pics(location_parent=location_parent)
    df = rd.renumber_files(df=df, location_parent=location_parent)

    tqdm.pandas(desc="Renaming Files", unit="row")
    df.progress_apply(lambda row: rd.rename_files(row, location_parent=location_parent), axis=1)

    # eon.output_json_with_only_overlays(input=input)

if __name__ == "__main__":
    main()