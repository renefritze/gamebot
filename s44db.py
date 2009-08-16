'''
Created on Aug 15, 2009

@author: koshi
'''
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import *
from datetime import datetime, date, time

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True )
    nick = Column( String(100) )
    country = Column( String(50) )
    cpu = Column( Integer)
    firstlogin = Column( DateTime )
    lastlogin = Column( DateTime )
    lobby = Column( String(30) )
    lobbyrev = Column( String(20) )
    
    def __init__(self, nick, country, cpu, lobby, lobbyrev):
        self.id = id
        self.nick = nick
        self.country = country
        self.cpu = cpu
        #self.lastlogin = now
        self.lobby = lobby
        self.lobbyrev = lobbyrev        
        
class Usersession(Base):
    __tablename__ = 'sessions'
    id = Column( Integer, primary_key=True )
    user_id = Column(Integer, ForeignKey('users.id'))
    start = Column( DateTime )
    end = Column( DateTime )
    
    user = relation(User, backref=backref('sessions', order_by=id))
    
    def __init__(self, user_id):
        self.start = datetime.today()
        self.user_id = user_id


        
class S44DB(object):
    '''
    classdocs
    '''
    

    def __init__(self,dbuser,dbpw,dbname):
        '''
        Constructor
        '''
        self.engine = create_engine('mysql://%s:%s@localhost/%s'%(dbuser,dbpw,dbname), echo=False)
        self.metadata = Base.metadata
        self.metadata.bind = self.engine
        self.metadata.create_all(self.engine)
        self.sessionmaker = sessionmaker( bind=self.engine )
        self.usersessions = dict()
        print 'db init;'
     
    def AddUser(self, nick, country, cpu, lobby, lobbyrev):
        print 'add ' + nick
        session = self.sessionmaker()
        user = session.query(User).filter(User.nick==nick).first()
        if not user:
            user = User( nick, country, cpu, lobby, lobbyrev )
        else:
            user.country = country
            user.cpu = cpu
            user.lobby = lobby
            user.lobbyrev = lobbyrev
            user.firstlogin = datetime.now()
        session.add( user )
        session.commit()
        session.close()
        
    def PrintAll(self):
        session = self.sessionmaker()
        print '-'*60
        for instance in session.query(User).order_by(User.id): 
            print instance.nick, instance.country
            for sess in instance.sessions:
                print sess.start, ' -- ', sess.end 
        print '-'*60
        session.close()
            
    def StartUsersession(self,nick):
        session = self.sessionmaker()
        user = session.query(User).filter(User.nick==nick).first()
        usersession = Usersession(user.id)
        self.usersessions[nick] = usersession
        session.close()
        
    def EndUsersession(self,nick):
        session = self.sessionmaker()
        if nick in self.usersessions:
            usersession = self.usersessions[nick]
            usersession.end = datetime.now()
            session.add(usersession)
            session.commit()
            del self.usersessions[nick]
        session.close()
        
        
        
        