import pandas as pd 
import numpy as np

from helpers import *

# file support
import os
from os import listdir, path
from os.path import isfile, join, basename, splitext
from time import time

# audio manipulation
import sounddevice as sd
import soundfile as sf
import scipy.io.wavfile as wav
import math

from pydub import AudioSegment
from pydub.utils import make_chunks

# experiencing 'file not found error' with pydub's AudioSegment...
# install either of the following libraries
# libav using 'apt-get install libav-tools libavcodec-extra'
# ffmpeg using 'apt-get install ffmpeg libavcodec-extra'
from pydub import AudioSegment


# silence threshold in dB
def remove_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    trim_ms = 0 # in milliseconds
    assert chunk_size > 0 # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size
    return trim_ms

def record_file(item, write_directory, fs=44100):
    print('creating replay of', item)

    # determine recording duration
    audio = AudioSegment.from_file(item, format='wav')
    input_duration = audio.duration_seconds

    # generate output path
    loc = write_directory + path_leaf(item)

    # load audio file as array
    data, _ = sf.read(item, dtype='float64')

    # record audio file
    recording = sd.rec(int(math.ceil(input_duration * fs)), samplerate=fs, channels=2)
    sd.wait()
    
    # play audio file
    sd.play(data, fs, blocking=True)

    # write first-draft recording
    wav.write(loc, fs, recording)

    return loc

def listen(seconds, directory, prefix = '', fs=44100, overwrite=True):
    print("* recording...")
    recording = sd.rec(int(seconds * fs), channels=1)
    sd.wait()

    loc = ""
    if overwrite:
        loc = directory + "test.wav"
    else:
        loc = directory + prefix + str(int(time())) + ".wav"
    wav.write(loc, fs, recording)

    return loc

def make_clips(sample, directory, name, length = 5000, fs = 44100):
    myaudio = AudioSegment.from_file(sample, "wav")
    myaudio = myaudio.set_frame_rate(fs)
    chunk_length_ms = 5000
    chunks = make_chunks(myaudio, chunk_length_ms)
    for i, chunk in enumerate(chunks):
        chunk_name = name + "{0}.wav".format(i)
        print("\t* exporting...", chunk_name)
        chunk.export(directory + name + chunk_name, format="wav")

    print("* writing clips")
    clips = get_files('experiment/directory/' + name + '/', ['.wav'])

    return clips

def playback(sample, write_directory=''):
    print("* starting playback...")

    loc = write_directory + path_leaf(sample)
    data, samplerate = sf.read(sample)

    recording = sd.playrec(data, samplerate, channels=2)
    sd.wait()

    print("* saving playback recording to " + loc + " ...")
    wav.write(loc, samplerate, recording)
    return loc

def record_directory(items, write_directory, fs = 44100):
    # devices = sd.query_devices()
    # for device in devices:
    #    try:
    #        set output device
    #        sd.default.device = device
    #        print(device)
        
    # simultaneous playback and recording
    for item in items:
        
        # generate output path
        loc = write_directory + path_leaf(item)

        if (path.exists(loc) == False):

            print('creating replay of', item)

            # determine recording duration
            # audio = AudioSegment.from_file(item, format='wav')
            # input_duration = audio.duration_seconds

            # load audio file as array
            data, samplerate = sf.read(item)
            print(item, samplerate)
            # time.sleep(3.0)
            # simultaneous playback and recording
            
            recording = sd.playrec(data, samplerate, channels=2)
            sd.wait()
            
            # record audio file
            # recording = sd.rec(int(math.ceil(input_duration * fs)), samplerate=fs, channels=2)
            # sd.wait()
            
            # play audio file
            # sd.play(data, fs, blocking=True)

            # write first-draft recording
            # print(type(recording))
            wav.write(loc, samplerate, recording)
        else:
            print(loc + ' already exists. Skipping replay...')
            # load first-draft recording
            # sound = AudioSegment.from_file(loc, format='wav')
            # sound, fs = sf.read(loc, dtype='float64')  

            # TRIM - (optional) - currently assuming the duration of the input audio is sufficient for its recording
            # trim start and end silence
            # start_trim = remove_leading_silence(sound)
            # end_trim = remove_leading_silence(sound.reverse())

            # output_duration = sound.duration_seconds
            # trimmed_sound = sound[start_trim:output_duration-end_trim]

            # overwrite first-draft recording
            # sound.export(loc, format='wav')
            # scaled = np.int16(sound/np.max(np.abs(sound)) * 32767)
            # wav.write(loc, fs, scaled)

        #     except Exception as ex:
        #        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        #        message = template.format(type(ex).__name__, ex.args)
        #        print(message)


# USAGE
# audio_samples = get_files('notebooks/chime/clips-5s/', ['.wav']) # samples to play and record
# record_directory(audio_samples, "notebooks/chime/recordings/")
#listen(5, 44100, 'recordings/', overwrite=False)