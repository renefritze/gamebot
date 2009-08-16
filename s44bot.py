# -*- coding: utf-8 -*-
from colors import *
from ParseConfig import *
import string
from utilities import *
from time import *
from os import system
from s44db import S44DB

class Main:
	chans = []
	admins = []
	nicklist_main = []
	nicklist_s44 = []

	def loadUserFile(self):
		self.nicklist = []
		self.nicklist_s44 = []
		self.ubuntu_list = []
		self.win_list = []
		self.readUserFile('users.txt', self.nicklist)
		self.readUserFile('users_s44.txt', self.nicklist_s44)

	def readUserFile(self, name, userlist):
		file_users=open(name,'r')
		file_users.flush()
		file_users.close()
		file_users=open(name,'r')
		while True:
			line = file_users.readline()
			if len(line) == 0:
				break
			if len(line) > 1:
				line = line[0:(len(line)-1)]
				userlist += [line]
		file_users.close()

	def saveUserFile(self):
		self.writeUserFile('users.txt',self.nicklist)
		self.writeUserFile('users_s44.txt',self.nicklist_s44)

	def writeUserFile(self, name, userlist):
		file_users=open(name,'w')
		for nick in userlist:
			file_users.write(nick+'\n')
		file_users.flush()
		file_users.close()

	def SendUsers(self, nick, socket ):
		users = self.nicklist_s44[:]
		users.sort(key=str.lower)
		num = 0
		line = ""
		socket.send('sayprivate %s %d users found:\n'%(nick,len(self.nicklist_s44) ))
		for user in users :
			line += user + "\t"
			num += 1
			if num % 10 == 0 :
				socket.send('sayprivate %s %s \n'%(nick,line ))
				line = ""
		socket.send('sayprivate %s %s \n'%(nick,line ))

	def SendMetric(self, nick, socket ):
		total = 0

		socket.send('sayprivate %s total s44 only joiners: %s \n'%(nick,len(self.nicklist_s44)))
		#sleep(0.05)
		#percent = len(self.nicklist_s44)/ float(len(self.nicklist))
		#socket.send('sayprivate %s total : %s \n'%(nick,len(self.nicklist)))
		#sleep(0.05)
		#socket.send('sayprivate %s percentage of sl: %f \n'%(nick,percent))
		#sleep(0.05)
		#percent = len(self.ubuntu_list)/ float(len(self.nicklist_s44))
		#socket.send('sayprivate %s percentage (of sl users) on linux: %f \n'%(nick,percent))
		#sleep(0.05)
		#percent = len(self.win_list)/ float(len(self.nicklist_s44))
		#socket.send('sayprivate %s percentage (of sl users) on other: %f (%d abs)\n'%(nick,percent,len(self.win_list)))

	def oncommandfromserver(self,command,args,socket):
		if command == "JOINED" :
			chan = args[0]
			user = args[1]
			if chan == "s44" :
				if not user in self.nicklist:
					if not user in self.nicklist_s44:
						self.nicklist_s44.append(user)
			elif chan in self.chans :
				if not user in self.nicklist:
					self.nicklist.append(user)
				if user in self.nicklist_s44:
					self.nicklist_s44.remove(user)
		if command == "SAIDPRIVATE" and len(args) > 1:
			if args[0] in self.admins:
				if args[1] == "metricsave":
					self.ondestroy()
				if args[1] == "metric":
					self.SendMetric( args[0], socket )
				if args[1] == "users":
					self.SendUsers( args[0], socket )
		if command == "ADDUSER" and len(args) > 2:
			self.db.AddUser(args[0], args[1], args[2], "", "")
			self.db.StartUsersession(args[0])
		if command == "REMOVEUSER" and len(args) > 0:
			self.db.EndUsersession(args[0])
		#self.db.Commit()

	def ondestroy( self ):
		print "saving files"
		self.saveUserFile()

	def onload(self,tasc):
		self.app = tasc.main
		self.chans = parselist(self.app.config["channels"],',')
		self.admins = parselist(self.app.config["admins"],',')
		system('touch users.txt users_s44.txt' )
		self.loadUserFile()
		self.db = S44DB(parselist(self.app.config["dbuser"],',')[0] ,
                      parselist(self.app.config["dbpw"],',')[0],
                      parselist(self.app.config["dbname"],',')[0] )
		self.db.PrintAll()
