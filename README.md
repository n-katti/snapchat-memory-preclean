# snapchat-rename-memories
Takes an input of all snapchat memories that are named poorly (Month rather than MM; missing YYYY). Renames them based on their folder name and converts Month to MM. Adds padded numbering at the end for easy sorting when multiple memories are on the same day

## Usage:

1. Download your snapchat memories and merge them with their metadata using [Snapchat Memory Downloader](https://downloadmysnapchatmemories.com/)
2. Install python packages
```shell
python -m pip install -r requirements.txt
```
3. Drop folders of snapchat memories in the same root folder as the `rename_dates.py` script (they should be named by year)
4. Run `rename_dates.py`. This will rename all pictures to a more sortable format, create copies, and consolidate all pictures into a folder called `Output` 

## Notes: 
1. `April-14.jpg` that is in the 2020 folder will be renamed to `2020_04_14_00.jpg`. If there is another picture from that same day, it will be named `2020_04_14_01.jpg`

2. Any suffixes added to .mp4 files by the Snapchat Memory Downloader tool will be removed. `April-14-short.mp4` in the 2020 folder will be renamed to `2020_04_14_00.mp4`

3. If you delete memories, this script will also redo the numbering. In the 2020 folder if there is an `April-14.jpg`,  an `April-14-2.jpg` and a `April-14-3.jpg` (this is just how the Snapchat Memory Downloader tool numbers things) and you delete `April-14.jpg`, then `April-14-2.jpg` will be renamed and renumbered to `2020_04_14_00.jpg` and `April-14-3.jpg` will be renamed to `2020_04_14_01.jpg`
