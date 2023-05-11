import numpy as np
from scipy.interpolate import interp1d as interp
import pyaudio

RECORD_TIME = 60
RATE = 44100
CHUNK = 4096

p = pyaudio.PyAudio()
player = p.open(format=pyaudio.paInt16, channels=2, rate=RATE, output=True, 
frames_per_buffer=CHUNK)
stream = p.open(format=pyaudio.paInt16, channels=2, rate=RATE, input=True, frames_per_buffer=CHUNK)

#tuneFreq=20
#t=np.arange(0,RECORD_TIME*5,RATE**(-1))
#total = np.zeros((0,))
#detuner = np.exp(-1j*2*np.pi*tuneFreq*t)

def mixwetdry(original:np.ndarray,effected:np.ndarray,wet:np.float32) -> np.ndarray:
    if wet > 1 or wet < 0:
        raise Exception("Wet/Dry ratio must be within [0,1].")
    return np.int16(wet*effected+(1-wet)*(original))

def bitcrush(audio,factor, wet):
    effected = np.int16(audio/factor)*factor
    return mixwetdry(audio,effected,wet)

def delayline(audio,audiolast,wet) -> np.ndarray:
    return mixwetdry(audio,audiolast,wet)

def pitchdown(audio,audiolast,stretchfactor):
    output=np.zeros(0)
    audinterp = interp(np.arange(audio.shape[0]),audio)
    output = np.int16(audinterp(np.linspace(0,audio.shape[0]-1,int(audio.shape[0]*stretchfactor))))
    for index in np.arange((int(output.shape[0]-audio.shape[0]))):
        wet = index/(output.shape[0]-audio.shape[0])
        output[index] = np.int16((1-wet)*audiolast[::-1][index]+wet*output[index])
    return output

audiolast=np.zeros(int(CHUNK*2*1.4))

for i in range(int(RECORD_TIME*2*(RATE/CHUNK))): #do this for 10 seconds
    audio = np.frombuffer(stream.read(CHUNK),dtype=np.int16)#*detuner[i*CHUNK:(i+2)*CHUNK]
    audio = pitchdown(audio,audiolast,1.4)
    audio = bitcrush(audio,1000, 0.3)
    audio = delayline(audio,audiolast,0.3)
    player.write(np.int16(2*audio),CHUNK)
    audiolast=audio

stream.stop_stream()
stream.close()
p.terminate()