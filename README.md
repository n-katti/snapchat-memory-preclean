# snapchat-rename-memories
Takes an input of all snapchat memories that are named poorly (Month rather than MM; missing YYYY). Renames them based on their folder name and converts Month to MM. Adds padded numbering at the end for easy sorting when multiple memories are on the same day

# Usage:

Install python packages
```shell
python -m pip install -r requirements.txt
```

## Use Case 1: Renaming All Photos Outputted from Snapchat Memory Downloader
1. Download your snapchat memories. Only select the json output option. Merge them with their metadata using [Snapchat Memory Downloader](https://downloadmysnapchatmemories.com/)
2. Drop folders of snapchat memories in the `snapchat-memory-precleaning/input` folder (the folders are named by year e.g. one folder for 2017, one for 2018, etc.)
3. This will rename all pictures to a more sortable format, create copies, and consolidate all pictures into a folder called `Output` 

### Notes: 
1. `April-14.jpg` that is in the 2020 folder will be renamed to `2020_04_14_00.jpg`. If there is another picture from that same day, it will be named `2020_04_14_01.jpg`

2. Any suffixes added to .mp4 files by the Snapchat Memory Downloader tool will be removed. `April-14-short.mp4` in the 2020 folder will be renamed to `2020_04_14_00.mp4`

3. If you delete memories, this script will also redo the numbering. In the 2020 folder if there is an `April-14.jpg`,  an `April-14-2.jpg` and a `April-14-3.jpg` (this is just how the Snapchat Memory Downloader tool numbers things) and you delete `April-14.jpg`, then `April-14-2.jpg` will be renamed and renumbered to `2020_04_14_00.jpg` and `April-14-3.jpg` will be renamed to `2020_04_14_01.jpg`

## Use Case 2: Clean Files Before Adding Captions
1. Download ALL of your snapchat memories and the JSON file. This use case will clean the files up before feeding into the snapchat-memory-overlay script, which adds overlays/captions to our pictures 

2. Place the memories in `/snapchat-rename-overlay/input/memories` and place the memories_history.json file in `/snapchat-memory-overlay/input`

3. Add the path to `/snapchat-memory-overlay/input` to line 13 in `main.py`

4. This part of the script will 1: rename the files by removing the date prefix so that the snapchat-memory-overlay script can read the file names (file name notation that Snapchat outputs for files has changed since the other script was written) and 2: will output a memories_history_new.json file that only contains the files which contain an overlay file. This is to make sure we're not processing any files that we don't need to and that we already have through Use Case 1. It also makes it easy to go through the pictures with captions later and decide if we want to keep the captioned photos or the uncaptioned photos from Use Case 1

5. Check the new `/snapchat-memory-overlay/input/memories_history_new.json` file and make sure it looks alright. Rename this to `memories_history.json` and put the original file elsewhere. Once this is done, you can run the snapchat-memory-overlay script to add captions to your memories
