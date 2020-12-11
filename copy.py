import socket
import select
import sys
import json
from chat_utils import *
import client_state_machine as csm
import tkinter as tk
from tkinter import Toplevel,Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button,StringVar, Message, messagebox,Listbox  # Tkinter Python Module for GUI
import tkinter.messagebox as msgbx
import time
import threading

class GUI:
    def __init__(self, args):
        # User(Client) Related
        self.peer = ''
        self.console_input = []
        self.state = S_OFFLINE
        self.system_msg = ''
        self.local_msg = ''
        self.peer_msg = ''
        self.args = args
        self.username = None


        # Window Related
        self.RootWindow = None
        self.LoginWindow = None
        self.mainWindow = None
        # StringVariable
        self.nameList = None
        self.search = None
        self.Time = None
        self.members = []
        # 接受的消息
        self.sendout = []
        self.selected_name=''
        # 发出的消息
        self.display = {}


    def quit(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def get_name(self):
        return self.name

    # 初始化
    def init_chat(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
        svr = SERVER if self.args.d == None else (self.args.d, CHAT_PORT)
        self.socket.connect(svr)
        self.sm = csm.ClientSM(self.socket)


    def send(self, msg):
        mysend(self.socket, msg)

    def recv(self):
        return myrecv(self.socket)

    def get_msgs(self):
        read, write, error = select.select([self.socket], [], [], 0)
        my_msg = ''
        peer_msg = []
        #peer_code = M_UNDEF    for json data, peer_code is redundant
        if len(self.sendout) > 0:
            my_msg = self.sendout.pop(0)
        if self.socket in read:
            peer_msg = self.recv()
        return my_msg, peer_msg

    def output(self):
        if len(self.display) > 0:
            print(type(self.display))
            print(type(self.display['typ']))
            typ = self.display['typ']
            value = self.display['value']
            print(typ,value)
            # MiddleFrame
            if typ == 'exchange':
                self.chat_transcript_area.insert('end',value+ '\n')

            elif typ == 'time':
                pass

            # LeftFrame
            elif typ == 'list':
                members = eval(value)
                for name in members.keys():
                    grp_key = members[name]
                    self.members.append( [ name, grp_key ] )
                    self.NameList.insert(END, name + " (group " + str(grp_key) + ")")

            elif typ == 'c':
                pass

            # RightFrame
            elif typ == '?':
                pass

            elif typ == "connect":
                self.chat_transcript_area.insert('end', value + '\n')

            # 只剩下p的情况
            else:
                # self.SearchResult.insert('end', self.display + '\n')
                lines = eval(value)
                for line in lines:
                    self.SearchResult.insert('end',line+ '\n')




    def login(self):
        # my_msg, peer_msg = self.get_msgs()
        userEntr = self.username.get()
        if len(userEntr) > 0:
            self.name = userEntr
            msg = json.dumps({"action":"login", "name":self.name})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.state = S_LOGGEDIN
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(self.name)
                self.print_instructions()
                return True
            elif response["status"] == 'duplicate':
                self.system_msg += 'Duplicate username, try again'
                return False
        else:               # fix: dup is only one of the reasons
           return False


    def read_input(self):
        while True:
            text = sys.stdin.readline()[:-1]
            self.console_input.append(text) # no need for lock, append is thread safe

    def print_instructions(self):
        self.system_msg += menu

    def guilogin(self):
        if self.login():
            msgbx.showinfo('Logged in.', 'Login Success')
            self.LoginWindow.destroy()
            self.openMainWindow()
        # further enhancement of handling sick login is needed
        elif self.login() == 'Duplicate':
            msgbx.showinfo('Error1', 'This Username already exists. Try another.')
        else:
            msgbx.showinfo('Error2', 'Invalid Input. Try Again.')

    #
    def run_chat(self):
        self.init_chat()
        self.RootWindow = Tk()
        self.RootWindow.geometry('0x0')
        self.RootWindow.resizable(0,0)
        self.openLoginWindow()
        self.RootWindow.mainloop()


    def openMainWindow(self):
        # if self.sm.get_state() != S_OFFLINE:
        #     self.proc()
        self.showMainWindow()
        reading_thread = threading.Thread(target=self.proc)
        reading_thread.daemon = False
        reading_thread.start()
        print("already here")
        # while self.login() != True:
        #     self.output()
        # self.output()
        # while self.sm.get_state() != S_OFFLINE:
        #     self.proc()
        #     self.output()
        #     time.sleep(CHAT_WAIT)
        # self.quit()
        print('finally works')

    def showMainWindow(self):
        # initialize MainWindow, defining it as a non-resizable Toplevel named 'Chatting'
        self.MainWindow = Toplevel(self.RootWindow)
        self.MainWindow.title("Chatting")
        self.MainWindow.geometry('960x600')
        self.MainWindow.resizable(0, 0)
        # display elements
        self.display_left_frame()
        self.display_middle_frame()
        self.display_right_frame()

    def display_left_frame(self):
        # Left Frame
        LeftFrame = Frame(self.MainWindow, height=600, width=200, bg="bisque2")
        LeftFrame.pack_propagate(0)

        # Leave Button
        btnLeave = Button(LeftFrame, text='Log Out', font=("Helvetica", 16), command=self.logout)
        btnLeave.pack(fill='both', pady=10, padx=6)

        # ShowTime & RefreshTime
        self.Time = StringVar()
        self.gettime()
        lblTime = Label(LeftFrame, textvariable=self.Time, font=("Helvetica", 16))
        lblTime.pack(fill='both', pady=10, padx=6)
        btnTime = Button(LeftFrame, text='Refresh Time', font=("Helvetica", 16), command=self.gettime)
        btnTime.pack(fill='both', side='top', padx=6)

        #  Name List
        NLFrame = Frame(LeftFrame)
        self.NameList = Listbox(NLFrame, selectmode='single')
        scrollbarName = Scrollbar(NLFrame, borderwidth=2, command=self.NameList.yview, orient=VERTICAL)
        self.NameList.config(yscrollcommand=scrollbarName.set)
        self.NameList.bind('<Double-1>', lambda x: self.newConnect())
        self.NameList.pack(side='left', padx=6, pady=12)
        scrollbarName.pack(side='right', padx=6, pady=10)
        btnRefresh = Button(LeftFrame, text='Refresh List', font=("Helvetica", 16), command=self.getlist)
        btnRefresh.pack(fill='both', padx=6, pady=10)
        # self.name_widget = Entry(LeftFrame, width=50, borderwidth=2)
        # self.name_widget.pack(side='left', anchor='e')
        # self.join_button = Button(frame, text="Join", width=10, command=self.on_join).pack(side='left')
        NLFrame.pack(side='top')
        LeftFrame.pack(side='left', padx=10, pady=5)

    def display_middle_frame(self):
        # middle frame
        MiddleFrame = Frame(self.MainWindow, height=600, width=400, bg="bisque2")
        MiddleFrame.pack_propagate(0)

        # label enjoy your chat
        LabelEnjoy = Label(MiddleFrame, text='Enjoy your chat!', font=("Helvetica", 16))
        LabelEnjoy.pack(fill='both', side='top', padx=6, pady=8)

        frmChat = Frame(MiddleFrame, height=300, width=400, bg="bisque2")
        frmChat.pack_propagate(0)
        frmChat.pack(side="top")

        self.chat_transcript_area = Text(frmChat, height=300, width=200, font=("Serif", 12))
        scrollbar = Scrollbar(frmChat, borderwidth=2, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        scrollbar.pack(side='right', fill='y', pady=8, padx=6)
        self.chat_transcript_area.pack(side='top', fill="y", padx=6, pady=8)


        # SEND instruction
        btnSend = Label(MiddleFrame, text='Press Enter to Send', font=("Helvetica", 16))
        btnSend.pack(fill='both', side='top', padx=6, pady=8)

        # Message entry
        self.enter_text_widget = Text(MiddleFrame, width=60, height=5, font=("Helvetica", 16))
        self.enter_text_widget.pack(side='top', padx=6, pady=10)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)

        # LeaveChat == 原先系统中用户输入"bye"的操作
        leaveChat = Button(MiddleFrame, text='Leave Conversation', font=("Helvetica", 16),
                           command=self.bye)
        leaveChat.pack(fill='both', side='top', padx=6, pady=10)
        MiddleFrame.pack(side='left', padx=6, pady=5)

    def display_right_frame(self):
        # Right Frame
        RightFrame = Frame(self.MainWindow, height=600, width=300, bg="bisque2")
        RightFrame.pack_propagate(0)

        # Welcome Message
        WelcomeStr = 'Welcome,' + self.name + '!'
        WelcomeLabel = Label(RightFrame, text=WelcomeStr, font=("Helvetica", 14))
        WelcomeLabel.pack(fill='both', padx=6, pady=10)
        RightFrame.pack(side='left', padx=10, pady=5)

        # instructionLabel
        InstructionStr = 'Enter a number to get a Sonnet'+'\n'+'OR Enter a word for chat history.'
        InstructionLabel = Label(RightFrame, text=InstructionStr, font=("Helvetica", 14))
        InstructionLabel.pack(fill='both', side='top', padx=5, pady=10)

        # Search Frame
        self.search = StringVar()
        SearchEnt = Entry(RightFrame,textvariable=self.search)
        SearchEnt.pack(side ='top',padx=5,pady=10)

        # Button Frame
        ButtonFrame = Frame(RightFrame,bg="bisque2")
        # Sonnet Button
        SonnetButton = Button(ButtonFrame,text='Get Sonnet!',command = self.getSonnet)
        SonnetButton.pack(side='left')
        # HisButton
        HisButton = Button(ButtonFrame, text='Search History',command=self.getSonnet)
        HisButton.pack(side='left')
        ButtonFrame.pack(side='top')
        # label "search result"
        SRLabel = Label(RightFrame, text='Here\'s the search result!', font=("Helvetica", 14))
        SRLabel.pack(fill='both', side='top', padx=6, pady=10)

        # SearchResult
        self.SearchResult = Text(RightFrame, width=30, height=20, font=("Serif", 12))
        scrollbarSearchResult = Scrollbar(RightFrame, borderwidth=2, command=self.NameList.yview, orient=VERTICAL)
        self.SearchResult.config(yscrollcommand=scrollbarSearchResult.set)
        self.SearchResult.bind('<KeyPress>', lambda e: 'break')
        scrollbarSearchResult.pack(side='right', fill='y', padx=6, pady=10)
        self.SearchResult.pack(side='top', padx=6, pady=12)



    def gettime(self):
        ctime = time.strftime('%m/%d,%H:%M', time.localtime())
        self.Time.set(ctime)

    def getlist(self):
        self.NameList.delete(0, 'end')
        request = "who"
        self.sendout = [request]
        print(self.sendout)

    def newConnect(self):
        # idx_selected_name = self.NameList.get(self.NameList.curselection())
        # self.selected_name = self.members[idx_selected_name[0]]
        selected = [self.NameList.get(x) for x in self.NameList.curselection()][0]
        self.selected_name = selected.split("(group")[0]
        my_msg = self.selected_name
        peer = my_msg[:]
        peer = peer.strip()
        sendout = "c" + peer
        if self.state == S_LOGGEDIN:
            self.sendout = [sendout]
            print(self.sendout)


    def bye(self):
        quit = msgbx.askyesno('Disconnect?','Do you really want to leave the conversation? The chat history will'
                                     'cleared.')
        if quit:
            self.sendout = ["bye"]
            self.chat_transcript_area.delete(1.0, 'end')

    def getSonnet(self):
        num = self.search.get()
        num = 'p'+num
        self.sendout = [num]
        print(self.sendout)



    def openLoginWindow(self):
        self.LoginWindow = Toplevel(self.RootWindow)
        self.LoginWindow.geometry('450x300')
        lblInstru = tk.Label(self.LoginWindow, text='Please enter your name')
        lblInstru.pack()
        self.username = tk.StringVar()
        entName = tk.Entry(self.LoginWindow, textvariable=self.username)
        entName.pack()
        btnLogin = tk.Button(self.LoginWindow, text='login', command=self.guilogin)
        btnLogin.pack()

    def logout(self):
        close = msgbx.askyesno('Quit?','Do you want to log off?')
        if close:
            self.MainWindow.destroy()
            self.quit()



    def on_enter_key_pressed(self,event):
        # if len(self.name_widget.get()) == 0:
        #     messagebox.showerror("Enter your name", "Enter your name to send a message")
        #     return
        self.send_chat()
        self.clear_text()

    def send_chat(self):
        # senders_name = self.name_widget.get().strip() + ": "
        chatInput = self.enter_text_widget.get(1.0, 'end').strip()
        message = ('['+self.name+']' + chatInput).encode('utf-8')
        self.chat_transcript_area.insert('end', message.decode('utf-8') + '\n')
        self.chat_transcript_area.yview(END)
        self.sendout = [chatInput]
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

        pass
    def setChatInstruction(self):
        pass

    def search(self):
        pass


#==============================================================================
# main processing loop
#==============================================================================
    def proc(self):
        while True:
            my_msg, peer_msg = self.get_msgs()
            self.display = self.sm.proc(my_msg, peer_msg)
            self.output()

            # time.sleep(CHAT_WAIT)
