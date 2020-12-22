from sqlalchemy import (
    Column,
    ForeignKey,
    Boolean, Integer, Text, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Nomination(Base):
    __tablename__ = "nomination"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)

    nominees = Column(JSON, nullable=False)

    tokens = relationship("Token", back_populates="nomination")


class Token(Base):
    __tablename__ = "token"

    id = Column(Integer, primary_key=True)
    value = Column(Text, nullable=False)
    assigned = Column(Boolean, nullable=False, default=False)
    nomination_id = Column(
        Integer,
        ForeignKey("nomination.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False
    )

    nomination = relationship("Nomination", back_populates="tokens")
    votes = relationship("Vote", back_populates="token")


class Vote(Base):
    __tablename__ = "vote"

    id = Column(Integer, primary_key=True)
    token_id = Column(
        Integer,
        ForeignKey("token.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False
    )
    data = Column(JSON, nullable=False)

    token = relationship("Token", back_populates="votes")
