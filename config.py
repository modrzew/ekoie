MULTIPLE_FILTERS_CHANCES = (
    0.05,  # for 0 filters
    0.5,  # for 1 filter
    0.9,  # for 2 filters
    # above 0.9 - 3 filters
)

# Length options
SLICE_LENGTH = (250, 500, 750)
MULTIPLE_TRACKS_LENGTH = (2000, 4000)

# Filter options
SPEED_UP_RANGE = (1.5, 1.9)
SLOW_DOWN_RANGE = (0.3, 0.9)
FREQUENCY_RANGE = (4000, 20000)
TONE_DOWN_RANGE = (0.4, 0.9)
PANZER_VOLUME_DECREASE = 6
OVERLAY_VOLUME_DECREASE = 3

# What are the chances for loading multiple tracks?
LOAD_MULTIPLE_THRESHOLD = 0.25
LOAD_TRIPLE_THRESHOLD = 0.15  # *= LOAD_MULTIPLE_THRESHOLD

# How many points to award?
FILTER_POINTS = (2, 3, 5, 7)
TRACKS_MULTIPLIER = (1, 1, 2.4, 3.6)
