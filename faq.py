# -*- coding: utf-8 -*-
from tasbot.ParseConfig import *
import string
from tasbot.utilities import *
from time import *
from tasbot.Plugin import IPlugin

class Main(IPlugin):
    def __init__(self,name,tasclient):
        IPlugin.__init__(self,name,tasclient)
        self.chans = []
        self.admins = []
        self.faqs = dict()
        self.faqlinks = dict()
        self.filename = ""
        self.last_faq = ""
        self.last_time = time()
        self.min_pause = 5.0

    def oncommandfromserver(self,command,args,socket):
        if command.startswith("SAID") and len(args) > 2:
            if args[2] == "!%s"%self.faqcmd and len(args) > 3:
                now = time()
                user = args[1]
                diff = now - self.last_time
                if diff > self.min_pause :
                    self.printFaq( socket, args[0], args[3] )
                self.last_time = time()
                return
            elif args[2] == "!%slearn"%self.faqcmd and args[1] in self.admins and len(args) > 4:
                self.addFaq( args[3], args[4:] )
                return
            elif args[2] == "!%slist"%self.faqcmd:
                faqstring = "available faq items are: "
                for key in self.faqs:
                    faqstring += key + " "
                socket.send("SAY %s %s\n" % (args[0],faqstring ))
                return
            elif args[2] == "!%slink"%self.faqcmd and args[1] in self.admins and len(args) > 4:
                self.addFaqLink( args[3], args[4:] )
                return
            elif args[2] == "!%shelp"%self.faqcmd:
                socket.send("SAY %s http://springlobby.info/projects/faqbot/wiki/Faqbot\n" % (args[0] ))
                return
            else:
                msg = " ".join( args[2:] ).lower()
                for phrase in self.sortedlinks:
                    if msg.find( phrase ) >= 0:
                        faqkey = self.faqlinks[phrase]
                        print "autodetected message: \"" + msg + "\" faq found: " + faqkey + "\n"
                        now = time()
                        diff = now - self.last_time
                        if diff > self.min_pause :
                            self.printFaq( socket, args[0], faqkey )
                        self.last_time = time()
                        return

    def printFaq( self, socket, channel, faqname ):
        msg = self.faqs[faqname]
        lines = msg.split('\n')
        for line in lines :
            socket.send("SAY %s %s\n" % (channel,line))
            print ("SAY %s %s\n" % (channel,line))

    def loadFaqs( self ):
        faqfile = open(self.faqfilename,'r')
        content = faqfile.read()
        entries = content.split('|')
        i = 0
        while i < len(entries) - 1  :
            self.faqs[entries[i].lower()] = entries[i+1]
            i += 2
        faqfile.close()

    def loadFaqLinks( self ):
        faqlinksfile = open(self.faqlinksfilename,'r')
        content = faqlinksfile.read()
        entries = content.split('|')
        i = 0
        while i < len(entries) - 1  :
            self.faqlinks[entries[i].lower()] = entries[i+1].lower()
            i += 2
        self.sortedlinks = sorted( self.faqlinks, key=len, reverse=True )
        faqlinksfile.close()

    def saveFaqs( self ):
        faqfile = open(self.faqfilename,'w')
        for key,msg in self.faqs.items():
            faqfile.write( key + "|" + msg + "|" )
        faqfile.flush()
        faqfile.close()

    def saveFaqLinks( self ):
        faqlinksfile = open(self.faqlinksfilename,'w')
        for key,msg in self.faqlinks.items():
            faqlinksfile.write( key + "|" + msg + "|" )
        faqlinksfile.flush()
        faqlinksfile.close()

    def addFaqLink( self, key, args ):
        msg = " ".join( args )
        if msg != "" :
            self.faqlinks[msg.lower()] = key.lower()
            self.sortedlinks = sorted( self.faqlinks, key=len, reverse=True )
        self.saveFaqLinks()

    def addFaq( self, key, args ):
        msg = " ".join( args )
        if msg != "" :
            msg = msg.replace( "\\n", '\n' )
            self.faqs[key.lower()] = msg.lower()
        self.saveFaqs()

    def ondestroy( self ):
        self.saveFaqs()
        self.saveFaqLinks()

    def onload(self,tasc):
      self.app = tasc.main
      self.chans = parselist(self.app.config["faqchannels"],',')
      self.admins = parselist(self.app.config["admins"],',')
      self.faqcmd = parselist(self.app.config["faqcmd"],',')[0]
      self.faqfilename = parselist(self.app.config["faqfile"],',')[0]
      self.faqlinksfilename = parselist(self.app.config["faqlinksfile"],',')[0]
      self.faqbotname = parselist(self.app.config["nick"],',')[0]
      self.loadFaqs()
      self.loadFaqLinks()
