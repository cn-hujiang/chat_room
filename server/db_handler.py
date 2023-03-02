'''数据库操作
author:
	limuxia
date:
	2018.08.03
介绍：
	1.注册,登录,修改密码：
	print(db_operator.register("limuxia","123","Muxia"))
	print(db_operator.login_check("limuxia","123"))
	print(db_operator.change_password("limuxia","123","456"))
	2.添加，删除好友，好友列表:
	print(db_operator.add_friend("limuxia","tommy"))
	print(db_operator.del_friend("limuxia","tommy"))
	print(db_operator.user_friend("limuxia"))
	3.保存消息，查看用户的所有未读消息
	print(db_operator.save_msg("limuxia","tommy",1,1,"你好,tommy!"))
	print(db_operator.get_unread_msg("tommy"))
	4.创建网络聊天室，管理聊天室成员(add / delete)，查看聊天室成员，保存信息到聊天室，查看聊天室历史消息
	print(db_operator.create_chatroom("浪浪浪小分队"))
	print(db_operator.manage_chatroom("浪浪浪小分队", "limuxia", "add"))
	print(db_operator.manage_chatroom("浪浪浪小分队", "tommy", "add"))
	print(db_operator.manage_chatroom("浪浪浪小分队", "tommy", "delete"))
	print(db_operator.get_chatroom_user("浪浪浪小分队"))
	print(db_operator.save_room_msg("limuxia","hahahhaha","吃吃吃小分队"))
	print(db_operator.get_room_msg("吃吃吃小分队",10))　#查看最新的10条消息
	5.其它
	print(db_operator.list_chatroom("limuxia"))　#查看用户加入的聊天室
	print(db_operator.get_nickname("limuxia"))　　#查看用户昵称
'''
import pymysql
import re
import create_db

