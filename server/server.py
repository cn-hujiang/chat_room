import time
import pymysql
from socket import *
from multiprocessing import *

import db_handler as db
from db_handler import *
from f_weather import *


class TCPServer:
    def __init__(self):
        self.sockfd = socket()
        self.ADDR = ('localhost', 8888)
        self.sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sockfd.bind(self.ADDR)
        self.sockfd.listen(5)

    def accept(self):
        self.connfd, self.c_addr = self.sockfd.accept()
        print('连接自客户端', self.c_addr)
        return self.connfd, self.c_addr

    def send(self, msg):
        self.connfd.send(msg.encode())

    def recv(self, size=1024):
        return self.connfd.recv(size).decode()


def connfdAcceptHandler(s, msgQue):
    while True:
        try:
            recvMsg = s.recv()
            if not recvMsg:
                continue
        except Exception as e:
            print(e)
        # print('来自服务端msgHandler{}'.format(recvMsg))
        if recvMsg.split('//#//')[0] == '101':
            msg = ['101', s, recvMsg.split('//#//')[1], recvMsg.split('//#//')[2]]
            msgQue.put(msg)
        elif recvMsg.split('//#//')[0] == '102':
            msg = ['102', s, recvMsg.split('//#//')[1], recvMsg.split('//#//')[2]]
            msgQue.put(msg)
        elif recvMsg.split('//#//')[0] == '200':
            msg = ['200', s, recvMsg.split('//#//')[1]]
            msgQue.put(msg)
        elif recvMsg.split('//#//')[0] == '201':
            msg = ['201', s, recvMsg.split('//#//')[1]]
            msgQue.put(msg)
        elif recvMsg.split('//#//')[0] == '202':
            msg = ['202', s, recvMsg.split('//#//')[1], recvMsg.split('//#//')[2]]
            msgQue.put(msg)
        elif recvMsg.split('//#//')[0] == '203':
            msg = ['203', s, recvMsg.split('//#//')[1]]
            msgQue.put(msg)
        elif recvMsg.split('//#//')[0] == '301':
            msg = ['301', s, recvMsg.split('//#//')[1], recvMsg.split('//#//')[2], recvMsg.split('//#//')[3]]
            msgQue.put(msg)
        elif recvMsg.split('//#//')[0] == '401':
            msg = ['401', s, recvMsg.split('//#//')[1], recvMsg.split('//#//')[2]]
            msgQue.put(msg)


def msgRecvHandler(msgQue, db_operator):
    onlineUser = []
    while True:
        msg = []
        for i in onlineUser:
            try:
                i[1].send('&*^@@^*&')
            except Exception:
                print('{} 已下线'.format(i[0]))
                onlineUser.remove(i)
                for j in onlineUser:
                    j[1].send('201//#//{}//#//{}'.format(i[0], str([n[0] for n in onlineUser])))
        try:
            msg = msgQue.get(True, 1)
        except Exception as e:
            pass
        # print(e)
        if not msg:
            pass
        elif msg[0] == '101':
            s, username, passwd = msg[1], msg[2], msg[3]
            flag = db_operator.login_check(username, passwd)
            if flag == 'NG' or flag is None:
                s.send('104')
                print('{}请求登录失败'.format(s.c_addr))
            elif flag == 'OK':
                s.send('103')
                time.sleep(0.1)
                onlineUser.append([username, s])
                print('{}上线了'.format(username))
                for i in onlineUser:
                    i[1].send('200//#//{}//#//{}'.format(username, str([i[0] for i in onlineUser])))
        elif msg[0] == '102':
            s, username, passwd = msg[1], msg[2], msg[3]
            flag = db_operator.register(username, passwd)
            if flag == "NAMEEXIST":
                s.send('106')
                print('{}注册失败,原因:用户名重复'.format(s.c_addr))
            elif flag == "OK":
                s.send('105')
                print('{}注册成功'.format(username))
            elif flag == "NG":
                s.send('107')
                print('{} 注册失败'.format(s.c_addr))
        elif msg[0] == '201':
            print('{} 已下线'.format(msg[2]))
            # print(onlineUser)
            for i in onlineUser:
                if i[0] == msg[2]:
                    onlineUser.remove(i)
                    break
            for i in onlineUser:
                i[1].send('201//#//{}//#//{}'.format(msg[2], str([i[0] for i in onlineUser])))
        elif msg[0] == '202':
            flag = db_operator.save_room_msg(msg[2], msg[3], "sys_chatroom")
            if flag == "OK":
                print("聊天室消息已存入数据库！")
            elif flag == "NG":
                print("聊天室消息存储失败！")
            for i in onlineUser:
                i[1].send('202//#//{}//#//{}'.format(msg[2], msg[3]))
        elif msg[0] == '203':
            print('{} 查询群聊历史记录'.format(msg[2]))
            flag = db_operator.get_room_msg("sys_chatroom", 100)
            msg1 = ''
            for i in flag:
                u, m, t = i
                msg1 += '{}  {}\n{}\n'.format(u, t, m)
            s.send('203//#//{}'.format(msg1))
        elif msg[0] == '301':
            userSock = msg[1]
            sname = msg[2]
            rname = msg[3]
            msg1 = msg[4]
            # userSock.send('301//#//{}//#//{}'.format(sname, msg1))
            for i in onlineUser:
                if i[0] == rname:
                    recvSock = i[1]
                    break
            recvSock.send('301//#//{}//#//{}'.format(sname, msg1))
            if db_operator.save_msg(sname, rname, 1, msg1) == 'OK':
                print('私聊消息存储成功')
        elif msg[0] == '401':
            s, username, city = msg[1], msg[2], msg[3]
            print('{}查询{}天气'.format(username, city))
            weather = weather_info(city)
            s.send('401//#//{}'.format(weather))


s = TCPServer()
db_operator = db.DB_Handler()
db_operator.create_chatroom("sys_chatroom")
msgQue = Queue()
p_msgRecv = Process(target=msgRecvHandler, args=(msgQue, db_operator))
p_msgRecv.daemon = True
p_msgRecv.start()

while True:
    s.accept()
    p_connfdAccept = Process(target=connfdAcceptHandler,
                             args=(s, msgQue))
    p_connfdAccept.daemon = True
    p_connfdAccept.start()
