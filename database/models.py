from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    task = Column(String)
    completed = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Task(id={self.id}, user_id={self.user_id}, task='{self.task}', completed={self.completed})>"