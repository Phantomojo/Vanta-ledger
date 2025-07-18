from sqlalchemy import Column, Integer, String, Text, ForeignKey
from . import Base

class Subcontractor(Base):
    __tablename__ = 'subcontractors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    contact = Column(String(255))
    notes = Column(Text)
    linked_project_id = Column(Integer, ForeignKey('projects.id')) 