from ParseConfig import *
import string
from utilities import *
class Main:
	joined_channels = 0
	admins = []
	
	def onloggedin(self,socket):
		cmns = parselist(self.app.config["channels"],',')
		for chan in cmns :
			socket.send("JOIN %s\n" % (chan))
		self.joined_channels = 1
	
	def oncommandfromserver(self,command,args,socket):
	    if command == "SAID" and len(args) > 3 and args[1] in self.admins:
		for chan in args[3:]:
		    if args[2] == "!faqchan":
			socket.send("JOIN %s\n" % (chan))
		    if args[2] == "!faq!chan":
			socket.send("LEAVE %s\n" % (chan))

	def onload(self,tasc):
	    self.app = tasc.main
	    self.admins = parselist(self.app.config["admins"],',')
