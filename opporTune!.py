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
import csv #store hashes in csv file which can be loaded as dict
from collections import defaultdict
import pyaudio
import wave

#Change presets of the library to the ones needed for our audio analysis
#From https://librosa.github.io/librosa/auto_examples/plot_presets.html
librosa = Preset(_librosa)
librosa['sr'] = 44100
librosa['hop_length'] = 2048 #windowing size
librosa['n_fft'] = 4096

minDB = -20
neighborSize = 15
maxDelTime = 10 
masterDict = dict()
songList= list()
matchThresh = 10
songsPlayed = 0


# might make sense to use default dict for speed purposes
def loadDict(hashCsv):
    #create new csv or load dict as csv
    # if loading i must parse into 1 dict where keys are a list with tuples in them
    #https://docs.python.org/3/library/csv.html
    #https://stackoverflow.com/questions/6740918/creating-a-dictionary-from-a-csv-file
    try:
        with open(hashCsv, mode='r') as infile:
            reader = csv.reader(infile)
            masterDict = {rows[0]:rows[1:] for rows in reader}
    except:
        masterDict = dict()
        print('No existing file') 

   
def saveDict(hashCsv, masterDict):
    with open(hashCsv, 'w') as file:
        for hashVal in masterDict:
            file.write(str(hashVal))
            for elem in masterDict[hashVal]:
                file.write(",")
                file.write(str(elem[0]))
                file.write(",")
                file.write(str(elem[1]))
            file.write("\n")

def songIndex(song):
    if song in songList:
        return songList.index(song)
    else:
        songList.append(song)
        return len(songList) - 1
    
'''
class Song(object):
   def __init__(self,path):
        self.songID = os.path.basename(os.path.normpath(song))
        self.songIndex = songIndex(songID) 
        self.songArray, self.samplingRate = librosa.load(path)'''
    
#Use this as template, if lost /Users/aditiraghavan/Documents/PraNos.mp3
#Fingerprints the song sample
def fingerprint(song):
    songID = os.path.basename(os.path.normpath(song))#https://stackoverflow.com/questions/3925096/how-to-get-only-the-last-part-of-a-path-in-python
    #tempIndex = songIndex(songID)
    y, sr = librosa.load(song)
    fftTransform = np.abs(librosa.core.stft(y=y, n_fft = 4096, hop_length = 2048) )
    fftTransform = librosa.power_to_db(fftTransform, ref = np.max)
    displaySpectrogram(fftTransform, 'linear', 1)
    print('before transpose finished', fftTransform.shape)
    fftTransform = fftTransform.transpose()
    print('transpose finished', fftTransform.shape)
    fftFilter, indexList = peakArray(fftTransform, neighborSize)
    print('peak finished', fftFilter.shape)
    fftFilter= fftFilter.transpose()
    print('transpose 2 finished', fftFilter.shape)
    displaySpectrogram(fftFilter, 'linear',2)
    #createHash(indexList,15,masterDict,songID)
    #saveDict('hashSong.csv', masterDict)
    pass
    
'''
    #plt.show()
    timeIdx = list()
    freqIdx = list()
    for elem in indexList:
        timeIdx.append(elem[0])
        freqIdx.append(elem[1])
    fig, ax = plt.subplots()
    #ax.imshow(melFilter)
    ax.scatter(timeIdx, freqIdx)
    ax.set_xlabel('Time')
    ax.set_ylabel('Frequency')
    plt.gca().invert_yaxis()
    plt.show()'''
   

#https://librosa.github.io/librosa/generated/librosa.core.power_to_db.html
#for more information https://matplotlib.org/     
#Fingerprints in song, shown in a figure 
def displaySpectrogram(spec, yAxis,num):
    plt.figure(num)
    librosa.display.specshow(spec, y_axis=yAxis, fmax=8000, x_axis='time') 
    plt.colorbar(format='%+2.0f dB')
    plt.title('Fingerprints')
    plt.tight_layout()
    

