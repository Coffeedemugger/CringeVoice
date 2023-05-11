import numpy as np
from matplotlib import pyplot as plt
import pyaudio

RECORD_TIME = 5
RATE = 44100
CHUNK = 1024

p = pyaudio.PyAudio()
player = p.open(format=pyaudio.paInt16, channels=2, rate=RATE, output=True, 
frames_per_buffer=CHUNK)
stream = p.open(format=pyaudio.paInt16, channels=2, rate=RATE, input=True, frames_per_buffer=CHUNK)

#tuneFreq=20
#t=np.arange(0,RECORD_TIME*5,RATE**(-1))
#total = np.zeros((0,))
#detuner = np.exp(-1j*2*np.pi*tuneFreq*t)

audiolast=np.zeros((CHUNK*2))
wet = 0.8

for i in range(int(RECORD_TIME*2*(RATE/CHUNK))): #do this for 10 seconds
    audio = np.frombuffer(stream.read(CHUNK),dtype=np.int16)#*detuner[i*CHUNK:(i+2)*CHUNK]
    output = np.int16(wet*(np.int16(audio/1000)*1000)+(1-wet)*audio)
    player.write(output,CHUNK)
    audiolast=audio

stream.stop_stream()
stream.close()
p.terminate()