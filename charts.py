# -*- coding: utf-8 -*-
from svg.charts.plot import Plot
from svg.charts import time_series
from datetime import timedelta,datetime,date,time
from dbentities import *

class Charts:

	def __init__(self,db,svgdir):
		self.db = db
		self.svgdir = svgdir
		self.dateformat = '%Y-%m-%d'

	def GetNewUserCount(self,begin,period):
		session = self.db.sessionmaker()
		ret = dict()
		lobbies = session.query( Lobby ).all()
		for lobby in lobbies:
			ret[lobby.name] = []
		end = begin + period
		while end < datetime.now():
			for lobby in lobbies:
				ret[lobby.name].append( end.strftime(self.dateformat) )
				ret[lobby.name].append( session.query( User ).filter( User.lobby_id == lobby.id ).filter( User.firstlogin <= end ).filter( User.firstlogin >= begin ).count() )
			end += period
			begin += period
		end = datetime.now()
		#for lobby in lobbies:
			#ret[lobby.name].append( end.day )
			#ret[lobby.name].append( session.query( User ).filter( User.lobby_id == lobby.id ).filter( User.firstlogin <= end ).filter( User.firstlogin >= begin ).count() )
		session.close()
		return ret
		
		
	def NewUsers(self,periods):
		for period in periods:
			data = self.GetNewUserCount(period[0],period[1])
			g = time_series.Plot({
				'min_y_value': 0,
				'min_x_value': data['other'][0], #better way than hardcode other ?
				#'step_x_labels':period[1],
				'step_include_first_x_label': True,
				'area_fill': True,
				#'stagger_x_labels': True,
				#'stagger_y_labels': True,
				#'show_x_guidelines': True,
				'rotate_x_labels': True,
				'x_label_format': self.dateformat,
				'show_graph_subtitle': True,
				'graph_title' : 'New users per lobby',
				'graph_subtitle' : period[2],
				'show_graph_title' : True,
				'timescale_divisions': "%d days"%(period[1].days)
			})
			
			for name in data.keys():
				g.add_data({'data': data[name], 'title': name})

			res = g.burn()
			f = open(self.svgdir + '/newusers-' + period[2].replace(' ','_') + '.svg', 'w')
			f.write(res)
			f.close()

	def All(self):
		periods = []
		now = datetime.now()
		today = datetime.combine(date.today(), time.min ) #datetime( now.year, now.month, now.day )
		lastweek = today - timedelta(days=7)
		inc = timedelta(days=1)
		periods.append( [lastweek, inc, 'Last week'] )
		lastmonths = today - timedelta(days=90)
		inc = timedelta(days=7)
		periods.append ( [lastmonths, inc, 'Last 3 months'] )
		lastyear = today - timedelta(days=365)
		inc = timedelta(days=30)
		periods.append ( [lastyear, inc, 'Last year'] )
		self.NewUsers(periods)
		
		
		