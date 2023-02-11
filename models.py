from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    user_id = Column(BIGINT(unsigned=True), primary_key=True)
    name = Column(String(255))

    def __repr__(self):
        return f"User(name={self.name})"

class Wallet(Base):
    __tablename__ = 'wallet'
    id = Column(BigInteger, primary_key=True)
    address = Column(String(255))
    user_id = Column(BIGINT(unsigned=True), ForeignKey('user.user_id'))

    def __repr__(self):
        return f"Wallet(address={self.address}, user_id={self.user_id})"