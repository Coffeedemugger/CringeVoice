import numpy as np
from scipy.interpolate import interp1d as interp
from matplotlib import pyplot as plt
import pyaudio

RECORD_TIME = 60
RATE = 44100
CHUNK = 4096

p = pyaudio.PyAudio()
player = p.open(format=pyaudio.paInt16, channels=2, rate=RATE, output=True, 
frames_per_buffer=CHUNK)
stream = p.open(format=pyaudio.paInt16, channels=2, rate=RATE, input=True, frames_per_buffer=CHUNK)
wet = 0.5

oldoutput = np.zeros(CHUNK*2)

for i in range(int(RECORD_TIME*2*(RATE/CHUNK))): #do this for 10 seconds
    output=np.zeros(0)
    audio = np.frombuffer(stream.read(CHUNK),dtype=np.int16)
    audinterp = interp(np.arange(audio.shape[0]),audio)
    output = np.int16(audinterp(np.linspace(0,audio.shape[0]-1,int(audio.shape[0]*1.2))))
    for index in np.arange((int(output.shape[0]-audio.shape[0]))):
        wet = index/(output.shape[0]-audio.shape[0])
        output[index] = np.int16((1-wet)*oldoutput[::-1][index]+wet*output[index])
    player.write(output,CHUNK)
    oldoutput = output 

stream.stop_stream()
stream.close()
p.terminate()