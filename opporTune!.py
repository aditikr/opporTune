import os 
import os.path
import matplotlib.pyplot as plt
import numpy as np
from presets import Preset
from tkinter import *
import librosa as _librosa
import librosa.display as _display

#Change presets of the library to the ones needed for our audio analysis
librosa = Preset(_librosa)
librosa['sr'] = 44100
librosa['hop_length'] = 2048 #windowing size
librosa['n_fft'] = 4096
minDB = 30 
neighborSize = 20 

trial = input("Give me a song path!") 
#Use this as template, if lost /Users/aditiraghavan/Documents/PraNos.mp3

y, sr = librosa.load(trial)
melTransform = librosa.feature.melspectrogram(y=y, sr=sr)

#Creates a new array of the same size as the melTransform and is filled with
# 0's and 1's , where 1's indicate peaks
def peakArray(arr2D, neighborSize):
    rows = len(arr2D)
    cols = len(arr2D[0])
    peaks = [ ([None] * cols) for row in range(rows) ]
    for row in range(rows):
        tempArrRow = arr2D[row]
        for col in range(cols):
            if col + neighborSize < cols:
                tempNeighbor = tempArrRow[col:col + neighborSize]   
            else: 
                tempNeighbor = tempArrRow[col:]
            maxFound =  max(tempNeighbor)
            maxIndex = np.argmax(tempNeighbor) #only gets you
            # the first index if there > 1, but does not affect functionality
            if maxFound < minDB:
                maxIndex = -1 #change to reduce runtime
            for elem in range(len(tempNeighbor)):
                if elem == maxIndex:
                    peaks[row][col+elem] = 1
                else:
                    peaks[row][col+elem] = 0      
    return peaks    
           
melFilter = peakArray(melTransform, neighborSize)
      
#Fingerprints in song, shown in a figure
plt.figure()
librosa.display.specshow(librosa.power_to_db(melFilter, ref = np.max), y_axis='mel', fmax=8000, x_axis='time') 
plt.colorbar(format='%+2.0f dB')
plt.title('Fingerprints')
plt.tight_layout()
plt.show()
