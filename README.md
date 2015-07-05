# EKOiE

Set of tools used for *Extreme Opening & Ending Contest* (*Ekstremalny Konkurs
Openingów i Endingów*), one of my flagship events at conventions.

Goal of this application is to play songs with some random filters applied to
them, in order to increase the difficulty of properly guessing from which title
given song is.

## Installation

I used Python 3.4.3 on Ubuntu 15.04 while coding this. I advise using
`virtualenv`/`pyenv` in order to create fresh environment.

1. `sudo apt-get install ffmpeg` (required to open/save MP3 files)
1. `sudo apt-get install libncurses5-dev` (it might be necessary to recompile
   your Python if this wasn't installed before)
1. `sudo apt-get install portaudio19-dev` (required to play audio)
1. `pip install -r requirements.txt`

## Running

```py
python interface.py
```

## Keybindings

- `a` - play currently selected song
- `s` - stop song that's currently being played
- `f` - randomize the filters (they will be applied when you play the next
  song)
- `r` - reset the filters
- `Ctrl+q`, `Ctrl+c` - quit the application

## Settings screen

- *track length*: it's set to 35 seconds by default, and that's what I use
  during the contest.
- *already cut?* - I found out that loading whole song file on my netbook is
  tremendously slow (up to 10 seconds) - because of that, I decided to prepare
  files that are already cut to 70 seconds (2x35) and load these.

## Cutter

If your computer is as slow as mine, I created a helper utility to prepare your
songs and cut them to proper length. Just run:

```py
python cutter.py
```

# License

See [LICENSE.md](LICENSE.md).
