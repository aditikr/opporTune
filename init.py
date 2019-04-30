import sys
import os
from tkinter import filedialog
from tkinter import *
import opportune


#TODO add UI for when song is found or not found 

opportune.startUp()

'''   
 
def quit():
    opportune.shutdown()



#https://stackoverflow.com/questions/111155/how-do-i-handle-the-window-close-event-in-tkinter
master.protocol("WM_DELETE_WINDOW", quit)


mainloop()'''

##COMPLETE REFORMAT OF UI

def recordWrapper(easy = False):
    print ("Time to record a song")
    return opportune.recognize(easy = easy)

def libraryWrapper():
    print ("Add to library")
    #https://pythonspot.com/tk-file-dialogs/
    try:
        folder = filedialog.askdirectory()
    except:
        ("Error finding Directory") 
    listSong = listFiles(folder)
    for song in listSong:
        try:
            opportune.addToLibrary(song)
            print("Added song")
        except:
            print("Error reading file, moving to next one")
    print('Done adding!')
    pass

#Taken from https://www.cs.cmu.edu/~112/notes/notes-recursive-applications.html#listFiles
def listFiles(path):
    if os.path.isfile(path):
        # Base Case: return a list of just this file
        return [ path ]
    else:
        # Recursive Case: create a list of all the recursive results from the files in the folder
        files = [ ]
        for filename in os.listdir(path):
            files += listFiles(path + "/" + filename)
        return files

#Taken from https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
####################################
# customize these functions
####################################

def init(data):
    data.mode = "start"
    data.fill = "medium purple"
    data.ActFill = "thistle" 
    data.textFill = "black"
    data.song = None
    data.artist = None
    data.path = None
    pass
 
    
def startMousePressed(event, data, allTags):
    if "start" in allTags:
        data.mode = "mainPage"
    pass

def mainPageMousePressed(event,data, allTags):
    if "listen" in allTags:
        data.songIndex = recordWrapper()
        if data.songIndex != None:
            data.mode = "songFound"
        else:
            data.mode = "songTryAgain"
        
    elif "upload" in allTags:
        libraryWrapper()
    elif "help" in allTags:
        data.mode = "help"
    elif "stats" in allTags:
        data.mode = "stats"
    pass

def helpAndStatsMousePressed(event,data, allTags):
    if "back" in allTags:
        data.mode = "mainPage"
    pass

def songFoundMousePressed(event,data, allTags):
    if "play" in allTags:
        if data.path != None:
            opportune.playFile(data.path)
            print('Played song')
            #TODO possibly change song playing feature so it can be stopped
        
    elif "back" in allTags:
        #opportune.playFile(None)
        data.mode = "mainPage"
    pass

def songTryAgainMousePressed(event,data, allTags):
    if "tryAgain" in allTags:
        data.songIndex = recordWrapper(True)
        if data.songIndex != None:
            data.mode = "songFound"
        else:
            data.mode = "songNotFound"
    elif "back" in allTags:
        data.mode = "mainPage"
    pass
    
def songNotFoundMousePressed(event,data, allTags):
    if "back" in allTags:
        data.mode = "mainPage" 
    pass
    
def mousePressed(event, data, allTags):
    if data.mode == "start": startMousePressed(event, data, allTags)
    elif data.mode == "mainPage": mainPageMousePressed(event,data, allTags)
    elif data.mode == "help" or data.mode == "stats": helpAndStatsMousePressed(event,data, allTags)
    elif data.mode == "songFound":
        songFoundMousePressed(event,data, allTags)
    elif data.mode == "songTryAgain":
        songTryAgainMousePressed(event,data, allTags)
    elif data.mode == "songNotFound":
        songNotFoundMousePressed(event,data, allTags)
    pass

def keyPressed(event, data):
    # use event.char and event.keysym
    pass

def startRedrawAll(canvas, data):
    butWidth = 75
    canvas.create_rectangle(0,data.width, 0, data.height, fill = "light slate blue")
    canvas.create_text(data.width/2, 100, text = 'Opportune It!')
    canvas.create_rectangle(data.width/2 - butWidth , 5*data.height/8 , data.width/2 + butWidth, 6*data.height/8, fill = "medium purple", tags = "start")
    pass