class DB_Handler(object):
	def __init__(self):
		self.local = 'localhost'
		self.db_login_name = 'root'
		self.db_login_pswd = '123456'
		self.db = 'chatroom'
		self.userinfo = "userinfo"
		self.chatmsg = "chatmsg"
		self.userfriend = "userfriend"
		self.chatroom = "chatroom"
		self.chatroomuser = "chatroom_user"
		self.chatroommsg = "chatroom_msg"
		self.charset = "utf8"
		# 初始化数据库对象时自动创建数据库
		creater = create_db.DB_Creater()
		# creater.do_delete()
		creater.do_create()

	def connect_to_DB(self, sql_statment):
		'''接收sql语句并执行'''
		_ = None #函数返回值
		db_conn = pymysql.connect(self.local,
							  self.db_login_name,
							  self.db_login_pswd,
							  self.db,
							  charset=self.charset)
		cursor = db_conn.cursor()
		try:
			flag = re.search(r'^(select)\s', sql_statment).group(1)
		except Exception:
			flag = ""
		if flag == "select":
			cursor.execute(sql_statment)
			data = cursor.fetchall()
			_ = data
		else:
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

	def user_exist(self, name):
		'''判断用户名是否存在'''
		statment = 'select username from %s where username="%s";' %\
					(self.userinfo, name)
		connfd = self.connect_to_DB(statment)
		if connfd:
			return 'EXIST'

	def register(self, name, pswd):
		'''接收用户注册信息'''
		exitfd = self.user_exist(name)
		if exitfd == 'EXIST':
			return 'NAMEEXIST'
		else:
			statment = 'insert into %s (username,\
					 password,isActive) values ("%s", "%s", 1);'\
					 % (self.userinfo, name, pswd)
			connfd = self.connect_to_DB(statment)
			if connfd == 'OK':
				return 'OK'
			else:
				return 'NG'

	def login_check(self, name, pswd):
		'''接收用户登录信息'''
		statment = 'select username, password from %s\
			where username="%s" and isActive=1;' % (self.userinfo, name)
		connfd = self.connect_to_DB(statment)
		if connfd:
			# 判断返回值的密码
			if pswd == connfd[0][1]:
				return 'OK'
		else:
			return 'NG'

	def change_password(self, name, old_pswd, new_pswd):
		'''修改密码'''
		statment1 = 'select username, password from %s where username="%s"\
					and isActive=1;' % (self.userinfo, name)
		connfd1 = self.connect_to_DB(statment1)
		if connfd1:
			if old_pswd == connfd1[0][1]:
				statment2 = 'update %s set password="%s" where username="%s";'\
							% (self.userinfo, new_pswd, name)
				connfd2 = self.connect_to_DB(statment2)
				if connfd2 == 'OK':
					return 'OK'
		return 'NG'

	def add_friend(self, name, friend_name):
		'''添加好友至数据库'''
		sql_str = 'insert into {} (user_id, friend_id, isActive)\
				   values ((select id from {} where username="{}"),\
				   (select id from {} where username="{}"), 1);'
		statment1 = sql_str.format(self.userfriend, self.userinfo, 
					name, self.userinfo, friend_name)
		statment2 = sql_str.format(self.userfriend, self.userinfo, 
					friend_name, self.userinfo, name)
		# 互相添加好友
		connfd1 = self.connect_to_DB(statment1)
		connfd2 = self.connect_to_DB(statment2)
		if connfd1 == connfd2 == 'OK':
			return 'OK'
		else:
			return 'NG'

	def del_friend(self, name, friend_name):
		'''互相删除好友，即isActive设置为０'''
		sql_str = 'update {} set isActive=0 where user_id=(select\
				   id from {} where username="{}") and friend_id=\
				   (select id from {} where username="{}");'
		statment1 = sql_str.format(self.userfriend, self.userinfo,
					name, self.userinfo, friend_name)
		statment2 = sql_str.format(self.userfriend, self.userinfo,
					friend_name, self.userinfo, name)
		# 互相删除好友
		connfd1 = self.connect_to_DB(statment1)
		connfd2 = self.connect_to_DB(statment2)
		if connfd1 == connfd2 == 'NG':
			return 'NG'
		else:
			return 'OK'

	def user_friend(self, name):
		'''返回(好友：昵称)列表'''
		sql_str = 'select {}.username, {}.nickname from {} inner join {}\
				   on {}.friend_id={}.id where ({}.user_id=(select id from\
				   userinfo where username="{}") and {}.isActive=1);'
		statment = sql_str.format(self.userinfo, self.userinfo, self.userfriend, 
								  self.userinfo,self.userfriend, self.userinfo, 
								  self.userfriend, name, self.userfriend)
		connfd = self.connect_to_DB(statment)
		if connfd:
			friend_list = []
			for i in connfd:
				friend_list.append("%s:%s" % (i[0], i[1]))
			return friend_list
		else:
			return "NF"

	def get_nickname(self, name):
		'''查询用户昵称'''
		sql_str = 'select nickname from {} where username="{}";'
		statment = sql_str.format(self.userinfo, name)
		try:
			return self.connect_to_DB(statment)[0][0]
		except Exception:
			return 'Unknown user'

	def save_msg(self, name, target_user, isRead, msg):
		'''保存私聊消息'''
		sql_str = 'insert into {} (user_id, target_id,isRead,\
				   msg, isActive) values ((select id\
				   from {} where username="{}"),(select id from\
				   {} where username="{}"), {}, "{}", {});'
		statment = sql_str.format(self.chatmsg, self.userinfo, name,
								  self.userinfo, target_user, isRead, 
								  msg, 1)
		connfd = self.connect_to_DB(statment)
		if connfd == 'OK':
			return 'OK'
		else:
			return 'NG'

	def get_unread_msg(self, uname, name):
		'''查询私聊消息'''
		sql_str = 'select msg, send_time from {}\
				   where target_id=(select id from {} where username\
				   ="{}" and user_id=(select id from {} where username="{}"));'
		statment = sql_str.format(self.chatmsg, self.userinfo, name, self.userinfo,uname)
		connfd = self.connect_to_DB(statment)
		if connfd:
			msg_list = []
			for message in connfd:
				msg_list.append(message[0] + " " + str(message[1]))
			return msg_list
		else:
			return 'NG'

	def create_chatroom(self, chatroom_name):
		'''创建聊天室'''
		sql_str = 'select chatroom_name from {} where chatroom_name="{}";' 
		statment = sql_str.format(self.chatroom, chatroom_name)
		connfd = self.connect_to_DB(statment)
		if connfd:
			# 判断聊天室是否已经存在
			return 'EXIST'
		else:
			_sql_str = 'insert into {}(chatroom_name, isActive) values("{}", {});'
			_statment = _sql_str.format(self.chatroom, chatroom_name, 1)
			_connfd = self.connect_to_DB(_statment)
			if _connfd == "OK":
				return "OK"
			return "NG"

	def manage_chatroom(self, chatroom_name, name, handler):
		'''管理聊天室用户'''
		if handler == 'add':
			# 添加用户：isActive＝１
			sql_str = 'insert into {} (chatroom_id, user_id, isActive) values\
					   ((select id from {} where chatroom_name="{}"),(select\
					   id from {} where username="{}"),1);'
			statment = sql_str.format(self.chatroomuser, self.chatroom, 
									  chatroom_name, self.userinfo, name)
		elif handler == "delete":
			# 删除用户：isActive＝０
			sql_str = 'update {} set isActive=0 where chatroom_id=(select id\
					   from {} where chatroom_name="{}") and user_id=(select\
					   id from {} where username="{}");'
			statment = sql_str.format(self.chatroomuser, self.chatroom,
									  chatroom_name, self.userinfo, name)
		connfd = self.connect_to_DB(statment)
		if connfd == "OK":
			return "OK"
		return "NG"

	def get_chatroom_user(self, chatroom_name):
		'''获取聊天室用户'''
		sql_str = 'select {}.username, {}.nickname from {} where {}.id=any\
					(select {}.user_id from {} where {}.chatroom_id=(select\
					{}.id from {} where {}.chatroom_name="{}"));'
		statment = sql_str.format(self.userinfo,self.userinfo,self.userinfo,
								  self.userinfo,self.chatroomuser,self.chatroomuser,
								  self.chatroomuser,self.chatroom,self.chatroom,
								  self.chatroom,chatroom_name)
		connfd = self.connect_to_DB(statment)
		if connfd:
			friend_list = []
			for i in connfd:
				friend_list.append("%s:%s" % (i[0], i[1]))
			return friend_list
		else:
			return "NF"

	def list_chatroom(self, name):
		'''查看群列表'''
		sql_str = 'select {}.chatroom_name from {} where {}.id=any(\
			select {}.chatroom_id from {} where {}.user_id=(select id\
			from {} where {}.username="{}"));'
		statment = sql_str.format(self.chatroom, self.chatroom, self.chatroom,
								  self.chatroomuser, self.chatroomuser, self.chatroomuser,
								  self.userinfo, self.userinfo, name)
		connfd = self.connect_to_DB(statment)
		if connfd:
			chatroom_list = []
			for i in connfd:
				chatroom_list.append("%s:%s" % ("群", i[0]))
			return chatroom_list
		else:
			return "NF"

	def save_room_msg(self, name, msg, chatroom_name):
		'''保存聊天室消息'''
		sql_str = 'insert into {}(chatroom_id,user_id,msg) values\
				  ((select id from {} where chatroom_name="{}"),\
				  (select id from {} where username="{}" ),"{}");'
		statment = sql_str.format(self.chatroommsg, self.chatroom, chatroom_name,
								  self.userinfo, name, msg)
		connfd = self.connect_to_DB(statment)
		if connfd == 'OK':
			return "OK"
		return "NG"

	def get_room_msg(self,chatroom_name,count):
		'''查看所有聊天室消息'''
		sql_str = 'select {}.username,{}.msg,{}.send_time from {},{} where {}.user_id = {}.id\
				   and {}.chatroom_id=(select id from {} where {}.chatroom_name="{}") order by\
				   send_time DESC limit {};'
		statment = sql_str.format(self.userinfo,self.chatroommsg,self.chatroommsg,
								  self.userinfo,self.chatroommsg,self.chatroommsg,
								  self.userinfo,self.chatroommsg,self.chatroom,
								  self.chatroom,chatroom_name,count)
		connfd = self.connect_to_DB(statment)
		if connfd:
			msg_list = []
			for i in connfd:
				# print(i)
				message = (i[0],i[1],str(i[2]))
				# message = str(i[2]) + '(' + i[0] + ')' +  ' : ' + i[1]
				msg_list.append(message)
			return msg_list
		else:
			return "NG"

