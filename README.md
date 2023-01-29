# UltraStar Song Scrapper

This script will scrap the website usdb.animux.de and try to download all the needed files to use in the game Ultrastar, if for some reason any of the 4 resources (lyrics, video, audio and cover) are missing the script will try to get it from external sources, like google or youtube.

## MAKE SURE YOU RUN ALL THE BELOW COMMANDS AT THE REPO BASE DIRECTORY

## Setup

To setup make sure you are in a linux based environment that uses the `apt` package manager, if you fill the requirements just use the below command, if not, install the packages and dependencies contained in the file.

> bash setup.sh

## Basic usage

To `try` to download all the database (Good Luck) just run the following command.

> python3 scrape.py

If you want to download with more specificity, you can set the `Artist` or the `Artist` and `Song Name` (only the `Song Name` is not supported).
`MAKE SURE YOU WRITE THE ARTIST AND SONG NAME AS WELL AS YOU CAN`

> python3 scrape.py "Artist Name"

> python3 scrape.py "Artist Name" "Song Name"

## Finished

After you have finished downloading everything, all the directories will be inside `./songs`, just copy and paste all of them inside you UltraStar songs directory.
And it's done!

### Thanks for reading 👌