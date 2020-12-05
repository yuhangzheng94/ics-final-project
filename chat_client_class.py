import socket
import select
import sys
import json
from chat_utils import *
import client_state_machine as csm
import tkinter as tk
import tkinter.messagebox as msgbx
from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button,StringVar, Message, messagebox  # Tkinter Python Module for GUI
import tkinter.messagebox as msgbx
import time
import threading



class MainWindow(Tk):
    def __init__(self):
        super().__init__()
        self.chat_transcript_area = None
        self.name_widget = None
        self.enter_text_widget = None
        self.join_button = None
        # str var
        self.nameList = None
        self.Time = None
        # self.initialize_socket()
        self.initialize_gui()
        self.mainWindow = None

        # self.listen_for_incoming_messages_in_a_thread()

    # def initialize_socket(self):
    #     self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # initialazing socket with TCP and IPv4
    #     remote_port = 10319  # TCP port
    #     self.client_socket.connect((remote_ip, remote_port))  # connect to the remote server




    def initialize_gui(self):  # GUI initializer
        self.title("Chatting")
        self.geometry('960x600')
        self.resizable(0, 0)
        self.display_left_frame()
        self.display_middle_frame()
        self.display_right_frame()

    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server,
                                  args=(self.client_socket,))  # Create a thread for the send and receive in same time
        thread.start()

    # function to recieve msg
    def receive_message_from_server(self, so):
        while True:
            buffer = so.recv(256)
            if not buffer:
                break
            message = buffer.decode('utf-8')

            if "joined" in message:
                user = message.split(":")[1]
                message = user + " has joined"
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
            else:
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)

        so.close()

    def display_left_frame(self):
        # Left Frame
        LeftFrame = Frame(height=600, width=200,  bg="bisque2")
        LeftFrame.pack_propagate(0)

        # Leave Button
        btnLeave = Button(LeftFrame, text='Log Out', font=("Helvetica", 16), command = self.logout)
        btnLeave.pack(fill='both', pady=10,padx=6)

        # ShowTime & RefreshTime
        self.Time = StringVar()
        self.Time.set('Show Time')
        btnTime = Button(LeftFrame, textvariable=self.Time,font=("Helvetica", 16),command = self.gettime)
        btnTime.pack(fill='both',pady=10,padx=6)
        btnTime = Button(LeftFrame, text='Refresh Time', font=("Helvetica", 16), command=self.gettime)
        btnTime.pack(fill='both', side='top', padx=6)

        #  Name List
        self.NameList = Text(LeftFrame, width=90, height=26, font=("Serif", 12))
        scrollbarName = Scrollbar(LeftFrame, borderwidth=2, command=self.NameList.yview, orient=VERTICAL)
        self.NameList.config(yscrollcommand=scrollbarName.set)
        self.NameList.bind('<KeyPress>', lambda e: 'break')
        scrollbarName.pack(side='right', fill='y',padx=6,pady=10)
        self.NameList.pack(side='top', padx=6, pady=12)
        # ----
        # self.nameList = StringVar()
        # MsgnameList = Message(LeftFrame,textvariable = self.nameList,font=("Helvetica", 16))
        # MsgnameList.pack(fill='both',padx=6,side='top')
        # ----
        btnRefresh = Button(LeftFrame,text='Refresh List',font=("Helvetica", 16),command = self.getlist)
        btnRefresh.pack(fill='both',padx=6,pady=10)
        # self.name_widget = Entry(LeftFrame, width=50, borderwidth=2)
        # self.name_widget.pack(side='left', anchor='e')
        # self.join_button = Button(frame, text="Join", width=10, command=self.on_join).pack(side='left')
        LeftFrame.pack(side='left',padx=10,pady=5)

    def display_middle_frame(self):
        # middle frame
        MiddleFrame = Frame(height=600, width='400',  bg="bisque2")
        MiddleFrame.pack_propagate(0)

        # label enjoy your chat
        LabelEnjoy = Label(MiddleFrame, text='Enjoy your chat!', font=("Helvetica", 16))
        LabelEnjoy.pack(fill='both', side='top', padx=6, pady=8)

        # display chat
        self.chat_transcript_area = Text(MiddleFrame, width=60, height=20, font=("Serif", 12))
        scrollbar = Scrollbar(MiddleFrame, borderwidth=2,command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        scrollbar.pack(side='right', fill='y',pady=8, padx=6)
        self.chat_transcript_area.pack(side='top', padx=6, pady=8)

        # SEND instruction
        btnSend = Label(MiddleFrame, text='Press Enter to Send', font=("Helvetica", 16))
        btnSend.pack(fill='both', side='top',padx=6, pady=8)

        # Message entry
        self.enter_text_widget = Text(MiddleFrame, width=60, height=5, font=("Helvetica", 16))
        self.enter_text_widget.pack(side='top', padx=6, pady=10)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        leaveChat = Button(MiddleFrame, text='Leave Conversation', font=("Helvetica", 16),command=self.setChatInstruction)
        leaveChat.pack(fill='both',side='top',padx=6,pady=10)
        MiddleFrame.pack(side='left', padx=6, pady=5)



    def display_right_frame(self):
        # Right Frame
        RightFrame = Frame(height=600, width=300,  bg="bisque2")
        RightFrame.pack_propagate(0)

        # Welcome Message
        WelcomeStr = 'Welcome,'+'TBC'+'!'
        WelcomeLabel = Label(RightFrame,text=WelcomeStr,font=("Helvetica", 14))
        WelcomeLabel.pack(fill='both',padx=6,pady=10)
        RightFrame.pack(side='left', padx=10, pady=5)

        # sonnet
        SonnetStr = 'Enter a number to get a Sonnet'
        SonnetLabel = Label(RightFrame,text=SonnetStr,font=("Helvetica", 14))
        SonnetLabel.pack(fill='both',side='top',padx=5,pady=10)
        SonnetEnt = Entry(RightFrame)
        SonnetEnt.pack(fill='both',side='top',padx=6,pady=10)

        # search chat history
        CHStr = 'Enter a word to get Chat History'
        CHLabel = Label(RightFrame, text=CHStr, font=("Helvetica", 14))
        CHLabel.pack(fill='both',side='top', padx=5, pady=10)
        CHEnt = Entry(RightFrame)
        CHEnt.pack(fill='both',side='top', padx=6, pady=10)

        # search button
        search = Button(RightFrame, text='Go',font=("Helvetica", 16),command=self.search)
        search.pack(fill='both',side='top',padx=6,pady=10)

        # label "search result"
        SRLabel = Label(RightFrame, text='Here\'s the search result!', font=("Helvetica", 14))
        SRLabel.pack(fill='both',side='top', padx=6, pady=10)

        # SearchResult
        self.SearchResult = Text(RightFrame, width=30, height=20, font=("Serif", 12))
        scrollbarSearchResult = Scrollbar(RightFrame, borderwidth=2, command=self.NameList.yview, orient=VERTICAL)
        self.SearchResult.config(yscrollcommand=scrollbarSearchResult.set)
        self.SearchResult.bind('<KeyPress>', lambda e: 'break')
        scrollbarSearchResult.pack(side='right', fill='y', padx=6, pady=10)
        self.SearchResult.pack(side='top', padx=6, pady=12)




        # Label(RightFrame, text='Chat Box:', font=("Serif", 12).pack(side='top', anchor='w')
        # self.chat_transcript_area = Text(frame, width=60, height=10, font=("Serif", 12))
        # scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        # self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        # self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        # self.chat_transcript_area.pack(side='left', padx=10)
        # scrollbar.pack(side='right', fill='y')


    def display_chat_entry_box(self):
        frame = Frame()
        Label(frame, text='Enter message:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.enter_text_widget = Text(frame, width=60, height=3, font=("Serif", 12))
        self.enter_text_widget.pack(side='left', pady=15)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.pack(side='top')

    def on_join(self):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return
        self.name_widget.config(state='disabled')
        self.client_socket.send(("joined:" + self.name_widget.get()).encode('utf-8'))

    def on_enter_key_pressed(self, event):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror("Enter your name", "Enter your name to send a message")
            return
        self.send_chat()
        self.clear_text()

    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self):
        senders_name = self.name_widget.get().strip() + ": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        message = (senders_name + data).encode('utf-8')
        self.chat_transcript_area.insert('end', message.decode('utf-8') + '\n')
        self.chat_transcript_area.yview(END)
        self.client_socket.send(message)
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    # Left
    # 已经可以实现关窗口前出现弹窗确认
    def logout(self):
        close = msgbx.askyesno('','Do you want to log out?')
        if close:
            self.destroy()
    # Q: differences between close, distroy, withdraw?

    def gettime(self):
        ctime = time.strftime('%m/%d,%H:%M', time.localtime())
        self.Time.set(ctime)

    def getlist(self):
        pass

    # Middel
    def send(self):
        pass

    def setChatInstruction(self):
        msgbox.askyesno(' ','Quit Conversation?')

    # Right
    def search(self):
        pass


    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            self.client_socket.close()
            exit(0)

class Client:
    def __init__(self, args):
        self.peer = ''
        self.console_input = []
        self.state = S_OFFLINE
        self.system_msg = ''
        self.local_msg = ''
        self.peer_msg = ''
        self.args = args
        self.username = None
        self.RootWindow= None
        self.LoginWindow=None
        self.MainWindow = None


    def quit(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def get_name(self):
        return self.name

    def init_chat(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
        svr = SERVER if self.args.d == None else (self.args.d, CHAT_PORT)
        self.socket.connect(svr)
        self.sm = csm.ClientSM(self.socket)
        reading_thread = threading.Thread(target=self.read_input)
        reading_thread.daemon = True
        reading_thread.start()

    def shutdown_chat(self):
        return

    def send(self, msg):
        mysend(self.socket, msg)

    def recv(self):
        return myrecv(self.socket)

    def get_msgs(self):
        read, write, error = select.select([self.socket], [], [], 0)
        my_msg = ''
        peer_msg = []
        #peer_code = M_UNDEF    for json data, peer_code is redundant
        if len(self.console_input) > 0:
            my_msg = self.console_input.pop(0)
        if self.socket in read:
            peer_msg = self.recv()
        return my_msg, peer_msg

    def output(self):
        if len(self.system_msg) > 0:
            print(self.system_msg)
            self.system_msg = ''

    def login(self):
        # my_msg, peer_msg = self.get_msgs()
        userEntr = self.username.get()
        if len(userEntr) > 0:
            self.name = userEntr
            msg = json.dumps({"action":"login", "name": self.name})
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
        if self.login:
            msgbx.showinfo('Logged in.','Login Success')
            self.LoginWindow.destroy()
        elif self.login == 'Duplicate':
            msgbx.showinfo('Error1','This Username already exists. Try another.')
        else:
            msgbx.showinfo('Error2','Invalid Input. Try Again.')


    def run_chat(self):
        self.init_chat()
        self.RootWindow = tk.Tk()
        self.RootWindow.geometry('1x1')
        self.LoginWindow = tk.Tk()
        self.LoginWindow.master = self.RootWindow
        self.LoginWindow.geometry('450x300')
        lblInstru = tk.Label(self.LoginWindow,text='Please enter your name')
        lblInstru.pack()
        self.username=tk.StringVar()
        entName = tk.Entry(self.LoginWindow,textvariable=self.username)
        entName.pack()
        btnLogin=tk.Button(self.LoginWindow,text='login',command=self.guilogin)
        btnLogin.pack()
        self.RootWindow.mainloop()


    def openMainWindow(self):
        if self.sm.get_state() != S_OFFLINE:
            self.proc()
        mainWindow = MainWindow()
        print('haha')
        while self.login() != True:
            self.output()
        self.output()
        while self.sm.get_state() != S_OFFLINE:
            self.proc()
            self.output()
            time.sleep(CHAT_WAIT)
        self.quit()
        mainWindow.mainloop()







#==============================================================================
# main processing loop
#==============================================================================
    def proc(self):
        my_msg, peer_msg = self.get_msgs()
        self.system_msg += self.sm.proc(my_msg, peer_msg)
