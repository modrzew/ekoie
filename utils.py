"""File utilities and helpers"""
import os
import os.path
import random


def get_filenames(directory):
    """Reads all mp3 files from given directory

    Returns dictionary with numbers from 1 as keys.
    """
    return {
        i: os.path.join(os.path.abspath(directory), filename)
        for i, filename in enumerate(os.listdir(directory), start=1)
    }


def shuffle(filenames):
    """Shuffles filenames and assigns them new keys"""
    values = list(filenames.values())
    random.shuffle(values)
    return {i: v for i, v in enumerate(values, start=1)}
