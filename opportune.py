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
import eyed3
import sounddevice
from playsound import playsound #need to import PyObjC


#Change presets of the library to the ones needed for our audio analysis
#From https://librosa.github.io/librosa/auto_examples/plot_presets.html
librosa = Preset(_librosa)
librosa['sr'] = 44100
librosa['hop_length'] = 2048 #windowing size
librosa['n_fft'] = 4096

minDB = -30
neighborSize = 30
maxDelTime = 10 
masterDict = defaultdict(dict) 
songDict = defaultdict(dict) 
#TODO reload topSongDict and topArtistDict
topSongDict = defaultdict(dict)  
matchThresh = 50
reducedThresh = 25
numAttempted = 0
numIdentified = 0 

#topArtist = findTopArtist()


hashPath = '/Users/aditiraghavan/Documents/GitHub/opporTune/hashSong.csv'
songPath = '/Users/aditiraghavan/Documents/GitHub/opporTune/songData.csv'



#TODO reach goal - get song 

def startUp():
    loadDict()
    loadSongDict()

def shutdown():
    saveDict()
    saveSongDict()
    print('Closed')
    
def loadSongDict(hashCsv = songPath):
    global songDict
    try:
        with open(hashCsv, mode='r') as infile:
            reader = csv.reader(infile)
            for rows in reader:
                print(rows)
                tempList = list()
                songIndex = int(rows[0])
                for elem in range(1, len(rows)):
                    tempList.append(rows[elem])
                songDict[songIndex] = tempList
            
        print(songDict)
    except:
        print('No existing file')
    
def saveSongDict(hashCsv = songPath, mainDict = songDict):
    with open(hashCsv, 'w') as file:
        for hashVal in mainDict:
            file.write(str(hashVal))
            for elem in mainDict[hashVal]:
                file.write(",")
                file.write(str(elem))
            file.write("\n")

# might make sense to use default dict for speed purposes
def loadDict(hashCsv = hashPath):
    #create new csv or load dict as csv
    # if loading i must parse into 1 dict where keys are a list with tuples in them
    #https://docs.python.org/3/library/csv.html
    #https://stackoverflow.com/questions/6740918/creating-a-dictionary-from-a-csv-file
    global masterDict
    try:
        with open(hashCsv, mode='r') as infile:
            reader = csv.reader(infile)
            for rows in reader:
                tempList = list()
                hashVal = int(rows[0])
                for elem in range(1, len(rows),2):
                    index, time = int(rows[elem]), int(rows[elem + 1])
                    tempTuple = (index,time)
                    tempList.append(tempTuple)
                masterDict[hashVal] = tempList
    except:
        print('No existing file') 


def saveDict(hashCsv = hashPath, mainDict = masterDict):
    with open(hashCsv, 'w') as file:
        for hashVal in mainDict:
            file.write(str(hashVal))
            for elem in mainDict[hashVal]:
                file.write(",")
                file.write(str(elem[0]))
                file.write(",")
                file.write(str(elem[1]))

            file.write("\n")

def findTopSong():
    max = 0
    maxSong = None
    for song in topSongDict:
        if topSongDict[song] > max:
            max =  topSongDict[song]
            maxSong = song
    return (max,maxSong)
    

def songData(song):
    songID = os.path.basename(os.path.normpath(song))#https://stackoverflow.com/questions/3925096/how-to-get-only-the-last-part-of-a-path-in-python
    for addedSong in songDict:
        if songID == songDict[addedSong][0]:
            topSongDict[songID] += 1
            artist = findArtist(songID)        
            return None #To make sure its not added to database twice
    topSongDict[songID] = 1
    dataList = list()
    data = eyed3.load(song)
    songIndex = len(songDict)
    dataList.append(songID)
    try:
        artist = dataList.append(data.tag.artist)
        if artist in topArtistDict:
            topArtistDict[artist] +=1
        else:
            topArtistDict[artist] = 1
            
    except:
        dataList.append("Unknown")
    try:
        dataList.append(data.tag.album)
    except:
        dataList.append("Unknown")
    try:
        dataList.append(song)
    except:
        dataList.append("Unknown path")
    songDict[songIndex] = dataList
    return songIndex
  
def getSongData(songIndex):
    return songDict[songIndex][0], songDict[songIndex][1], songDict[songIndex][3] #song, artists, filepath
    
def playFile(path):
    print(path)
    #y, sr = librosa.load(path)
    playsound(path)
    
    
#TODO remove invalid data types from songdict
#try to keep track of number of files added and make that the index
def addToLibrary(song):
    print(song)
    songIndex = songData(song)
    print('Song Indexed')
    if songIndex != None:
        indexList = fingerprint(song)
        if indexList != None:
            createHash(indexList,15,masterDict,songIndex)
            print('Added to Library')
        else:
            print('Invalid data type')
    else:
        print('Already in Library')
    
#Use this as template, if lost /Users/aditiraghavan/Documents/PraNos.mp3
#Fingerprints the song sample
def fingerprint(song):
    print(song)
    try:
        y, sr = librosa.load(song)
        print('Parsed song')
    except:
        print('Could not parse song')
        return None
    fftTransform = np.abs(librosa.core.stft(y=y, n_fft = 4096, hop_length = 2048) )
    fftTransform = librosa.power_to_db(fftTransform, ref = np.max)
    fftTransform = fftTransform.transpose()
    fftFilter, indexList = peakArray(fftTransform, neighborSize)
    return indexList
    
    ''''
        displaySpectrogram(fftTransform, 'linear', 1)
    print('peak finished', fftFilter.shape)
    fftFilter= fftFilter.transpose()
    print('transpose 2 finished', fftFilter.shape)
    displaySpectrogram(fftFilter, 'linear',2)
    #createHash(indexList,15,masterDict,songID)
    #saveDict('hashSong.csv', masterDict)
    pass
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
    

#Creates a new array of the same size as the transform and is filled with
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
   
    
def recognize(songPath = None, easy = False):
    if songPath == None: 
        song = readMic()
    else: 
        song = songPath
    y, sr = librosa.load(song)
    fftTransform = np.abs(librosa.core.stft(y=y, n_fft = 4096,hop_length = 2048) )
    fftTransform = librosa.power_to_db(fftTransform, ref = np.max)
    fftTransform = fftTransform.transpose()
    
    fftFilter, indexList = peakArray(fftTransform, neighborSize)
    fftFilter= fftFilter.transpose()
    #print(indexList,neighborSize, masterDict, matchThresh)
    if easy == False:
        songIndex, offset = match(indexList,neighborSize, masterDict, matchThresh)
    else:
        songIndex, offset = match(indexList,neighborSize, masterDict, reducedThresh)
    global numAttempted
    global numIdentified
    numAttempted += 1 
    if songIndex != None:
        numIdentified += 1
        
        return songIndex
    else:
        print('Song not found')
        
        return None

#After fingerprinting song,it checks if it is already in the database
def match(peakIndex, fanOut, mainDict, matchThresh):
    #https://stackoverflow.com/questions/29348345/declaring-a-multi-dimensional-dictionary-in-python
    count = defaultdict(dict)
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
                            songID = value[0]
                            time = value[1]
                            offset = time - time1
                            if songID in count and offset in count[songID]:
                                count[songID][offset] += 1 
                                if count[songID][offset] == matchThresh:
                                    return songID,offset
                            else: 
                                count[songID][offset] = 1
    return None,None


