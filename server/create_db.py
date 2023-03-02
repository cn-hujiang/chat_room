'''
python3 create_db.py 1 创建数据库及数据表
python3 create_db.py ２　试着插入几条用户记录
    username = ["admin", "limuxia", "tommy", "abc"]
    password = ["123", "123", "123", "123"]
    nickname = ["管理员", "muxia", "TOMMY", "abc"]
'''

import pymysql


# import sys

class DB_Creater(object):
    def __init__(self):
        self.local = 'localhost'
        self.db_login_name = 'root'
        self.db_login_pswd = '123456'
        self.userinfo = "userinfo"
        self.chatmsg = "chatmsg"
        self.userfriend = "userfriend"
        self.chatroom = "chatroom"
        self.chatroomuser = "chatroom_user"

    def connect_to_DB(self, sql_statment, db=None):
        '''执行SQL语句'''
        self.db = db
        _ = None
        db_conn = pymysql.connect(self.local,
                                  self.db_login_name,
                                  self.db_login_pswd,
                                  charset='utf8')
        cursor = db_conn.cursor()
        if self.db is not None:
            cursor.execute("use %s" % self.db)
        try:
            cursor.execute(sql_statment)
            db_conn.commit()
            _ = 'OK'
        except Exception as e:
            db_conn.rollback()
            print(e)
            _ = "NG"
        cursor.close()
        db_conn.close()
        return _

    def do_create(self):
        cdsql = 'create database chatroom;'
        ctsql1 = '''create table userinfo(
                    id int primary key auto_increment,
                    username varchar(50) unique not null,
                    password varchar(254) not null,
                    reg_time timestamp not null,
                    isActive boolean not null)default charset=utf8;
                 '''
        ctsql2 = '''create table chatmsg(
                    id int primary key auto_increment,
                    user_id int not null,
                    send_time timestamp not null,
                    target_id int not null,
                    isRead boolean not null,
                    msg varchar(4096) not null,
                    isActive boolean not null)default charset=utf8;
                 '''
        ctsql3 = '''create table userfriend(
                    id int primary key auto_increment,
                    user_id int not null,
                    friend_id int not null,
                    add_time timestamp not null,
                    isActive boolean not null)default charset=utf8;
                 '''
        ctsql4 = '''create table chatroom(
                    id int primary key auto_increment,
                    chatroom_name varchar(30) unique not null,
                    create_time timestamp not null,
                    isActive boolean not null)default charset=utf8;
                 '''
        ctsql5 = '''create table chatroom_user(
                    id int primary key auto_increment,
                    chatroom_id int not null,
                    user_id int not null,
                    create_time timestamp not null,
                    isActive boolean not null)default charset=utf8;
                 '''
        ctsql6 = '''create table chatroom_msg(
                    id int primary key auto_increment,
                    chatroom_id int not null,
                    user_id int not null,
                    send_time timestamp not null,
                    msg varchar(4096) not null)default charset=utf8;
                 '''
        if self.connect_to_DB(cdsql) != 'NG':
            self.connect_to_DB(ctsql1, db="chatroom")
            self.connect_to_DB(ctsql2, db="chatroom")
            self.connect_to_DB(ctsql3, db="chatroom")
            self.connect_to_DB(ctsql4, db="chatroom")
            self.connect_to_DB(ctsql5, db="chatroom")
            self.connect_to_DB(ctsql6, db="chatroom")

    def do_delete(self):
        deldatabase = 'drop database chatroom;'
        self.connect_to_DB(deldatabase)

    def do_insertdata(self):
        username = ["admin", "limuxia", "tommy", "abc"]
        password = ["123", "123", "123", "123"]
        nickname = ["管理员", "muxia", "TOMMY", "abc"]
        for i in range(4):
            userinfo = "insert into userinfo (username, password, nickname, isActive) values ('%s', '%s', '%s', %d);" % (
            username[i], password[i], nickname[i], 1)
            self.connect_to_DB(userinfo, db="chatroom")

# if __name__ == '__main__':
#     if sys.argv[1] == "1":
#         DB_Creater().do_create()
#     elif sys.argv[1] == "2":
#         DB_Creater().do_insertdata()
#     elif sys.argv[1] == "3":
#         DB_Creater().do_delete()