# 测试代码
# db_operator = DB_Handler()
# print(db_operator.create_chatroom("sys_chatroom"))
# print(db_operator.register("limuxia","123"))
# print(db_operator.save_room_msg("limuxia","123","sys_chatroom"))
# print(db_operator.save_room_msg("limuxia","456","sys_chatroom"))
# print(db_operator.save_room_msg("limuxia","789","sys_chatroom"))
# print(db_operator.save_room_msg("limuxia","000","sys_chatroom"))
# print(db_operator.get_room_msg("sys_chatroom",10))


# print(db_operator.login_check("limuxia","123"))
# print(db_operator.change_password("limuxia","123","456"))
# print(db_operator.add_friend("limuxia","tommy"))
# print(db_operator.del_friend("limuxia","tommy"))
# print(db_operator.user_friend("limuxia"))
# print(db_operator.get_nickname("limuxia"))
# print(db_operator.save_msg("limuxia","tommy",1,1,"你好,tommy!"))
# print(db_operator.get_unread_msg("tommy"))
# print(db_operator.manage_chatroom("吃吃吃小分队", "limuxia", "add"))
# print(db_operator.manage_chatroom("吃吃吃小分队", "tommy", "add"))
# print(db_operator.manage_chatroom("吃吃吃小分队", "tommy", "delete"))
# print(db_operator.get_chatroom_user("吃吃吃小分队"))
# print(db_operator.list_chatroom("limuxia"))