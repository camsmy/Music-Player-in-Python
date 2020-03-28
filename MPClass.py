import os #Directory                        #=============================================================================
import sys                                  #                           NEED TO INSTALL:                                 #
import sqlite3                              #                          - pip install pygame                              #
import random #Shuffle Play                 #                          - pip install PIL                                 #
import pygame #MP3 Functions                #                          - pip install tinytag                             #
import tkinter.messagebox                   #                                                                            #
from tkinter import * #window               #                                                                            #
from pygame.locals import *                 #=============================================================================
from PIL import ImageTk, Image #image
from tkinter.filedialog import askdirectory #ask directory file path
from tinytag import TinyTag, TinyTagException #MP3 Details(Artist, Album, etc.)



class MyWindow:
#=======================================================LOGIN WINDOW=======================================================
    # Constructor
    def __init__(self,window):
        tkinter.messagebox.showinfo('Ask Directory','Please select the ALL Folder')
        self.directory = askdirectory()
        self.conn = sqlite3.connect(self.directory + "/mp.db")
        self.c = self.conn.cursor()
        #          VARIABLES 
        self.acc = [] #list for user account
        self.usern = StringVar() #stores username
        self.passw = StringVar() #stores password
        self.var = IntVar() #Remember me variable 
        self.listofsongs = [] #inserts all songs in a list
        self.songinfo= [] #song info (Title, Artist)
        self.index = 0 #pointer for what to play
        self.shuffle = False #for Shuffle 
        self.repeat = False #for Repeat
        self.stop = False #for Stop 
        self.isPlaylist = False #if playlist is to be played
        self.tempstopped = 0 #stores the index of last song played
        self.tempprevsong = [] #stores the index of the previous song (for all song)
        self.tempprevsong1 = [] #stores the index of the previous song (for playlist)
        self.pplaylist = [] #stores all song from playlist
        self.v = "" #label for song title
        self.art = "" #label for song artist
        self.npplist = "" #label for now playing playlist
        #BACKGROUND IMAGE 
        self.canvas = Canvas(window,width=500,height=600)
        self.image = ImageTk.PhotoImage(Image.open(self.directory + "/ui/login.png"))
        self.canvas.create_image(0,0,anchor=NW,image=self.image)
        self.canvas.pack()
        
        #USERNAME 
        self.username = Label(window, text='Username: ', width=30,font=('cambria',11,'bold'),background="DarkGoldenRod1").place(x=120,y=270)
        self.userentry = Entry(window, width=40, textvar = self.usern,border=2).place(x=135,y=290)
        
        #PASSWORD 
        self.pw = Label(window, text='Password: ', width=30,font=('cambria',11,'bold'),background="DarkGoldenRod1").place(x=120,y=310)
        self.pwentry = Entry(window, width=40,show="*",  textvar = self.passw,border=2).place(x=135,y=330)

        #REMEMBER ME? 
        self.rb  = Radiobutton(window, text="Remember Me?", variable=self.var,font=('cambria',11,'bold') ,value=1, background="DarkGoldenRod1")
        self.rb.place(x=180,y=360)

        #LOGINBUTTON 
        self.li = Button(window, text ="LOGIN",font=('cambria',16,'bold'), background='black', fg="DarkGoldenRod1", command = self.LoginCheck).place(x=210,y=400 )
    
        #Don't have an account? 
        self.noacc = Label(window,text="Don\'t have an account?",font=('cambria',10,'bold'), background="DarkGoldenRod1").place(x=130, y=460)
        self.link1 = Label(window, text="REGISTER HERE",font=('cambria',10,'bold'), fg="blue", cursor="hand2",background="DarkGoldenRod1")
        self.link1.place(x=270,y=460)
        self.link1.bind("<Button-1>", lambda e: self.register())

    #Check if account exist
    def LoginCheck(self): 
    
        #get account details 
        for row in self.c.execute("SELECT * FROM User"):
            self.acc.append(list(row))
        i = 0

        #traverse to acc
        noAcc = False
        isValid = False
        for line in self.acc:
            i+=1
            # check if the user has the correct password
            if(str(self.usern.get()) == str(line[0])):
                if(str(self.passw.get()) == str(line[1])):
                    isValid = True
                    # self.MP3Win()
                    break
                else:
                    tkinter.messagebox.showwarning('Wrong Passowrd','Wrong password! Try again.')
                    break
            else:
                if i == len(self.acc) - 1:
                    noAcc = True
        if isValid:
            self.displayplaylist()
        elif not isValid and noAcc:
            tkinter.messagebox.showwarning("No Registered Username", "Username is not registered in the app!")


