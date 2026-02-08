 # fastapi_app/models.py

from typing import List, Optional

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, Session, relationship
from pydantic import BaseModel
from datetime import date
from datetime import datetime
from enum import Enum


Base = declarative_base()

