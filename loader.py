import math
import multiprocessing
import os
import os.path
import threading
import time

import pydub

import audio


class Worker(threading.Thread):
    def __init__(self, worker_number, filenames):
        super(Worker, self).__init__()
        self._worker_number = worker_number
        self._filenames = filenames
        self.tracks = []
        self.running = False

    def run(self):
        self.running = True
        for i, filename in enumerate(self._filenames):
            track = pydub.AudioSegment.from_mp3(filename)
            self.tracks.append(audio.cut(track, length=70000))
            print('Worker %s, file %s done' % (self._worker_number, i))
        self.running = False


directory = '/home/modrzew/OneDrive/Muzyka/Chińskie bajki'
filenames = [
    os.path.abspath(os.path.join(directory, filename))
    for filename in os.listdir(directory)
    if filename.endswith('.mp3')
]
filenames *= 4
files_count = len(filenames)
cpu_count = multiprocessing.cpu_count() - 1
per_worker = math.ceil(files_count / cpu_count)
workers = []
for i in range(cpu_count):
    chunk = filenames[i*per_worker:(i+1)*per_worker]
    worker = Worker(i+1, chunk)
    workers.append(worker)
    worker.start()
while any(w.running for w in workers):
    time.sleep(1)
tracks = []
for worker in workers:
    tracks += worker.tracks