#=============================================================================================================================       
#=======================================================REGISTER WINDOW=======================================================
    # register window
    def register(self):

        #create window
        self.reg = Toplevel()
        self.reg.geometry("500x600+20+20")        
        self.reg.title("Register Account")
        self.canvas1 = Canvas(self.reg,width=500,height=600)
        self.image1 = ImageTk.PhotoImage(Image.open(self.directory + "/ui/login.png")) 
        self.canvas1.create_image(0,0,anchor=NW,image=self.image1)
        self.canvas1.pack()

        #USERNAME 
        self.username = Label(self.reg, text='Username: ', width=30,font=('cambria',11,'bold'),background="DarkGoldenRod1").place(x=120,y=270)
        self.userentry = Entry(self.reg, width=40, textvar = self.usern,border=2).place(x=135,y=290)
        
        #PASSWORD 
        self.pw = Label(self.reg, text='Password: ', width=30,font=('cambria',11,'bold'),background="DarkGoldenRod1").place(x=120,y=310)
        self.pwentry = Entry(self.reg, width=40,show="*",  textvar = self.passw,border=2).place(x=135,y=330)
        
        #REGISTERBUTTON 
        self.li = Button(self.reg, text ="Register",font=('cambria',16,'bold'), background='black', fg="DarkGoldenRod1", command = self.Usercheck).place(x=210,y=400 )

    # check if the entered username already exist
    def Usercheck(self):
        found = False
        # get username for every account
        for row in self.c.execute("SELECT Username FROM User"):
            if( self.userentry == str(row)):
                found = True
                break
        if(found):
            tkinter.messagebox.showwarning('User already exists',"The User is existing already!")
        else:
            self.c.execute("INSERT INTO User VALUES (?, ?)", (str(self.usern.get()), str(self.passw.get())))
            self.conn.commit()
            self.reg.destroy()

