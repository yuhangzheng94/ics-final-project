"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
        # #==============================================================================
        # # Once logged in, do a few things: get peer listing, connect, search
        # # And, of course, if you are so bored, just go
        # # This is event handling instate "S_LOGGEDIN"
#==============================================================================
        try:
            if my_msg[0] == 'p' and my_msg[1:].isdigit():
                # 用户再request 诗歌
                poem_idx = my_msg[1:].strip()
                mysend(self.s, json.dumps({"action": "poem", "target": poem_idx}))
                poem = json.loads(myrecv(self.s))["results"]
                print('have sent message')
                if (len(poem) > 0):
                    self.out_msg = {"typ": "poem", "value": poem}
                else:
                    self.out_msg = {"typ": "poem", "value": 'Invalid input! Try again.'}
                return self.out_msg
        except:
            pass

        # time

        try:
            if my_msg == 'time':
                mysend(self.s, json.dumps({"action": "time"}))
                time_in = json.loads(myrecv(self.s))["results"]
                self.out_msg += time_in
        except:
            pass
        # who

        try:
            if my_msg == 'who':
                mysend(self.s, json.dumps({"action": "list"}))
                members = json.loads(myrecv(self.s))["members"]
                print('have sent message: list')
                if len(members) > 0:
                    self.out_msg = {"typ": "list", "value": members}
                return self.out_msg
        except:
            pass


        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += time_in

                # elif my_msg == 'who':
                #     mysend(self.s, json.dumps({"action":"list"}))
                #     logged_in = json.loads(myrecv(self.s))["results"]
                #     self.out_msg += 'Here are all the users in the system:\n'
                #     self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    # 去除首尾空格
                    if self.connect_to(peer) == True:
                        # 如果我成功地与peer配对
                        self.state = S_CHATTING
                        self.out_msg = 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg = 'Connection unsuccessful\n'
                    dict_result = {"typ":"connect", "value": self.out_msg}
                    return dict_result

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    # 寻找"？后的message"
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = str(json.loads(myrecv(self.s))["results"]).strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                try:
                    peer_msg = json.loads(peer_msg)
                except Exception as err :
                    self.out_msg += " json.loads failed " + str(err)
                    return self.out_msg
            
                if peer_msg["action"] == "connect":
                    # ----------your code here------#
                    # 先确认我的status 如果我现在只是login，那么直接成组; 无需考虑成组的情况因为me的state是login不是chatting
                    self.state = S_CHATTING
                    value = 'You are connected with' + ' ' + peer_msg['from']
                    self.out_msg = {"typ": "c", "value":str(value)}
                    # ----------end of your code----#
                    
#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                # ----------your code here------#
                peer_msg = json.loads(peer_msg)
                """3 scenarios: 
                peer try to connect with me. 
                peer exchange msg with me. 
                peer disconnect and I am the only one left """
                if peer_msg['action'] == 'connect':
                    # 让我知道peer join了，并且让和我在同一个chat group的member知道peer join了,这个是server端的工作
                    value = peer_msg['from'] + ' '+ 'joined'
                    self.out_msg = {"typ": "c", "value":str(value)}

                if peer_msg['action'] == 'exchange':
                    value = '[' + peer_msg['from'] + ']:' + peer_msg['msg']
                    self.out_msg = {"typ": "exchange", "value": str(value)}

                if peer_msg['action']== 'disconnect':
                    value = peer_msg['msg']
                    self.out_msg = {"typ": "disconnect", "value": str(value)}
                    self.state = S_LOGGEDIN
                # ----------end of your code----#
                
            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state
#==============================================================================
        else:
            value =  'How did you wind up here??\n'
            self.out_msg = {"typ": "exchange", "value": str(value)}
            print_state(self.state)

        return self.out_msg
