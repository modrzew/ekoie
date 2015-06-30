# Play

```py
pydub.playback.play(track)
```

# Speed up

```py
track.speedup(playback_speed=2, chunk_size=80, crossfade=5)
```

# Reversed

```py
track.reverse()
```

# 8Hz (or random)

```py
track.set_frame_rate(8196)
```

# Volume changer

```py
slices = [track[i:i+250] for i in range(0, len(track), 250)]
first = slices[0]
for i, s in enumerate(slices[1:]):
    if i % 2 == 0:
        s -= 30
    first += s
```


