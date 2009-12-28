# -*- coding: utf-8 -*-
from svg.charts.plot import Plot
from datetime import timedelta,datetime,date,time
from dbentities import *

class Charts:

	def __init__(self,db,svgdir):
		self.db = db
		self.svgdir = svgdir

	def GetNewUserCount(self,begin,period):
		session = self.db.sessionmaker()
		ret = dict()
		lobbies = session.query( Lobby ).all()
		for lobby in lobbies:
			ret[lobby.name] = []
		end = begin + period
		while end < datetime.now():
			for lobby in lobbies:
				ret[lobby.name].append( end.day )
				ret[lobby.name].append( session.query( User ).filter( User.lobby_id == lobby.id ).filter( User.firstlogin <= end ).filter( User.firstlogin >= begin ).count() )
			end += period
			begin += period
		end = datetime.now()
		#for lobby in lobbies:
			#ret[lobby.name].append( end.day )
			#ret[lobby.name].append( session.query( User ).filter( User.lobby_id == lobby.id ).filter( User.firstlogin <= end ).filter( User.firstlogin >= begin ).count() )
		session.close()
		return ret
		
		
	def NewUsers(self):
		g = Plot({
			'min_x_value': lastweek.day,
			'min_y_value': 0,
			'area_fill': True,
			'stagger_x_labels': True,
			'stagger_y_labels': True,
			'show_x_guidelines': True
		})
		data = self.GetNewUserCount(lastweek,period)
		for name in data.keys():
			print data[name]
			g.add_data({'data': data[name], 'title': name})

		res = g.burn()
		f = open(r'Plot.py.svg', 'w')
		f.write(res)
		f.close()

	def All(self):
		periods = []
		now = datetime.now()
		today = datetime.combine(date.today(), time.min ) #datetime( now.year, now.month, now.day )
		lastweek = today - timedelta(days=7)
		inc = timedelta(days=1)
		periods.append = ( lastweek, inc, 'Last week' )
		lastmonths = today - timedelta(days=90)
		inc = timedelta(days=7)
		periods.append = ( lastmonths, inc, 'Last 3 months' )
		lastyear = today - timedelta(days=365)
		inc = timedelta(days=30)
		periods.append = ( lastyear, inc, 'Last year' )
		
		
		