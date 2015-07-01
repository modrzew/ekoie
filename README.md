# EKOiE

Set of tools used for *Extreme Opening & Ending Contest* (*Ekstremalny Konkurs
Openingów i Endingów*), one of my flagship events at conventions.

This is heavily WIP (work in progress), and probably not usable yet. My desire
is to manage these tools using single interface, and utilize that while running
the event.

## Installation

I used Python 3.4.3 on Ubuntu 15.04 while coding this. I advise using
`virtualenv`/`pyenv` in order to create fresh environment.

1. `sudo apt-get install ffmpeg` (required to open/save MP3 files)
1. `sudo apt-get install libncurses5-dev` (it might be necessary to recompile
   your Python if this wasn't installed before)
1. `sudo apt-get install portaudio19-dev` (required to play audio)
1. `pip install -r requirements.txt`
