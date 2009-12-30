# -*- coding: utf-8 -*-

from dbentities import *

class Notices:

	def __init__(self,db):
		self.db = db
		
	def HasNotice(self, rev):
		session = self.db.sessionmaker()
		db_rev = session.query( LobbyRevision ).filter( LobbyRevision.revision == rev ).first()
		if not db_rev:
			return False
		ret = session.query( Notice ).filter( Notice.lobbyrev_id == db_rev.id ).count()
		session.close()
		return ret

	def GetNotices(self,rev):
		session = self.db.sessionmaker()
		db_rev = session.query( LobbyRevision ).filter( LobbyRevision.revision == rev ).first()
		if not db_rev:
			return []
		
		ret = session.query( Notice ).filter( Notice.lobbyrev_id == db_rev.id ).all()
		session.close()
		return ret

	def AddNotice(self, rev, text):
		session = self.db.sessionmaker()
		db_rev = session.query( LobbyRevision ).filter( LobbyRevision.revision == rev ).first()
		if not db_rev:
			return False
		
		notice = Notice()
		notice.lobbyrev_id = db_rev.id
		notice.text = text
		session.add( notice )
		session.commit()
		session.close()
		return True
		
		