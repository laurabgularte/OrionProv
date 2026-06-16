from sqlalchemy import create_engine, Column, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProvisioningOrder(Base):
    __tablename__ = "provisioning_orders"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, nullable=False)
    service_type = Column(String, nullable=False) 
    status = Column(String, default="PENDING")    # PENDING, PROCESSING, SUCCESS, FAILED, ROLLBACKED
    steps_completed = Column(JSON, default=[])    # Log de passos executados
    error_log = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)