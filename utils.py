"""File utilities and helpers"""
import os
import os.path
import random


def get_filenames(directory):
    """Reads all mp3 files from given directory

    Returns dictionary with numbers from 1 as keys.
    """
    results = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if not filename.endswith('mp3'):
                continue
            results.append(os.path.join(dirpath, filename))
    return {i: path for i, path in enumerate(results, start=1)}


def shuffle(filenames):
    """Shuffles filenames and assigns them new keys"""
    values = list(filenames.values())
    random.shuffle(values)
    return {i: v for i, v in enumerate(values, start=1)}
