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

class Main:
	chans = []
	admins = []
	
	def SendUsers(self, nick, socket ):
		users = self.db.GetGameUsers( 's44' )
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
		users = self.db.GetGameUsers( 's44' )
		

		socket.send('sayprivate %s total s44 only joiners: %s \n'%(nick,len(users)))
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

	def CmdStatsReport(self, socket, cmd_name, cmd_params, lobby):
		source_nick = cmd_params[0]
		#socket.send('say %s %s %s \n'%(self.stats_channel, source_nick, ' '.join(cmd_params) ))
		print 'say %s %s %s \n'%(self.stats_channel, source_nick, ' '.join(cmd_params) )
		params=cmd_params[2:]
		revision = params[0]
		os = 'Unknown'
		if len(params) > 1:
			os = params[2]
		self.db.UpdateUser(source_nick, lobby, revision, os)
		socket.send('say %s %s %s %s %s\n'%(self.stats_channel,source_nick, lobby, revision, os))
	

		#update notificatiosn below
		if revision == 'v0.0.1-svn':
			socket.send('sayprivate '+source_nick + ' ' + self.update_notice +'\n')
		else :
			revision = revision.split('.')
			if len(revision) > 3:
				if revision[3].isdigit() :
					revision = int(revision[3])
					if revision < self.min_revision :
						socket.send('sayprivate '+source_nick + ' ' + self.update_notice +'\n' )

	def SendLobbyMetric(self, nick, socket, lobby ):
		lobbyusers = self.db.GetLobbyUsers( lobby )
		allusers = self.db.GetAllUsers() * 1.0
		if lobbyusers > 0:
			socket.send('sayprivate %s percentage of %s users:\t\t %f\n'%(nick, lobby, lobbyusers/allusers ) )
		socket.send('sayprivate %s absolute number of %s users:\t %d\n'%(nick, lobby, lobbyusers ) )
		socket.send('sayprivate %s total number of users:\t\t\t\t\t %d\n'%(nick, allusers ) )

		socket.send('sayprivate %s session stats:\n'%(nick) )
		stats = self.db.GetSessionStats()
		total = stats['all']
		for key,num in stats.items():
			socket.send('sayprivate %s %8i\t %s sessions \t(%5f)\n'%(nick, num, key, ( num / float(total) ) * 100 ) )
		from datetime import datetime,timedelta
		since = datetime.now() - timedelta(7)
		socket.send('sayprivate %s %d updates since %s\n'%(nick,self.db.GetUpdates( since ), str(since) ) )
		stats = self.db.GetOSstats(lobby)
		for key,num in stats.items():
			socket.send('sayprivate %s %d sl users on %s\n'%(nick, num, key) )
		from datetime import datetime,timedelta
	

	def oncommandfromserver(self,command,args,socket):
		if command == "JOINED" :
			chan = args[0]
			user = args[1]
			if chan == "s44" :			
				self.db.SetPrimaryGame( user, 's44' )
			elif chan in self.chans :
				self.db.SetPrimaryGame( user, 'multiple' )
		if command == "SAIDPRIVATE" and len(args) > 1:
			if args[0] in self.admins:
				if args[1] == "metricsave":
					self.ondestroy()
				if args[1] == "metric":
					if len( args ) > 2:
						if args[2] == 'sl':
							args[2] = 'SpringLobby'
						self.SendLobbyMetric( args[0], socket, args[2] )
					else:
						self.SendMetric( args[0], socket )
				if args[1] == "users":
					self.SendUsers( args[0], socket )
				if args[1] == 'chart':
					self.ChartTest()
		if command == "ADDUSER" and len(args) > 2:
			self.db.AddUser(args[0], args[1], args[2] )
			self.db.StartUsersession( args[0] )
		if command == "REMOVEUSER" and len(args) > 0:
			self.db.EndUsersession(args[0])
		if command.startswith("SAID") and len(args) > 1:
			print args, command
			if args[1] == "stats.report":
				self.CmdStatsReport( socket, command, args, 'SpringLobby' )

	def ondestroy( self ):
		print "saving files"
		self.db.CloseAllSessions()

	def onload(self,tasc):
		self.app = tasc.main
		self.chans = parselist(self.app.config["channels"],',')
		self.admins = parselist(self.app.config["admins"],',')
		self.update_notice = parselist(self.app.config["update_notice"],',')[0]
		self.stats_channel = parselist(self.app.config["stats_channel"],',')[0]
		self.min_revision = int( parselist(self.app.config["min_revision"],',')[0] )
		system('touch users.txt users_s44.txt' )
		self.db = S44DB(parselist(self.app.config["dbuser"],',')[0] ,
                      parselist(self.app.config["dbpw"],',')[0],
                      parselist(self.app.config["dbname"],',')[0] )
		if not self.db:
			raise SystemExit(-1)

	def ChartTest(self):
		import charts
		chart = charts.Charts( self.db, "/tmp/sl" )
		chart.All()

