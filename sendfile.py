#!/usr/bin/python3
import socket
import sys
from socket import gethostbyname_ex, gethostname
from tkinter import filedialog


def getMyIP():
	if 'win' in sys.platform:
		return gethostbyname_ex(gethostname())[-1][-1]
	elif 'linux' in sys.platform:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('4.4.4.4', 80))
		return s.getsockname()[0]
	else:
		print("未知平台，无法运行")
		sys.exit()


class SendFile:
	def __init__(self):
		self.my = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.my_ip = getMyIP()
		self.type = None
		self.filename = str()
		print("*" * 60)
		print("当前设备ip: {}\n".format(self.my_ip))
		print("*" * 60)
		try:
			print("\t输入【1】接受文件或消息")
			print("\t输入【2】发送本机文件")
			print("\t输入【3】发送消息")
			print("\t输入【4或ctrl+c】退出")
			sel = input("输入要进行的操作\n")
			if sel == '1':
				self.receive()
			elif sel == '2':
				self.sendFile()
			elif sel == '3':
				self.sendMessage()
			elif sel == '4':
				self.my.close()
				exit()
			else:
				return
		except KeyboardInterrupt:
			self.my.close()
			exit()
		self.my.close()

	def receive(self):
		self.my.bind(('', 7890))
		self.my.listen(128)
		while True:
			print("》》》正在等待接受文件或消息")
			other_my, he_addr = self.my.accept()
			while True:
				r_data = other_my.recv(4096)
				if r_data:
					data = r_data.split(b",")
					if data[0] == b"mes":
						other_my.send(b'ok')
						self.type = 'M'
					elif data[0] == b'file':
						other_my.send(b'ok')
						self.type = 'F'
						self.filename = data[1].decode('utf-8')
					else:
						if self.type == 'M':
							print("\t\t来自{}的消息>> {}".format(he_addr, r_data.decode('utf-8')))
						elif self.type == 'F':
							with open(self.filename, 'ab+') as f:
								f.write(r_data)
							print("\t\t来自{}的文件{}写入".format(he_addr, self.filename))
						else:
							print("\t\t来自{}的未知消息，这里不讨论".format(he_addr))
				else:
					other_my.close()
					self.my.close()
					return

	def sendMessage(self):
		his_ip = input("输入接受者ip: ")
		if his_ip:
			self.my.connect((his_ip, 7890))
			self.my.send(b"mes")
			if self.my.recv(1024) == b"ok":
				message = input("输入要发送的信息：")
				self.my.send(message.encode('utf-8'))
				self.my.close()
				print("发送成功")
			else:
				self.my.close()
				print("连接失败！")

	def sendFile(self):
		path = filedialog.askopenfilename()
		if not path:
			return
		print('将发送文件：{}'.format(path))
		his_ip = input("输入接受者ip: ")
		if his_ip:
			self.my.connect((his_ip, 7890))
			self.my.send(b"file,%s" % path.split('/')[-1].encode())
			if self.my.recv(1024) == b"ok":
				f = open(path, 'rb')
				self.my.sendall(f.read())
				self.my.close()
				f.close()
				print("发送成功")
			else:
				self.my.close()
				print("连接失败！")


if __name__ == '__main__':
	print("welcome to use <SendFile & Correspondence> tools")
	while True:
		SendFile()
