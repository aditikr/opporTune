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

def recordWrapper():
    print ("Time to record a song")
    print(opportune.recognize())

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
    # load data.xyz as appropriate
    pass
 
def startPressed(data,x,y):
    butWidth = 75
    if x > data.width/2 - butWidth and x < data.width/2 + butWidth:
        return True
    if y > 5*data.height/8 and y < 6*data.height/8:
        return True
    return False
    
def startMousePressed(event, data, allTags):
    x = event.x
    y = event.y
    if startPressed(data,x,y):
        data.mode = "mainPage"  
    pass


def mainPageMousePressed(event,data, allTags):
    if "listen" in allTags:
        recordWrapper()
    elif "upload" in allTags:
        libraryWrapper()
    elif "help" in allTags:
        data.mode = "help"
    elif "stats" in allTags:
        data.mode = "stats"
    pass
    

def mousePressed(event, data, allTags):
    if data.mode == "start": startMousePressed(event, data, allTags)
    if data.mode == "mainPage": mainPageMousePressed(event,data, allTags)
    pass

def keyPressed(event, data):
    # use event.char and event.keysym
    pass

def startRedrawAll(canvas, data):
    butWidth = 75
    canvas.create_rectangle(0,data.width, 0, data.height, fill = "light slate blue")
    canvas.create_text(data.width/2, 100, text = 'Opportune It!')
    canvas.create_rectangle(data.width/2 - butWidth , 5*data.height/8 , data.width/2 + butWidth, 6*data.height/8, fill = "medium purple")
    pass

def mainRedrawAll(canvas,data):
    margin = 30
    butWidth = 50
    butHeight = 20
    canvas.create_text(data.width/2, 100, text = "Main Page")
    canvas.create_text(margin,margin, text= "Stats", tags = "stats" )
    canvas.create_text(margin,data.height - margin, text= 'Help', tags = "help")
    canvas.create_text(data.width/4, 5*data.height/8,  text = "Listen" , fill = "medium purple", activefill = "thistle", tags = "listen")
    canvas.create_text(3*data.width/4, 5*data.height/8,  text = "Upload" , fill = "medium purple", activefill = "thistle", tags = "upload")
 
 
def statsRedrawAll(canvas,data):
    margin = 20 
    canvas.create_text(data.width/2, margin, text = 'Your Stats')

def helpRedrawAll(canvas,data):
    margin = 20 
    canvas.create_text(data.width/2, margin, text = 'Help')
    

#TODO finish all modes
def redrawAll(canvas, data):
    if data.mode == "start": startRedrawAll(canvas, data)
    if data.mode == "mainPage": mainRedrawAll(canvas,data)
    if data.mode == "stats": statsRedrawAll(canvas,data)
    if data.mode == "help": helpRedrawAll(canvas,data)
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