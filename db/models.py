from sqlalchemy import Column, String, Integer, BigInteger, VARCHAR, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Create a base class for SQLAlchemy models.
Base = declarative_base()


# Define the Client model.
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, autoincrement=False)
    client_name = Column(VARCHAR, index=True, unique=False)
    shem_hevra = Column(VARCHAR, index=True, unique=False)
    telefon = Column(Integer, index=True)
    bdika_gilui = relationship("BdikaGilui", back_populates="client")  # Relationship with BdikaGilui model


# Define the BdikaGilui model.
""" 
var = BG - that mean it is from class BdikaGilui
"""


class BdikaGilui(Base):
    __tablename__ = "bdikotgilui"
    id = Column(Integer, primary_key=True, autoincrement=True)
    makom_shembg = Column(VARCHAR, index=True)
    makom_yehudbg = Column(VARCHAR, index=True)
    makom_ktovetbg = Column(VARCHAR, index=True)
    makom_locationbg = Column(VARCHAR, index=True)
    kamut_galaimbg = Column(Integer, index=True)
    check_datebg = Column(VARCHAR, index=True)
    document_namebg = Column(VARCHAR, index=True)
    file_uploadbg = Column(VARCHAR, index=True)
    id_order = Column(Integer, ForeignKey('clients.id'))  # Foreign key relationship with Client model
    client = relationship("Client", back_populates="bdika_gilui")  # Relationship with Client model