#=============================================================================================================================
#============================================================STPLAYER=========================================================
    
    #====================================================== MP3 Window===============================================
    def MP3Win(self):
        # Create Window          
        self.screen = pygame.display.set_mode((1000, 750))
        self.W, self.H = 1000, 750
        self.HW, self.HH = self.W / 2, self.H / 2
        self.AREA = self.W * self.H
        os.environ['SDL_VIDEO_WINDOW_POS'] = "50,50"
        # SETUP PYGAME
        self.CLOCK = pygame.time.Clock()
        self.DS = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("STMusic Player")
        self.icon = pygame.image.load(self.directory + "/ui/logo.png")
        pygame.display.set_icon(self.icon)
        self.FPS = 120
        self.bkgd = pygame.image.load(self.directory + "/ui/parallax-bg.png").convert()
        x = 0
        
        #Vinyl
        self.ui_vinyl = pygame.image.load(self.directory + "/ui/vinyl-2.png")
        self.Xcoord = 315
        self.Ycoord = 100

        #Buttons Background 
        self.ui_bg2 = pygame.image.load(self.directory + "/ui/bg2.png")
        self.bg_Xcoord = 0
        self.bg_Ycoord = 590

        #PLAY BUTTON 
        self.ui_play = pygame.image.load(self.directory + "/ui/play.png")
        self.play_rect =self.ui_play.get_rect(topleft=(480,640))

        #STOP BUTTON 
        self.ui_stop = pygame.image.load(self.directory + "/ui/stop.png")
        self.stop_rect = self.ui_stop.get_rect(topleft=(380,640))

        #PAUSE BUTTON 
        self.ui_pause = pygame.image.load(self.directory + "/ui/pause.png")
        self.pause_rect = self.ui_pause.get_rect(topleft=(580,640))

        #NEXT BUTTON 
        self.ui_nextbut = pygame.image.load(self.directory + "/ui/next.png")
        self.nextbut_rect = self.ui_nextbut.get_rect(topleft=(700,650))

        #REPLY BUTTON 
        self.ui_reply = pygame.image.load(self.directory + "/ui/abcd.png")
        self.reply_rect = self.ui_reply.get_rect(topleft=(900,650))

        #SHUFFLE BUTTON 
        self.ui_shuffle = pygame.image.load(self.directory + "/ui/shuffle.png")
        self.shuffle_rect = self.ui_shuffle.get_rect(topleft=(800,650))
        
        #PREVIOUS BUTTON 
        self.ui_prev = pygame.image.load(self.directory + "/ui/previous.png")
        self.prev_rect = self.ui_prev.get_rect(topleft=(250,650))

        #VOLUME UP
        self.ui_volup = pygame.image.load(self.directory + "/ui/volup.png")
        self.volup_rect = self.ui_volup.get_rect(topleft=(150,650))

        #VOLUME DOWN
        self.ui_voldw = pygame.image.load(self.directory + "/ui/voldown.png")
        self.voldw_rect = self.ui_voldw.get_rect(topleft=(50,650))


        #EXIT BUTTON
        self.ui_exit = pygame.image.load(self.directory + "/ui/exit.png")
        self.exit_rect = self.ui_exit.get_rect(topleft=(930,10))

        #Display Song info
        pygame.init()
        self.myfont = pygame.font.SysFont("monospace", 20)
        self.myfont.set_bold(True)

        #RENDER TEXT
        self.label = self.myfont.render(self.v, 1, (255,255,0))
        self.artlabel = self.myfont.render(self.art,1,(255,255,0))
        self.myfont = pygame.font.SysFont("monospace", 32)
        self.myfont.set_bold(True)
        self.pltitle = self.myfont.render(self.npplist,1,(255,255,0))
        
        #MAIN LOOP
        while True:
            pygame.init()
            self.events()
            self.rel_x = x % self.bkgd.get_rect().width
            self.DS.blit(self.bkgd, (self.rel_x - self.bkgd.get_rect().width, 0))
            if self.rel_x < self.W:
                self.DS.blit(self.bkgd, (self.rel_x, 0))
            x -= 1
            pygame.draw.line(self.DS, (255, 0, 0), (self.rel_x, 0), (self.rel_x, self.H), 0)
            # Display on Pygame Window
            self.DS.blit(self.pltitle, ((self.W - self.ulen * 10)/2, 30))
            self.DS.blit(self.label, ((self.W - self.slen * 10)/2, 520))
            self.DS.blit(self.artlabel, ((self.W - self.alen * 10)/2, 550))
            self.load_vinyl()
            self.load_bg2()
            self.load_play()
            self.load_stop()
            self.load_pause()
            self.load_nextbut()
            self.load_reply()
            self.load_prev()
            self.load_shuffle()
            self.load_exit()
            self.load_volup()
            self.load_voldw()
            pygame.display.update()
            self.CLOCK.tick(self.FPS)


    # GET DIRECTORY OF MP3 FILES
    def directorychooser(self):
        directory = (self.directory + "/mp3") 
        os.chdir(directory)
        # store mp3 files in a list
        for root, dirs, files in os.walk(directory):
            for name in files:
                if name.endswith(".mp3"):
                    temp_track = TinyTag.get(root + "\\"+name)
                    self.listofsongs.append(name)
                    tempdict = {"Title":temp_track.title,"Artist":temp_track.artist}
                    self.songinfo.append(tempdict) #eto info (title + artist) dict within a list

        #play the first song list
        pygame.mixer.init()
        pygame.mixer.music.load(self.listofsongs[0])

        #get the name of song
        self.v = self.listofsongs[self.index].replace(".mp3","")
        #get the name of artist
        self.art = self.songinfo[self.index].get("Artist")
        for i in self.listofsongs:
            self.pplaylist.append(i)        
        
    # display the current playing song
    def updatelabel(self):
        # setup pygame
        pygame.init()
        self.myfont = pygame.font.SysFont("monospace", 20)
        self.myfont.set_bold(True)
        # if not on playlist
        if not self.isPlaylist:
            self.v = self.listofsongs[self.index].replace(".mp3","")

        # if on playlist
        else:
            self.v = self.pplaylist[self.index].replace(".mp3","")
        self.label = self.myfont.render(self.v, 1, (255,255,0))
        self.slen = len(str(self.v))
        pygame.mixer.music.play()
        
    #display the current playing playlist
    def updateplist(self):
        pygame.init()
        self.myfont = pygame.font.SysFont("monospace", 32)
        self.myfont.set_bold(True)
        self.pltitle = self.myfont.render(self.npplist,1,(255,255,0))

    #display the current playing song artist
    def updateartist(self):
        pygame.init()
        self.myfont = pygame.font.SysFont("monospace", 20)
        self.myfont.set_bold(True)

        #if not on playlist
        if not self.isPlaylist:
            self.art = self.songinfo[self.index].get("Artist")

        #if on playlist
        else:
            for dicts in self.songinfo:
                if dicts["Title"] == self.pplaylist[self.index].replace(".mp3",""):
                    self.art = dicts.get("Artist")
        self.artlabel = self.myfont.render(self.art,1,(255,255,0))
        self.alen = len(str(self.art))


    # go to next song
    def nextsong(self):
        
        # if all songs
        if not self.isPlaylist:

            #store the current running song in a list
            self.tempprevsong.append(self.index)
            self.tempind = self.index

            #if shuffle is on 
            if(self.shuffle):
                while(self.tempind == self.index):

                    #random generated
                    self.index = random.randint(0, len(self.listofsongs) - 1)
            
            #if shuffle is not on
            else:

                #if last song go back to first song
                if(len(self.listofsongs) == self.index+1):
                    self.index = 0
                else:
                    self.index += 1
            pygame.mixer.music.load(self.listofsongs[self.index])
        else:
            self.tempprevsong1.append(self.index)
            self.tempind1 = self.index
            #if shuffle is on 
            if(self.shuffle):
                while(self.tempind1 == self.index):

                    #random generated
                    self.index = random.randint(0, len(self.pplaylist) - 1)
            else:
                #if last song go back to first song
                if(len(self.pplaylist) == self.index+1):
                    self.index = 0
                else:
                    self.index += 1
            pygame.mixer.music.load(self.pplaylist[self.index])
        pygame.mixer.music.play()
        self.updatelabel()
        self.updateartist()
        

    #go to prervious song
    def prevsong(self):

        #if on playlist
        if not self.isPlaylist:

            #if previous songs list is not empty
            if(len(self.tempprevsong) != 0):

                #pop the stored songs
                self.index = self.tempprevsong.pop()
            else:

                #if last song go back to first song
                if(self.index == 0):
                    self.index = len(self.listofsongs) - 1
                else:
                    self.index -= 1
            pygame.mixer.music.load(self.listofsongs[self.index])

        #if not on playlist
        else:

            #if previous songs list is not empty
            if(len(self.tempprevsong1) != 0):

                #pop the stored songs
                self.index = self.tempprevsong1.pop()
            else:

                #if last song go back to first song
                if(self.index == 0):
                    self.index = len(self.pplaylist) - 1
                else:
                    self.index -= 1
            pygame.mixer.music.load(self.pplaylist[self.index])

        pygame.mixer.music.play()

        #update the song name and artist name in GUI
        self.updatelabel()
        self.updateartist()


    #stop song
    def stopsong(self):
        self.stop = True

        #store the last song played
        self.tempstopped = self.index
        pygame.mixer.music.stop()
        self.v = ""
        self.art = ""


    #pause song
    def pausesong(self):
        pygame.mixer.music.pause()


    #unpause song
    def unpausesong(self):

        #check if there is no song playing
        if(self.stop == True):

            #if playing a playlist    
            if not self.isPlaylist:
                pygame.mixer.music.load(self.listofsongs[self.tempstopped])
            else:
                pygame.mixer.music.load(self.pplaylist[self.tempstopped])
            pygame.mixer.music.play()
            self.stop = False

            #update song name and artist name on GUI
            self.updatelabel()
            self.updateartist()
        else:
            pygame.mixer.music.unpause()


    #shuffle song 
    def shufflesong(self):
        if(self.shuffle):
            self.shuffle = False
        else:
            self.shuffle = True


    #repeat song
    def repeatsong(self):
        if(self.repeat):
            self.repeat = False
        else:
            self.repeat = True


    #volume up
    def volume_up(self):
        vol = pygame.mixer.music.get_volume() + 0.1
        pygame.mixer.music.set_volume(vol)


    #volume down
    def volume_down(self):
        vol = pygame.mixer.music.get_volume() - 0.1
        pygame.mixer.music.set_volume(vol)

