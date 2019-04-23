import sys
import os
from tkinter import filedialog
from tkinter import *
import opportune

#TODO add UI for when song is found or not found 

master = Tk()
#opportune.loadDict()

def uploadWrapper():
    master.withdraw()
    upload = Tk()
    print ("Time to upload a song")
    #https://pythonspot.com/tk-file-dialogs/
    song = filedialog.askopenfilename(initialdir = "/",title = "Select file")
    upload.destroy()
    master.deiconify()
    print(opportune.recognize(song))
    pass
    
def recordWrapper():
    print ("Time to record a song")
    print(opportune.recognize())

def libraryWrapper():
    master.withdraw()
    library = Tk()
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
    library.destroy()
    master.deiconify()
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
 
def quit():
    opportune.saveDict()

upload = Button(master, text =" Upload a song", command=uploadWrapper)
upload.pack()
record = Button(master, text = "Record a song with a microphone", command = recordWrapper)
record.pack()
addToLibrary = Button(master, text = "Add to Library", command = libraryWrapper)
addToLibrary.pack()

#https://stackoverflow.com/questions/111155/how-do-i-handle-the-window-close-event-in-tkinter
master.protocol("WM_DELETE_WINDOW", quit)


mainloop()