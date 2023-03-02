import time
import sys
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import *


class MainPage:
    def __init__(self, master, username, s, chatroomQue, weatherQue, historyQue, pchatQue):
        self.root = master
        self.username = username
        self.s = s
        self.chatroomQue = chatroomQue
        self.pchatQue = pchatQue
        self.weatherQue = weatherQue
        self.historyQue = historyQue
        self.pchatDict = {}
        self.root.resizable(False, False)
        self.creatPage()

    def creatPage(self):
        self.root.title('网络聊天室')
        fr = Frame(self.root, bg='grey')
        fr.grid()
        st = ScrolledText(fr, height=25, width=55, bg='white')
        st.grid(row=0, column=0, padx=8, pady=4, sticky=W)
        st.config(state=DISABLED)
        tx = ScrolledText(fr, height=15, width=55, bg='white')
        tx.grid(row=1, column=0, padx=8, pady=2, sticky=W)
        btFrm = Frame(fr, bg='grey')
        btFrm.grid(row=2, sticky=W, padx=8, pady=4)
        bt1 = Button(btFrm, text='history', command=lambda: self.msgHistory('聊天室历史记录'), justify=LEFT, height=1, width=7)
        bt1.grid(row=0, column=0, sticky=W)
        bt2 = Button(btFrm, text='weather', command=self.weather, justify=LEFT, height=1, width=5)
        bt2.grid(row=0, column=1, sticky=W)

        def logout():
            print('点击关闭')
            self.s.send('201//#//{}'.format(self.username).encode())
            sys.exit('客户端退出')

        bt6 = Button(btFrm, text='log out', command=logout, height=1, width=7)
        bt6.grid(row=0, column=2, sticky=W)

        def sendMsg():
            msg = tx.get(0.0, END).strip('\n')
            self.s.send('202//#//{}//#//{}'.format(self.username, msg).encode())
            tx.delete(0.0, END)
            tx.mark_set('insert', '0.0')

        def sendMsgEvent(event):
            if event.keysym == 'Return':
                sendMsg()

        tx.bind('<KeyPress-Return>', sendMsgEvent)
        bt3 = Button(btFrm, text='send', command=sendMsg, justify=RIGHT, height=1, width=4)
        Label(btFrm, bg='grey', width=16).grid(row=0, column=3)
        bt3.grid(row=0, column=4, sticky=E, padx=8)
        fr1 = Frame(fr, bg='grey')
        fr1.grid(row=0, column=1, rowspan=2, padx=4, sticky=N + S)
        Label(fr1, bg='grey', text='Online User:', justify=LEFT).grid(row=0, sticky=W)
        member_lst = StringVar()
        self.lst = Listbox(fr1, height=29, listvariable=member_lst)
        self.lst.grid(row=1, sticky=N + S)
        self.lst.bind('<Double-Button-1>', self.pchat)
        self.root.protocol("WM_DELETE_WINDOW", logout)

        def msgShow():
            try:
                msg, msg1 = '', ''
                msg = self.chatroomQue.get(0)
                print('来自chatroomQue队列消息出口{}'.format(msg))
                st.config(state=NORMAL)
            except Exception:
                pass
            if not msg:
                pass
            elif msg[0] == '200':
                msg1 = '{} 进入聊天室\n'.format(msg[1])
                st.insert(END, msg1)
                member_lst.set(tuple(eval(msg[2])))
            elif msg[0] == '201':
                msg1 = '{} 退出聊天室\n'.format(msg[1])
                st.insert(END, msg1)
                member_lst.set(tuple(eval(msg[2])))
            elif msg[0] == '202':
                t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                msg1 = '{}:    {}\n{}\n'.format(msg[1], t, msg[2])
                st.insert(END, msg1)
            st.see(END)
            st.config(state=DISABLED)

            try:
                msg, msg1 = '', ''
                msg = self.pchatQue.get(0)
                print('来自pchatQue队列消息出口{}'.format(msg))
            except Exception:
                pass
            if not msg:
                pass
            elif msg[0] == '301':
                if msg[1] in self.pchatDict:
                    print(self.pchatDict)
                    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    msg1 = '{}:    {}\n{}\n'.format(msg[1], t, msg[2])
                    self.pchatDict[msg[1]].insert(END, msg1)
                else:
                    self.pchat(name=msg[1])
                    self.pchatQue.put(msg)
            self.root.after(100, msgShow)

        msgShow()

    def weather(self):
        top = Toplevel()
        top.resizable(False, False)
        top.title('天气查询')
        Label(top, text='请输入要查询的城市(拼音):').grid(row=0, column=0, padx=8, pady=4)
        city = StringVar()
        cityEn = Entry(top, textvariable=city, width=20)
        cityEn.grid(row=0, column=1, padx=8, pady=4)

        def inquery():
            try:
                tx2.delete(0.0, END)
            except Exception:
                pass
            ctyName = city.get()
            cityEn.delete(0, END)
            tx2 = ScrolledText(top, height=20, width=40, bg='white')
            tx2.grid(row=2, column=0, columnspan=2, pady=8, padx=8)
            tx2.delete(0.0, END)
            tx2.insert(END, '正在查询 {} 天气...'.format(ctyName))
            self.s.send('401//#//{}//#//{}'.format(self.username, ctyName).encode())
            recvMsg = self.weatherQue.get()
            weatherInfo = recvMsg[1]
            tx2.delete(0.0, END)
            tx2.insert(END, weatherInfo)
            tx2.config(state=DISABLED)

        bt4 = Button(top, text='inquery', command=inquery, height=1, width=7)

        def inqueryEve(event):
            if event.keysym == 'Return':
                inquery()

        cityEn.bind('<KeyPress-Return>', inqueryEve)
        bt4.grid(row=1, column=0, columnspan=2, pady=4)

    def msgHistory(self, name):
        top1 = Toplevel()
        top1.resizable(False, False)
        top1.title(name)
        st1 = ScrolledText(top1, height=35, width=55, bg='white')
        st1.config(state=DISABLED)
        st1.grid(padx=8, pady=4, row=0)

        def ext():
            top1.destroy()

        bt5 = Button(top1, text='exit', height=1, width=4, command=ext)
        bt5.grid(row=1, padx=8, pady=4)
        self.s.send('203//#//{}'.format(self.username).encode())
        recvMsg = self.historyQue.get()
        st1.config(state=NORMAL)
        st1.insert(END, recvMsg[1])
        st1.config(state=DISABLED)

    def pchat(self, event=None, name=None):
        top2 = Toplevel()
        top2.resizable(False, False)
        if not name:
            name = self.lst.get(self.lst.curselection())
        top2.title('正在与{}聊天'.format(name))
        fr2 = Frame(top2, bg='grey')
        fr2.grid()
        st1 = ScrolledText(fr2, height=25, width=70, bg='white')
        st1.grid(row=0, padx=6, pady=6)
        # st1.config(state = DISABLED)
        tx1 = ScrolledText(fr2, height=15, width=70, bg='white')
        tx1.grid(row=1, padx=6, pady=6)
        btFrm1 = Frame(fr2, bg='grey')
        btFrm1.grid(row=2, sticky=W + E)
        bt8 = Button(btFrm1, text='history', command=lambda: self.msgHistory('与{}的聊天记录'.format(name)), height=1,
                     width=7)
        bt8.grid(row=0, column=0, padx=10, pady=6, sticky=W)

        def sendMsg():
            msg = tx1.get(0.0, END).strip('\n')
            self.s.send('301//#//{}//#//{}//#//{}'.format(self.username, name, msg).encode())
            tx1.delete(0.0, END)
            tx1.mark_set('insert', '0.0')
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            msg1 = '{}:    {}\n{}\n'.format(self.username, t, msg)
            st1.insert(END, msg1)

        def sendMsgEvent(event):
            if event.keysym == 'Return':
                sendMsg()

        tx1.bind('<KeyPress-Return>', sendMsgEvent)
        bt7 = Button(btFrm1, text='send', command=sendMsg, height=1, width=4)
        Label(btFrm1, bg='grey', width=50).grid(row=0, column=1)
        bt7.grid(row=0, column=2, padx=10, pady=6, sticky=E)

        def wincls():
            del self.pchatDict[name]
            top2.destroy()

        top2.protocol("WM_DELETE_WINDOW", wincls)
        self.pchatDict[name] = st1
