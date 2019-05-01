import sys
import os
from tkinter import filedialog
from tkinter import *
import opportune


opportune.startUp()
#https://pixabay.com/vectors/notes-music-music-notes-clef-1417670/

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
        try:
            for filename in os.listdir(path):
                files += listFiles(path + "/" + filename)
            return files
        except:
            return []

#Taken from https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html

def init(data):
    data.mode = "mainPage"
    data.fill = "black"
    data.actFill = "white" 
    data.song = None
    data.artist = None
    data.path = None
    data.logo = PhotoImage(file = '/Users/aditiraghavan/Documents/GitHub/opporTune/opportuneLogo.png')
    #https://www.dafont.com/static.font?text=opportune
    data.mainFont = "Dimitri 20"
    data.largerFont = "Dimitri 35"
    data.margin = 40
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
        print(data.path)
        if data.path != None:
            opportune.playFile(data.path)
            print('Played song')
            #TODO possibly change song playing feature so it can be stopped
        
    elif "back" in allTags:
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
    if data.mode == "mainPage": mainPageMousePressed(event,data, allTags)
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

def mainRedrawAll(canvas,data):
    margin = 75
    butWidth = 50
    butHeight = 20
    canvas.create_text(data.width/2, margin, text= "Opportune", font = 
    ('Dimitri Swank', 40) )
    canvas.create_text(margin,margin, text= "Stats", tags = "stats", font = 
    data.mainFont, activefill = data.actFill)
    canvas.create_text(data.width - margin, margin, text= 'Help', tags = "help", fill = data.fill, activefill = data.actFill, font = data.mainFont)
    canvas.create_text(data.width/2, data.height/2,  text = "Listen" , fill = data.fill, activefill = data.actFill, font = data.largerFont, tags = "listen")
    canvas.create_text(data.width/2, 3*data.height/4,  text = "Add Music" , fill = data.fill, activefill = data.actFill, font = data.mainFont, tags = "upload") 
 
def statsRedrawAll(canvas,data):
    canvas.create_text(data.width/2, data.margin, text = 'Stats', font = data.largerFont)
    topSong, plays = opportune.findTopSong()
    canvas.create_text(data.width/4, 3*data.margin, text = "Top Song:" + str(topSong), font = data.mainFont)
    canvas.create_text(data.width/4, 4*data.margin, text = "Top Artist:", font = data.mainFont)
    canvas.create_text(data.width/4, 3*data.height/4, anchor = "ne", fill = data.fill, activefill = data.actFill, font = data.mainFont, text = "Back" , tags = "back")

def helpRedrawAll(canvas,data):
    canvas.create_text(data.width/2, data.margin, text = 'Help', font = data.largerFont)
    canvas.create_text(data.width/4, 3*data.margin, \
    text= "\n\t\t\tPress upload to analyze an audio file on your computer\n\n\t\t\tPress listen to use the microphone on your computer\n\n\t\t\tPress the back button to return to the main page", font = "Dimitri 17", justify = "center")
    canvas.create_text(data.width/4, 3*data.height/4, anchor = "ne", fill = data.fill, activefill = data.actFill, font = data.mainFont, text = "Back" , tags = "back")
    
#TODO fix play button
def songFoundRedrawAll(canvas,data):
    songIndex = data.songIndex
    data.song, data.artist, data.path = opportune.getSongData(songIndex)
    canvas.create_text(data.width/2, data.height/2, text = str(data.song), font = data.mainFont,)
    canvas.create_text(data.width/2, data.height/2+ data.margin, text = str(data.artist), font = data.mainFont)
    canvas.create_text(data.width/4, 3*data.height/4, anchor = "ne", text = "Play Song" , fill = data.fill, activefill = data.actFill, font = data.mainFont, tags = "play")
    canvas.create_text(3*data.width/4, 3*data.height/4, anchor = "nw", fill = data.fill, activefill = data.actFill, font = data.mainFont, text = "Back" , tags = "back")    
    pass
    
def songTryAgainRedrawAll(canvas,data):
    canvas.create_text(data.width/2, data.height/3, text = "Song not found, try again!",font = data.mainFont,)
    canvas.create_text(3*data.width/4, 3*data.height/4, anchor = "n", text = "Try Again" , fill = data.fill, activefill = data.actFill, font = data.mainFont, tags = "tryAgain")
    canvas.create_text(data.width/4, 3*data.height/4, anchor = "ne", fill = data.fill, activefill = data.actFill, font = data.mainFont, text = "Back" , tags = "back")
    pass

def songNotFoundRedrawAll(canvas,data):
    canvas.create_text(data.width/2, data.height/2, text = "Song not found, we're sorry!",font = data.mainFont )
    canvas.create_text(data.width/4, 3*data.height/4, anchor = "ne", fill = data.fill, activefill = data.actFill, font = data.mainFont, text = "Back" , tags = "back")    
    pass 

def redrawAll(canvas, data):
    canvas.create_rectangle(0,0,data.width,data.height, fill = "salmon")
    if data.mode == "mainPage": mainRedrawAll(canvas,data)
    elif data.mode == "stats": statsRedrawAll(canvas,data)
    elif data.mode == "help": helpRedrawAll(canvas,data)
    elif data.mode == "songFound": songFoundRedrawAll(canvas,data)
    elif data.mode == "songTryAgain": songTryAgainRedrawAll(canvas,data)
    elif data.mode == "songNotFound": songNotFoundRedrawAll(canvas,data)
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
        
    def quit():
        opportune.shutdown()
        root.destroy()
        
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    root = Tk()
    #https://stackoverflow.com/questions/111155/how-do-i-handle-the-window-close-event-in-tkinter
    root.protocol("WM_DELETE_WINDOW", quit)
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
    
  


    
run(500, 300)