#Creates a new array of the same size as the melTransform and is filled with
# 0's and 1's , where 1's indicate peaks
def peakArray(arr2D, neighborSize):
    indexList = list()
    shapeArr = arr2D.shape
    rows = len(arr2D)
    cols = len(arr2D[0])
    #change peaks from list to array type 
    peaks = np.zeros(shapeArr)
    for row in range(rows):
        tempArrRow = arr2D[row]
        for col in range(cols):
            if tempArrRow[col] > minDB:
                maxFound = -1000
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
                maxIndex = np.argmax(tempNeighbor)#only gets you
                # the first index if there > 1, but does not affect functionality
                if maxFound > minDB:
                    if maxIndex + startIdx == col: 
                        peaks[row][col] = 1 
                        indexList.append((row,col))
    return peaks, indexList   
 
def addToDict(hashVal, songTime, mainDict):
    if (hashVal in mainDict):
        masterDict[hashVal] += [songTime]
    else:
        masterDict[hashVal] = [songTime]
    pass
           
def createHash(peakIndex, fanOut, mainDict, songID):
    for i in range(len(peakIndex)):
        for j in range(fanOut):
            if i + j < len(peakIndex):
                freq1 = peakIndex[i][1]
                time1 = peakIndex[i][0]
                freq2 = peakIndex[i+j][1]
                time2 = peakIndex[i+j][0]
                delTime = time2- time1
                if delTime < maxDelTime and delTime > 0:
                    tempKey = (hash((delTime,freq1,freq2)))
                    songTime = (songID,time1)
                    addToDict(tempKey,songTime, mainDict)
    pass
    
## Recognizer
import pyaudio
import wave


   
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLING = 44100
HOPLEN = 1024
RECORDSECONDS = 5
songsPlayed = 0 
waveOutput = "record.wav"


#Taken from https://stackoverflow.com/questions/35344649/reading-input-sound-signal-using-python
def readMic():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=SAMPLING, input=True,
                    frames_per_buffer=HOPLEN)
    frames = list()
    
    for i in range(0, int(SAMPLING / HOPLEN * RECORDSECONDS)):
        data = stream.read(HOPLEN,exception_on_overflow = False)
        frames.append(data)
    
    print("* done recording")
    stream.stop_stream()
    stream.close()
    audio.terminate()
    wf = wave.open(waveOutput, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(SAMPLING)
    wf.writeframes(b''.join(frames))
    wf.close()
    return waveOutput 
    
    
def recognize():
    song = readMic()
    y, sr = librosa.load(song)
    fftTransform = np.abs(librosa.core.stft(y=y, n_fft = 4096,hop_length = 2048) )
    fftTransform = librosa.power_to_db(fftTransform, ref = np.max)
    fftTransform = fftTransform.transpose()
    fftFilter, indexList = peakArray(fftTransform, neighborSize)
    fftFilter= fftFilter.transpose()
    print(indexList,neighborSize, masterDict, matchThresh)
    SongID, offset = match(indexList,neighborSize, masterDict, matchThresh)
    return SongID, offset


def match(peakIndex, fanOut, mainDict, matchThresh):
    for i in range(len(peakIndex)):
        for j in range(fanOut):
            if i + j < len(peakIndex):
                freq1 = peakIndex[i][1]
                time1 = peakIndex[i][0]
                freq2 = peakIndex[i+j][1]
                time2 = peakIndex[i+j][0]
                delTime = time2- time1
                if delTime < maxDelTime and delTime > 0:
                    tempKey = (hash((delTime,freq1,freq2)))
                    if tempKey in masterDict:
                        for value in masterDict[tempKey]:
                            songID = tuples[0]
                            time = tuples[1]
                            offset = time - time1
                            if songID in count and offset in count[SongID]:
                                count[songID][offset] += 1 
                                if count[songID][offset] == threshold:
                                    return songID,offset
                            else: 
                                count[SongID][offset] = 1
    return None,None