def mainRedrawAll(canvas,data):
    margin = 30
    butWidth = 50
    butHeight = 20
    canvas.create_text(data.width/2, 100, text = "Main Page")
    canvas.create_text(margin,margin, text= "Stats", tags = "stats" )
    canvas.create_text(data.width - margin, margin, text= 'Help', tags = "help")
    canvas.create_text(data.width/4, 5*data.height/8,  text = "Listen" , fill = "medium purple", activefill = "thistle", tags = "listen")
    canvas.create_text(3*data.width/4, 5*data.height/8,  text = "Add Music" , fill = "medium purple", activefill = "thistle", tags = "upload")
 
 
def statsRedrawAll(canvas,data):
    margin = 20 
    canvas.create_text(data.width/2, margin, text = 'Your Stats')
    topSong, plays = opportune.findTopSong()
    canvas.create_text(data.width/2, margin*2, text = str(topSong) + str(plays))
    canvas.create_text(3*data.width/4, 5*data.height/8,  text = "Back" , fill = "medium purple", activefill = "thistle", tags = "back")



def helpRedrawAll(canvas,data):
    margin = 40 
    canvas.create_text(data.width/2, margin, text = 'Help')
    canvas.create_text(2*margin, 2*margin, \
    text= "\tPress upload to analyze an audio file on your computer\n\tPress listen to use the microphone on your computer\n\tPress the back button to return to the main page")
    canvas.create_text(data.width - margin, margin, text= 'Back', tags = "back")
    
    
def songFoundRedrawAll(canvas,data):
    spacing = 20 
    songIndex = data.songIndex
    data.song, data.artist, data.path = opportune.getSongData(songIndex)
    canvas.create_text(data.width/2, data.height/2, text = str(data.song))
    canvas.create_text(data.width/2, data.height/2+ spacing, text = str(data.artist))
    canvas.create_text(data.width/4, 5*data.height/8,  text = "Play Song" , fill = "medium purple", activefill = "thistle", tags = "play")
    canvas.create_text(3*data.width/4, 5*data.height/8,  text = "Back" , fill = "medium purple", activefill = "thistle", tags = "back")
    pass
    
def songTryAgainRedrawAll(canvas,data):
    canvas.create_text(data.width/2, data.height/2, text = "Song not found, try again!")
    canvas.create_text(data.width/4, 5*data.height/8,  text = "Try Again" , fill = "medium purple", activefill = "thistle", tags = "tryAgain")
    canvas.create_text(3*data.width/4, 5*data.height/8,  text = "Back" , fill = "medium purple", activefill = "thistle", tags = "back")
    pass

def songNotFoundRedrawAll(canvas,data):
    canvas.create_text(data.width/2, data.height/2, text = "Song not found, we're sorry!'")
    canvas.create_text(3*data.width/4, 5*data.height/8,  text = "Back" , fill = "medium purple", activefill = "thistle", tags = "back")
    pass
    

def redrawAll(canvas, data):
    if data.mode == "start": startRedrawAll(canvas, data)
    elif data.mode == "mainPage": mainRedrawAll(canvas,data)
    elif data.mode == "stats": statsRedrawAll(canvas,data)
    elif data.mode == "help": helpRedrawAll(canvas,data)
    elif data.mode == "songFound": songFoundRedrawAll(canvas,data)
    elif data.mode == "songTryAgain": songTryAgainRedrawAll(canvas,data)
    elif data.mode == "songNotFound": songNotFoundRedrawAll(canvas,data)
    # draw in canvas
    pass

####################################
# use the run function as-is 
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        item = canvas.find_closest(event.x, event.y)
        allTags = canvas.itemcget(item,"tags") #https://stackoverflow.com/questions/38982313/python-tkinter-identify-object-on-click
        mousePressed(event, data, allTags)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    redrawAllWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(400, 200)