#==================================================DISPLAY PLAYLIST=========================================================
    #display all the available playlist
    def displayplaylist(self): 
        pygame.init()
        self.listofsongs = []
        self.pplaylist = []
        self.directorychooser()

        # create window
        self.displaylist = Toplevel()
        self.displaylist.geometry("500x600+20+20")
        self.displaylist.title("My Playlist")
        self.displaylist.configure(background='black')
        self.crpl = Label(self.displaylist, text='Playlist', width=30,font=('cambria', 18,'bold'),background="DarkGoldenRod1").place(x=40,y=15)
        
        #create listbox for playlist
        self.playlistbox = Listbox(self.displaylist, background='black',selectmode=SINGLE,fg = "DarkGoldenRod1", width=70)
        self.playlistbox.place(x=40,y=50)  
        self.crpl = Label(self.displaylist, text='Songs on Playlist', width=30,font=('cambria', 18,'bold'),background="DarkGoldenRod1").place(x=40,y=215)

        #create listbox for available songs
        self.listofsong = Listbox(self.displaylist, background='black',selectmode=SINGLE,fg = "DarkGoldenRod1", width=70)
        self.listofsong.place(x=40,y=250)

        #Scrollbar(self.listofsong,orient="vertical")
        if len(self.pplaylist) !=0:
            for song in self.pplaylist:
                self.listofsong.insert(0,song.replace(".mp3",""))
        self.splaylist()
        
        #draw button on GUI
        self.crtpl = Button(self.displaylist,text="Create Playlist",width=15, font=('cambria',15,'bold'), background='DarkGoldenRod1', fg="black", command = self.createplaylist).place(x=50,y=430 )
        self.rmvpl = Button(self.displaylist,text="Remove Playlist",width=15,font=('cambria',15,'bold'), background='DarkGoldenRod1', fg="black", command = self.removeplaylist).place(x=265,y=430 )
        self.checklist = Button(self.displaylist,text="Check",width=15,font=('cambria',15,'bold'), background='DarkGoldenRod1', fg="black", command = self.checkplist).place(x=265,y=485 )
        self.editpl = Button(self.displaylist,text="Edit",width=15,font=('cambria',15,'bold'), background='DarkGoldenRod1', fg="black", command = self.editplay).place(x=50,y=485 )
        self.plist = Button(self.displaylist,text="Play",width=33,font=('cambria',15,'bold'), background='DarkGoldenRod1', fg="black", command = self.playall).place(x=50,y=545 )
    

    #Check playlist
    def checkplist(self):
        #to get the picked playlist
        self.tempstr = self.playlistbox.curselection()
        self.listofsong.delete(0,END)
        self.index = 0
        if not self.tempstr:
            tkinter.messagebox.showwarning("Error Playing","Please select playlist!")
        else:
            #if not on playlist
            if self.tempstr[0] == 0:
                self.isPlaylist = False
                for song in self.listofsongs:
                    self.listofsong.insert(0,song.replace(".mp3",""))

            #if on playlist
            else:
                self.pplaylist.clear()
                tempint = self.tempstr[0]
                tempint-=1

                #get the playlist from database
                for song in self.c.execute("SELECT Title from "+self.temptitle[tempint][0]): 
                    self.pplaylist.append(song[0]+".mp3")
                    self.listofsong.insert(0,song[0])
                self.isPlaylist = True

    #select database playlist
    def splaylist(self): 
        self.temptitle = []
        self.playlistbox.delete(0,END)

        #Get the available playlist of the user
        for line in self.c.execute("SELECT PlaylistTitle FROM UserPlaylist WHERE Username = (?)",(self.usern.get(),)):
            self.temptitle.append(line)
            self.playlistbox.insert(0,line[0])
        self.temptitle.reverse()
        self.playlistbox.insert(0,"All Songs")


    #play playlist and go to PLAYER
    def playall(self): 
        self.checkplist() 
        
        #chosen playlist of user
        self.tempstr = self.playlistbox.curselection() #pinili ng user

        #delete list of songs in listbox
        self.listofsong.delete(0,END) 

        #to go back to first song
        self.index = 0 
        #if not on playlist
        if self.tempstr:
            if self.tempstr[0] == 0: 
                self.isPlaylist = False 

                #display songs on listbox
                for song in self.listofsongs: 
                    self.listofsong.insert(0,song.replace(".mp3",""))
                pygame.mixer.music.load(self.listofsongs[self.index]) 
                #set the current song name and artist
                self.v = self.listofsongs[self.index].replace(".mp3","")
                self.v = self.songinfo[self.index].get("Artist")
                self.npplist = "All Songs"
                self.ulen = len(str(self.npplist))
                pygame.init()
                self.updateplist()
                self.updatelabel() 
                self.updateartist()
                self.MP3Win()

            #if on playlist
            else: 
                self.pplaylist.clear() 
                tempint = self.tempstr[0] 
                tempint-=1 
                self.c.execute("SELECT COUNT(Title) from "+self.temptitle[tempint][0])

                #count if empty
                templ = list(self.c) 
                temptup = templ[0]

                #if playlist is empty
                if temptup[0] == 0 : 
                    tkinter.messagebox.showinfo('Playlist is empty','Playlist is empty! Please insert a music.')
                
                #if playlist is not empty
                else: 

                    #get the playlist from database
                    for song in self.c.execute("SELECT Title from "+self.temptitle[tempint][0]): 

                        #store in playlist and in the listbox
                        self.pplaylist.append(song[0]+".mp3") 
                        self.listofsong.insert(0,song[0]) 
                    self.isPlaylist = True
                    pygame.mixer.music.load(self.pplaylist[self.index])

                    #set song name and artist
                    self.v = self.pplaylist[self.index].replace(".mp3","")
                    self.art = self.songinfo[self.index].get("Artist")
                    self.npplist = self.temptitle[tempint][0]  
                    self.ulen = len(str(self.npplist))
                    pygame.mixer.music.play()

                    #update the song name and artist on GUI
                    self.updatelabel()
                    self.updateartist()
                    self.displaylist.destroy()
                    self.MP3Win()

        
 #==================================================DISPLAY PLAYLIST=========================================================
    def editplay(self): 

        #get the picked playlist of the user
        self.tempstr = self.playlistbox.curselection()
        self.tempsongs = []

        #if user doesnt choose any
        if len(self.tempstr)==0: 
            tkinter.messagebox.showwarning("No Playlist","Please choose a playlist")
        else:

            #create window
            self.editp = Toplevel()
            self.editp.geometry("500x600+20+20")
            self.editp.title("Edit Playlist")
            self.editp.configure(background='black')

            #show the current songs of playlist
            self.crpl = Label(self.editp, text='Current Songs on Playlist', width=30,font=('cambria', 18,'bold'),background="DarkGoldenRod1").place(x=40,y=15)
            self.currentsongs = Listbox(self.editp, background='black',selectmode=MULTIPLE,fg = "DarkGoldenRod1", width=70)
            self.currentsongs.place(x=40,y=50)   

            #show all the available songs
            self.crpl = Label(self.editp, text='Available Songs', width=30,font=('cambria', 18,'bold'),background="DarkGoldenRod1").place(x=40,y=215)
            self.songs = Listbox(self.editp, background='black',selectmode=MULTIPLE,fg = "DarkGoldenRod1", width=70)
            self.songs.place(x=40,y=250)
            self.listofsongs.reverse()

            #transfer all songs in listbox
            for song in self.listofsongs: 
                self.songs.insert(0,song.replace(".mp3",""))
            self.listofsongs.reverse()
            tempint = self.tempstr[0]
            tempint-=1
            self.c.execute("SELECT COUNT(Title) from "+self.temptitle[tempint][0])
            templ = list(self.c)
            temptup = templ[0]
            if temptup[0] !=0:
                for song in self.c.execute("SELECT Title from "+self.temptitle[tempint][0]): #get the playlist from database
                    self.tempsongs.append(song[0])
                    self.currentsongs.insert(0,song[0])
            self.tempsongs.reverse()
            self.addsongs = Button(self.editp,text="Add to Playlist",font=('cambria',16,'bold'),width=20, background='DarkGoldenRod1', fg="black", command = self.addpl).place(x=130,y=430 )
            self.remsongs = Button(self.editp,text="Remove from Playlist",font=('cambria',16,'bold'),width=20, background='DarkGoldenRod1', fg="black", command = self.rempl).place(x=130,y=480 )
            self.done_btn = Button(self.editp,text="Done",font=('cambria',16,'bold'),width=20, background='DarkGoldenRod1', fg="black", command = self.des_edit).place(x=130,y=530)
    

    #destroy edit window
    def des_edit(self):
        self.editp.destroy()


    #add songs to playlist
    def addpl(self): 

        #get the picked song of user in listbox
        seltuple = self.songs.curselection()
        templists = list(seltuple)
        found = False
        for i in templists:
            #if song already exists on the playlist
            if self.listofsongs[i].replace(".mp3","") in self.tempsongs:
                found = True
        if found:
            tkinter.messagebox.showwarning("No Duplicate Song!","Song already exists in your playlist!")
        else:
            for i in templists:

                #if not exist on the playlist
                tempint = self.tempstr[0]
                tempint-=1  
                title = self.songinfo[i]["Title"]
                artist = self.songinfo[i]["Artist"]
                self.tempstr[0]

                #store the song on the database
                self.c.execute("INSERT INTO "+self.temptitle[tempint][0]+ " VALUES(?,?)",(title,artist))
                self.reopenpl()
                self.conn.commit()
            found = False
    
    #remove song sa playlist
    def rempl(self): 
        #get the picked playlist of user
        seltuple = self.currentsongs.curselection()
        tint = self.tempstr[0]
        tint-=1
        dtitle = self.temptitle[tint][0]
        templists = list(seltuple)
        if len(seltuple) ==0:
            tkinter.messagebox.showwarning("No song selected","Please select a song to remove")
        else:
            tempint = templists[0]
            tempint-=1
            self.tempsongs.reverse()
            #delete songs on the database
            self.tempsongs.reverse()
            for i in templists:
                self.c.execute("DELETE from "+dtitle+" WHERE Title = (?)",(self.tempsongs[i],))
                self.conn.commit()
            self.reopenpl()


    #reopen playlist
    def reopenpl(self):
        self.currentsongs.delete(0,END)
        self.tempsongs.clear()
        tempint = self.tempstr[0]
        tempint-=1
        for song in self.c.execute("SELECT Title from "+self.temptitle[tempint][0]):
            self.tempsongs.append(song[0])
            self.currentsongs.insert(0,song[0])
        self.tempsongs.reverse()


    #Create playlist
    def createplaylist(self):
        self.playlist = Toplevel()
        self.playlist.geometry("500x300+20+20")        
        self.playlist.title("Create Playlist")
        self.playlist.configure(background='black')
        self.playlisttitle = StringVar()
        # self.crpl = Label(self.playlist, text='Create Playlist', width=20,font=('cambria', 24,'bold'),background="DarkGoldenRod1").place(x=70,y=50)
        #Playlist Title 
        self.ptitle = Label(self.playlist, text='Playlist Title: ', width=30,font=('cambria',11,'bold'),background="DarkGoldenRod1").place(x=120,y=100)
        self.ptitleentry = Entry(self.playlist, width=40, textvar = self.playlisttitle,border=2).place(x=135,y=130)
        #List all playlist in a ListBox
        self.createbutton = Button(self.playlist, text ="Create Playlist",font=('cambria',16,'bold'), background='DarkGoldenRod1', fg="black", command = self.checkTableExists).place(x=180,y=200 )


    #remove playlist
    def removeplaylist(self):

        #get the picked playlist from user
        self.tempstr = self.playlistbox.curselection()
        if len(self.tempstr)==0: 
            tkinter.messagebox.showwarning("No Playlist","Please choose a playlist")
        else:
            tempint = self.tempstr[0]
            tempint-=1
            #drop the table for playlist 
            self.c.execute("DROP TABLE " + self.temptitle[tempint][0])

            #rermove the playlist from user
            self.c.execute("DELETE FROM UserPlaylist WHERE PlaylistTitle = ?", (self.temptitle[tempint][0],))
            self.conn.commit()
            tkinter.messagebox.showinfo("Playlist Deleted!","Playlist successfully deleted!")
            self.displaylist.destroy()
            self.displayplaylist()
    

    #check if playlist name is existing
    def checkTableExists(self):
        self.c.execute(''' SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{0}' '''.format(self.playlisttitle.get().replace('\'', '\'\'')))
        
        #if the count is 1, then table exists
        if self.c.fetchone()[0]==1 :
            tkinter.messagebox.showerror('Table exists','Table already exists!')

        #create playlist and store songs
        else:
            self.ctable_playlist()


    #create table for playlist in database
    def ctable_playlist(self):
        isSpace = False
        for i in self.playlisttitle.get():
            if i == " ":
                isSpace = True
        print(isSpace)
        if isSpace:
            tkinter.messagebox.showerror("SQL ERROR","Space is not allowed!")
        else:
            #create table
            self.c.execute("CREATE TABLE "+self.playlisttitle.get()+" (Title    VARCHAR NOT NULL UNIQUE, Artist VARCHAR NOT NULL,PRIMARY KEY(Title));")
            #insert the playlist from the user
            self.c.execute("INSERT INTO UserPlaylist (Username, PlaylistTitle) VALUES (?, ?)", (self.usern.get(),self.playlisttitle.get()))
            self.conn.commit()
            self.splaylist()
            self.itable_playlist()
        


    #store songs from the created playlist
    def itable_playlist(self):
        self.list1 = []
        self.playlist.destroy()

        #create window
        self.isongs = Toplevel()
        self.isongs.geometry("500x600+20+20")        
        self.isongs.title("Insert Songs")
        self.isongs.configure(background='black')

        #listbox for available songs 
        self.crpl = Label(self.isongs, text='Available Songs', width=30,font=('cambria', 18,'bold'),background="DarkGoldenRod1").place(x=40,y=15)
        self.listbox = Listbox(self.isongs,background='black',selectmode=MULTIPLE,fg = "DarkGoldenRod1", width=70)
        self.listbox.place(x=40,y=50)  
        self.listofsongs.reverse()

        #listbox for the songs on created playlist
        self.crpl = Label(self.isongs, text='Songs on Playlist', width=30,font=('cambria', 18,'bold'),background="DarkGoldenRod1").place(x=40,y=215)
        self.toinsert = Listbox(self.isongs,background='black',selectmode=MULTIPLE,fg = "DarkGoldenRod1", width=70)
        self.toinsert.place(x=40,y=250)

        #put the songs on the listbox
        for items in self.listofsongs:
            self.listbox.insert(0, items.replace(".mp3",""))
        self.listofsongs.reverse()
        self.insertbutton = Button(self.isongs, text ="Insert",font=('cambria',16,'bold'),width=20, background='DarkGoldenRod1', fg="black", command = self.insertList).place(x=130,y=430 )
 
        self.idbbutton = Button(self.isongs,text ="Done",font=('cambria',16,'bold'),width=20, background='DarkGoldenRod1', fg="black", command = self.insertdb).place(x=130,y=480 )

    
    #insert songs from playlist
    def insertList(self):

        #get the selected song of the user
        temptuple = self.listbox.curselection()
        templist = list(temptuple)

        #while not empty
        while len(templist)!=0:
            if self.listofsongs[templist[0]] in self.list1:
                print("Song already inserted!")
                break
            else:
                self.list1.append(self.listofsongs[templist[0]])
                self.toinsert.insert(0,self.listofsongs[templist[0]].replace(".mp3",""))
                templist.pop(0)
    
    
    #insert songs on database
    def insertdb(self):
        temptuple = self.toinsert.get(0,END)
        templist = list(temptuple)
        for song in templist:
            title=""
            artist=""
            for tempdict in self.songinfo:
                if tempdict["Title"] == song.replace(".mp3",""):
                    title = tempdict["Title"]
                    artist = tempdict["Artist"]
                    self.c.execute("INSERT INTO "+self.playlisttitle.get()+" VALUES (?, ?)", (title,artist))
                    self.conn.commit()
                    break
        self.isongs.destroy()


    def events(self):
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            #When clicked on play
            if event.type == pygame.MOUSEBUTTONDOWN and self.play_rect.collidepoint(event.pos):
                self.unpausesong()

            #When clicked on stop
            if event.type == pygame.MOUSEBUTTONDOWN and self.stop_rect.collidepoint(event.pos):
                self.stopsong()

            #When clicked on pause
            if event.type == pygame.MOUSEBUTTONDOWN and self.pause_rect.collidepoint(event.pos):
                self.pausesong()

            #When clicked on next
            if event.type == pygame.MOUSEBUTTONDOWN and self.nextbut_rect.collidepoint(event.pos):
                self.nextsong()

            #When clicked on replay
            if event.type == pygame.MOUSEBUTTONDOWN and self.reply_rect.collidepoint(event.pos):
                self.repeatsong() 

            #When clicked on exit
            if event.type == pygame.MOUSEBUTTONDOWN and self.exit_rect.collidepoint(event.pos):
                pygame.display.quit()
                self.displaylist.destroy()
                self.displayplaylist()

            #When clicked on previous
            if event.type == pygame.MOUSEBUTTONDOWN and self.prev_rect.collidepoint(event.pos):
                self.prevsong() 

            #When clicked on shuffle
            if event.type == pygame.MOUSEBUTTONDOWN and self.shuffle_rect.collidepoint(event.pos):
                self.shufflesong()  
            
            #When clicked on volume up
            if event.type == pygame.MOUSEBUTTONDOWN and self.volup_rect.collidepoint(event.pos):
                self.volume_up()

            #When clicked on volume down
            if event.type == pygame.MOUSEBUTTONDOWN and self.voldw_rect.collidepoint(event.pos):
                self.volume_down()


    #draw the image
    def load_vinyl(self):
        self.screen.blit(self.ui_vinyl,(self.Xcoord,self.Ycoord)) 

    #to draw the image
    def load_bg2(self):
        self.screen.blit(self.ui_bg2,(self.bg_Xcoord,self.bg_Ycoord)) 

    #to draw the image
    def load_play(self):
        self.screen.blit(self.ui_play,self.play_rect) 

    #to draw the image
    def load_stop(self):
        self.screen.blit(self.ui_stop,self.stop_rect) 

    #to draw the image
    def load_pause(self):
        self.screen.blit(self.ui_pause,self.pause_rect)

    #to draw the image
    def load_nextbut(self):
        self.screen.blit(self.ui_nextbut,self.nextbut_rect) 

    #to draw the image
    def load_reply(self):
        self.screen.blit(self.ui_reply,self.reply_rect) 

    #to draw the image
    def load_prev(self):
        self.screen.blit(self.ui_prev,self.prev_rect) 

    #to draw the image
    def load_shuffle(self):
        self.screen.blit(self.ui_shuffle,self.shuffle_rect) 

    #to draw the image
    def load_exit(self):
        self.screen.blit(self.ui_exit,self.exit_rect) 

    #to draw the image
    def load_volup(self):
        self.screen.blit(self.ui_volup,self.volup_rect) 

    #to draw the image
    def load_voldw(self):
        self.screen.blit(self.ui_voldw,self.voldw_rect) 
#=============================================================================================================================