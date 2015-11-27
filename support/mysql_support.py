# -*- coding:utf8 -*-

from sqlalchemy import create_engine
try:
    from config import SQLALCHEMY_DATABASE_URI
    from config import SQLALCHEMY_ANALYSIS_URI
except:
    print 'SQLALCHEMY_DATABASE_URI is not exist'
    print 'Please add config.py in support folder'
    exit()

engine = create_engine(SQLALCHEMY_DATABASE_URI)
analysis_engine = create_engine(SQLALCHEMY_ANALYSIS_URI)

from sqlalchemy.orm.session import sessionmaker
from model import User, Tweet
Session = sessionmaker()
Session.configure(bind=engine)
AnalysisSession = sessionmaker()
AnalysisSession.configure(bind=analysis_engine)


if __name__ == '__main__':
    sess = AnalysisSession()
    sess.add(User(1, 'test', 'screen_test', 0, 0))
    sess.commit()
    sess.query(User).filter(User.id == 1).delete(
            synchronize_session=False)
    sess.commit()
    sess.close()
