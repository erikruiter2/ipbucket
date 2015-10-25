from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from ipaddr_func import ip2long, long2ip
from sqlalchemy.exc import IntegrityError

engine = create_engine('sqlite:////tmp/ipbucket.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()



def init_db(): 
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)


def db_add_entry(tablename, **kwargs):
  """ Adds an entry to a table, returns an errormessage on failure, on success it returns the id of the created object"""
  try:
    n = tablename(**kwargs)
    db_session.add(n)
    db_session.commit()
  except ValueError as e:
    return "Error while adding entry: " + str(e)
  except TypeError as e:
    return "Error while adding entry: " + str(e)
  except IntegrityError as e:
    db_session.rollback()
    return "Error while adding entry: " + str(e.orig.message) + str(e.params)   
  return n.id

 
def db_query_all(tablename):
  print tablename.__tablename__
  entries = list()
  entrylist = dict()

  for entry in tablename.query.all():
    for value in vars(entry):
      if value != '_sa_instance_state':
        entrylist[value] = vars(entry)[value]
      if value == 'ip' and tablename.__tablename__ == 'ipv4network':
		    entrylist[value] = long2ip(vars(entry)[value])  + "/" + str(vars(entry)['mask']) 	

    entries.append(entrylist)
    entrylist = dict()
  return entries



def db_query_by_id(tablename, _id):
  entrylist = dict()
  entry = tablename.query.filter_by(id=_id).first()
  for value in vars(entry):
    if value != '_sa_instance_state':
      entrylist[value] = vars(entry)[value]
  return entrylist

