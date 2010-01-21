# -*- coding: utf-8 -*-
from colors import *
from ParseConfig import *
import string
from utilities import *
from time import *
from os import system
from s44db import S44DB
import sys, os
from svg.charts.plot import Plot
from notices import Notices

class Main:
	chans = []
	admins = []

	def onload(self,tasc):
		self.app = tasc.main
		self.modchannels = parselist(self.app.config["modchannels"],',')
		self.channels = parselist(self.app.config["channels"],',')
		self.modname = parselist(self.app.config["mod"],',')[0]
		self.modtag = parselist(self.app.config["modtag"],',')[0]
		self.admins = parselist(self.app.config["modadmins"],',')
		self.admins.append( parselist(self.app.config["admins"],',') )
		self.db = S44DB(parselist(self.app.config["dbuser"],',')[0] ,
                      parselist(self.app.config["dbpw"],',')[0],
                      parselist(self.app.config["dbname"],',')[0] )
		if not self.db:
			raise exit( 0 )

	def SendUsers(self, nick, socket ):
		users = self.db.GetGameUsers( self.modname )
		users.sort(key=str.lower)
		num = 0
		line = ""
		socket.send('sayprivate %s %d users found:\n'%(nick,len(users) ))
		for user in users :
			line += user + "\t"
			num += 1
			if num % 10 == 0 :
				socket.send('sayprivate %s %s \n'%(nick,line ))
				line = ""
		socket.send('sayprivate %s %s \n'%(nick,line ))


	def SendMetric(self, nick, socket ):
		users = self.db.GetGameUsers( self.modname )
		socket.send('sayprivate %s total %s only joiners: %d \n'%(nick,self.modname,len(users)))

	def oncommandfromserver(self,command,args,socket):
		if command == "JOINED" :
			chan = args[0]
			nick = args[1]
			if chan in self.modchannels:
				self.db.SetPrimaryGame( nick, self.modname )
				try:
					user = self.db.GetUser( nick )
					print '%s -- %d -- %d'%(nick, user.welcome_sent,user.rank )
					if not user.welcome_sent and user.rank < 1:
						socket.send('say %s hello first time visitor %s\n'%(chan,nick) )
						user.welcome_sent = True
						self.db.SetUser( user )
				except Exception, e:
					print(e)

			elif chan in self.channels:
				self.db.SetPrimaryGame( nick, 'multiple' )
		if command == "SAIDPRIVATE" and len(args) > 1:
			if args[0] in self.admins and args[1].startswith('!'):
				command = args[1][1:]
				if command == "metric":
					self.SendMetric( args[0], socket )
				if command == "users":
					self.SendUsers( args[0], socket )
				if command == 'chart':
					self.ChartTest()
					socket.send('sayprivate %s done \n'%(args[0]))
				