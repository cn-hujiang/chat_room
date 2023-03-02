from socket import *
from select import *
from multiprocessing import *
# from threading import *
from tkinter import *
from tkinter.messagebox import *
from tkinter.scrolledtext import ScrolledText

from MainPage import *


class LoginPage:
    def __init__(self, master=None):
        self.root = master
        self.root.resizable(False, False)
        self.username = StringVar()
        self.password = StringVar()
        self.loginQue = Queue()
        self.chatroomQue = Queue()
        self.weatherQue = Queue()
        self.historyQue = Queue()
        self.pchatQue = Queue()
        self.creatPage()
        self.s = socket()
        try:
            self.s.connect(('localhost', 8888))
        except Exception as e:
            showerror(title='连接失败', message='服务器错误,{}'.format(e))
        self.msgRecv()

    def msgRecv(self):
        def msgRecvHandler():
            p = poll()
            p.register(self.s, POLLIN)
            while True:
                events = p.poll()
                for fd, event in events:
                    if fd == self.s.fileno() and event is POLLIN:
                        recvMsg = self.s.recv(4096).decode().strip('&*^@@^*&').split('//#//')
                        # print('来自客户端msgHandler{}'.format(recvMsg))
                        if not recvMsg:
                            pass
                        elif recvMsg[0] in ['103', '104', '105', '106', '107']:
                            self.loginQue.put(recvMsg)
                        elif recvMsg[0] in ['200', '201']:
                            self.chatroomQue.put(recvMsg)
                        elif recvMsg[0] == '202':
                            self.chatroomQue.put(['202', recvMsg[1], recvMsg[2]])
                        elif recvMsg[0] == '203':
                            self.historyQue.put(recvMsg)
                        elif recvMsg[0] == '301':
                            self.pchatQue.put(recvMsg)
                        elif recvMsg[0] == '401':
                            self.weatherQue.put(recvMsg)

        p = Process(target=msgRecvHandler)
        p.daemon = True
        p.start()

    def creatPage(self):
        self.root.title('用户登录')
        fr1 = Frame(self.root, bg='white')
        fr1.grid()

        img = PhotoImage(file='./logo.gif')
        imgLb = Label(fr1, image=img, bg='white', width=400, height=150)
        imgLb.img = img
        imgLb.grid(row=0, column=0, columnspan=2)

        Label(fr1, text='请输入用户名:', bg='white').grid(row=1, column=0, pady=8, sticky=E)
        Entry(fr1, textvariable=self.username).grid(row=1, column=1, pady=8, sticky=W)
        Label(fr1, text='请输入密码:', bg='white').grid(row=2, column=0, sticky=E)
        pwdEtry = Entry(fr1, textvariable=self.password, show='*')
        pwdEtry.grid(row=2, column=1, sticky=W)

        fr2 = Frame(self.root, bg='white')
        fr2.grid(row=3, column=0, columnspan=2, sticky=N + E + W)
        Label(fr2, width=15, bg='white').grid(row=0, column=0)
        Button(fr2, text='登录', command=lambda: self.login(fr1, fr2)).grid(row=0, column=1, pady=8)
        Label(fr2, width=10, bg='white').grid(row=0, column=2)
        Button(fr2, text='注册', command=self.regist).grid(row=0, column=3, pady=8)

        def loginEve(event):
            if event.keysym == 'Return':
                self.login(fr1, fr2)

        pwdEtry.bind('<KeyPress-Return>', loginEve)

    def login(self, fr1, fr2):
        username = self.username.get()
        self.s.send('101//#//{}//#//{}'.format(self.username.get(), self.password.get()).encode())
        msg = self.loginQue.get()
        if msg[0] == '103':
            fr1.destroy()
            fr2.destroy()
            MainPage(root, self.username.get(), self.s, self.chatroomQue, self.weatherQue, self.historyQue,
                     self.pchatQue)
        elif msg[0] == '104':
            showerror(title='错误', message='用户名或密码有误,请重新登录')

    def regist(self):
        uname = StringVar()
        pwd = StringVar()
        pwd1 = StringVar()

        registPage = Toplevel()
        registPage.title('注册新用户')
        fr3 = Frame(registPage, bg='white')
        fr3.grid()

        img = PhotoImage(file='./logo.gif')
        imgLb = Label(fr3, image=img, bg='white', width=400, height=150)
        imgLb.img = img
        imgLb.grid(row=0, column=0, columnspan=2)

        Label(fr3, text='请输入用户名:', bg='white').grid(row=1, pady=10, stick=E)
        Entry(fr3, textvariable=uname).grid(row=1, column=1, stick=W)
        Label(fr3, text='请输入密码:', bg='white').grid(row=2, pady=10, stick=E)
        Entry(fr3, textvariable=pwd, show='*').grid(row=2, column=1, stick=W)
        bt = Label(fr3, text='请再次输入密码:', bg='white')
        bt.grid(row=3, pady=10, stick=E)
        Entry(fr3, textvariable=pwd1, show='*').grid(row=3, column=1, stick=W)
        Button(fr3, text='注册',
               command=lambda: self.registConfirm(registPage, uname.get(), pwd.get(), pwd1.get())).grid(row=4, column=1,
                                                                                                        pady=20,
                                                                                                        stick=W)

        def rgEve(event):
            if event.keysym == 'Return':
                self.registConfirm()

        bt.bind('<KeyPress-Return>', rgEve)

    def registConfirm(self, registPage, uname, pwd, pwd1):
        if pwd != pwd1:
            showerror(title='注册失败', message='两次输入的密码不一致!')
            return
        elif not uname or not pwd or not pwd1:
            showerror(title='注册失败', message='输入的内容不能为空!')
            return
        elif (' ' in uname) or (' ' in pwd) or (' ' in pwd1):
            showerror(title='注册失败', message='账户密码不能有空格!')
            return
        self.s.send('102//#//{}//#//{}'.format(uname, pwd).encode())
        msg = self.loginQue.get()
        if msg[0] == '105':
            showinfo(title='注册成功', message='注册成功')
            registPage.destroy()
        elif msg[0] == '106':
            showerror(title='注册失败', message='该用户已存在')
        elif msg[0] == '107':
            showerror(title='注册失败', message='注册失败')


root = Tk()
LoginPage(root)
root.mainloop()
