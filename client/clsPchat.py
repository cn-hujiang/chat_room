from tkinter import *
from tkinter.scrolledtext import ScrolledText


class Pchat:
    def __init__(self, username, fname, master=None, s=None):
        self.root = master
        self.username = username
        self.s = s
        self.fname = fname
        self.creatPage()

    def creatPage(self):
        self.root.resizable(False, False)
        self.root.title('正在与{}聊天'.format(self.fname))
        fr = Frame(self.root, bg='grey')
        fr.grid()
        self.st1 = ScrolledText(fr, height=25, width=70, bg='white')
        self.st1.grid(row=0, padx=6, pady=6)
        self.st1.config(state=DISABLED)
        self.st2 = ScrolledText(fr, height=15, width=70, bg='white')
        self.st2.grid(row=1, padx=6, pady=6)
        btFrm1 = Frame(fr, bg='grey')
        btFrm1.grid(row=2, sticky=W + E)
        bt = Button(btFrm1, text='history', height=1, width=7)
        bt.grid(row=0, column=0, padx=10, pady=6, sticky=W)
        bt1 = Button(btFrm1, text='send', command=self.sendMsg, height=1, width=4)

        def sendMsgEvent(event):
            if event.keysym == 'Return':
                self.sendMsg()

        self.st2.bind('<KeyPress-Return>', sendMsgEvent)
        Label(btFrm1, bg='grey', width=50).grid(row=0, column=1)
        bt1.grid(row=0, column=2, padx=10, pady=6, sticky=E)

    def sendMsg(self):
        msg = self.st2.get(0.0, END).strip('\n')
        self.st2.delete(0.0, END)
        self.st2.mark_set('insert', '0.0')


root = Tk()
user1 = Pchat('user1', 'user2', root)
root.mainloop()
