import math
import matplotlib.pyplot as plt
import mido
import numpy as np

import note_seq
import librosa

from config import Consts
import eventCodec

# note_on   音符开始
# note_off  音符终止
# note      音符音高
# velocity  音量 0-127
# time      一拍480tick
# tempo     乐曲速度

def cal_tempo_to_bpm(tempo):
    return 60000000 / tempo

def cal_bpm_to_tempo(bpm):
    return 60000000 / bpm

def time_to_mido_time(t):
    return 480 * t

def mido_time_to_time(mido_t):
    return mido_t / 480

def read_MIDI(absolute_path):
    midi_file = mido.MidiFile(absolute_path)
    midi = []
    for index, track in enumerate(midi_file.tracks):
        print(index, track.name)
        for _, message in enumerate(track):
            # print(i, message)
            if message.is_meta:
                print(message)
            if Consts.SYSEX is message.type:
                print(Consts.SYSEX, message)
            # if NOTE_ON is message["type"]:
            #     pass
            # if NOTE_OFF is message["type"]:
            #     pass
    return midi

def splite_MIDI_into_pieces():
    pass


if "__main__" == __name__:
    pass
