import os 
import os.path
import matplotlib
matplotlib.use("TkAgg") #implemented as there is a conflict between tkinter and matplotlib
# more info: stackoverflow.com/questions/32019556/matplotlib-crashing-tkinter-application/34109240
import matplotlib.pyplot as plt
import numpy as np
from presets import Preset
from tkinter import *
import librosa as _librosa
import librosa.display as _display

#Change presets of the library to the ones needed for our audio analysis
#From https://librosa.github.io/librosa/auto_examples/plot_presets.html
librosa = Preset(_librosa)
librosa['sr'] = 44100
librosa['hop_length'] = 2048 #windowing size
librosa['n_fft'] = 4096
minDB = 10
neighborSize = 15

#Use this as template, if lost /Users/aditiraghavan/Documents/PraNos.mp3

def fingerprint(song):
    y, sr = librosa.load(song)
    melTransform = librosa.feature.melspectrogram(y=y, sr=sr)
    melTransform = melTransform.transpose()
    melFilter = peakArray(melTransform, neighborSize).transpose()
#https://librosa.github.io/librosa/generated/librosa.core.power_to_db.html
#for more information https://matplotlib.org/     
#Fingerprints in song, shown in a figure
    plt.figure()
    librosa.display.specshow(librosa.power_to_db(melFilter, ref = np.max), y_axis='mel', fmax=8000, x_axis='time') 
    plt.colorbar(format='%+2.0f dB')
    plt.title('Fingerprints')
    plt.tight_layout()
    plt.show()
    plt.close()
    return 
    

#Creates a new array of the same size as the melTransform and is filled with
# 0's and 1's , where 1's indicate peaks
def peakArray(arr2D, neighborSize):
    shapeArr = arr2D.shape
    rows = len(arr2D)
    cols = len(arr2D[0])
    #change peaks from list to array type 
    peaks = np.zeros(shapeArr)
    for row in range(rows):
        tempArrRow = arr2D[row]
        for col in range(cols):
            if col < neighborSize:
                startIdx = 0
            else:
                startIdx = col - neighborSize
            if col + neighborSize >= cols:
                endIdx = cols - 1
            else: 
                endIdx = col + neighborSize
            tempNeighbor = tempArrRow[startIdx:endIdx]
            maxFound =  max(tempNeighbor)
            maxIndex = np.argmax(tempNeighbor) #only gets you
            # the first index if there > 1, but does not affect functionality
            if maxFound > minDB:
                if maxIndex == col: 
                    peaks[row][col] = 1 
    return peaks    
           





