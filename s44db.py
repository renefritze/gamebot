'''
Created on Aug 15, 2009

@author: koshi
'''
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import *
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column( Integer, primary_key=True )
    nick = Column( String(100) )
    country = Column( String(50) )
    cpu = Column( Integer )
    firstlogin = Column( DateTime )
    lastlogin = Column( DateTime )
    lobby_id = Column( Integer, ForeignKey( 'lobbies.id' ) )
    lobbyrev_id = Column( Integer, ForeignKey( 'lobbyrevisions.id' ) )
    os_id = Column( Integer, ForeignKey( 'os.id' ) )
    
    lobby = relation( 'Lobby', backref=backref( 'users', order_by=id) )
    lobbyrev = relation( 'LobbyRevision', backref=backref( 'users', order_by=id) )
    os = relation( 'OperatingSystem', backref=backref( 'users', order_by=id) )

    
    def __init__(self, nick, country, cpu):
        self.id = id
        self.nick = nick
        self.country = country
        self.cpu = cpu
     
        
class Usersession(Base):
    __tablename__ = 'sessions'
    id = Column( Integer, primary_key=True )
    user_id = Column( Integer, ForeignKey( 'users.id') )
    start = Column( DateTime )
    end = Column( DateTime )
    
    user = relation( User, backref=backref( 'sessions', order_by=id ) )
    
    def __init__(self, user_id):
        self.start = datetime.now()
        self.user_id = user_id

class Lobby(Base):
    __tablename__ = 'lobbies'
    id = Column( Integer, primary_key=True )
    name = Column( String(20) )
    
    def __init__(self,name):
        self.name = name
        
    
class LobbyRevision(Base):
    __tablename__ = 'lobbyrevisions'
    id = Column( Integer, primary_key=True )
    revision = Column( String(50) )
    lobby_id = Column( Integer, ForeignKey( 'lobbies.id' ) )
    
    #lobby = relation( Lobby, backref=backref( 'revisions', order_by=id ) )
    
    def __init__(self, revision, lobby_id):
        self.revision = revision
        self.lobby_id = lobby_id
        
    
class LobbyUpdate(Base):
    __tablename__ = 'lobbyupdates'
    id = Column( Integer, primary_key=True )
    oldrev_id = Column( Integer, ForeignKey( 'lobbyrevisions.id' ) )
    newrev_id = Column( Integer, ForeignKey( 'lobbyrevisions.id' ) )
    user_id = Column( Integer, ForeignKey( 'users.id' ) )
    #oldrev = relation( LobbyRevision )
    #newrev = relation( LobbyRevision )
    user = relation( User )
    date = Column( DateTime ) 
    
    def __init__(self, oldrev_id, newrev_id,user_id):
        self.oldrev_id = oldrev_id
        self.newrev_id = newrev_id
        self.user_id = user_id
        self.date = datetime.now()

class LobbySwitch(Base):
    __tablename__ = 'lobbyswitches'
    id = Column( Integer, primary_key=True )
    oldlobby_id = Column( Integer, ForeignKey( 'lobbies.id' ) )
    newlobby_id = Column( Integer, ForeignKey( 'lobbies.id' ) )
    user_id = Column( Integer, ForeignKey( 'users.id' ) )
    user = relation( User )
    date = Column( DateTime ) 
    
    def __init__(self, oldlobby_id, newlobby_id,user_id):
        self.oldlobby_id = oldlobby_id
        self.newlobby_id = newlobby_id
        self.user_id = user_id
        self.date = datetime.now()
        
class OperatingSystem(Base):
    __tablename__ = 'os'
    id = Column( Integer, primary_key=True )
    name = Column( String(60) )
    
    def __init__(self,name):
        self.name = name
        
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
     
    def AddUser(self, nick, country, cpu ):
        print 'add ' + nick
        session = self.sessionmaker()
               
        user = session.query( User ).filter( User.nick == nick ).first()
        if not user: #new user
            user = User( nick, country, cpu )
            user.firstlogin = datetime.now()
            session.add( user )
            #session.commit() #commit so we get valid ids??? breaks next commit...
        #update user info
        user.country = country
        user.cpu = cpu
        user.lastlogin = datetime.now()
                    
        session.add( user )
        session.commit()
        session.close()
        
    def UpdateUser(self, nick, lobbyname, lobbyrev_name, os ):
        print 'add ' + nick
        session = self.sessionmaker()
        
        lobby = session.query( Lobby ).filter( Lobby.name == lobbyname ).first()
        if not lobby: #new lobby
            lobby = Lobby( lobbyname )
            session.add( lobby )
        lobbyrev = session.query( LobbyRevision ).filter( LobbyRevision.revision == lobbyrev_name ).first()
        if not lobbyrev:
            lobbyrev = LobbyRevision( lobbyrev_name, lobby.id )
            session.add( lobbyrev ) 
        
        user = session.query( User ).filter( User.nick == nick ).first()
        if not user: 
            #some error output
            return

        if user.lobby: #previously set lobby? 
            if user.lobby_id != lobby.id:
                switch = LobbySwitch( user.lobby_id, lobby.id, user.id )
                session.add( switch )
            elif user.lobbyrev_id != lobbyrev.id : #same lobby, but diff rev 
                update = LobbyUpdate( user.lobbyrev_id, lobbyrev.id, user.id )
                session.add( update )
            user.lobbyrev_id = lobbyrev.id
            user.lobby_id = lobby.id
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
        
        
        
        