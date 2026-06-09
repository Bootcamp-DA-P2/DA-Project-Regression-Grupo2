from fastapi import FastAPI, HTTPException, HttpException, status, Depends

from sqlalchemy.orm import Session, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from pydantic import BaseModel

import pandas as pd

import os

def df_to_dict(path):
    df = pd.read_csv(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"File {path} not found.")
    return df.to_dict('records')

app = FastAPI(title='Football Data API') 

# Carga dinámica de modelos guardados
MODELS_DIR = '../models/'
loaded_models = {}
for m_name, filename in [('Random Forest', 'random_forest_model.pkl'), ('XGBoost', 'xgboost_model.pkl')]:
    path = os.path.join(MODELS_DIR, filename)
    if os.path.exists(path):
        loaded_models[m_name] = joblib.load(path)
        print(f"✅ Modelo '{m_name}' cargado en el backend.")

# Database setup
engine = create_engine('sqlite:///fotball_data.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models

class Competition(Base):
    __tablename__ = 'competitions'
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, unique=True, index=True)

    clubs = relationship("Club", back_populates="competition")

class Club(Base):
    __tablename__ = 'clubs'
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    club_name = Column(String, unique=True, nullable=False, index=True)

    league_id = Column(Integer, ForeignKey('competitions.id'), nullable=False)
    competition = relationship("Competition", back_populates="clubs")

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    position = Column(String, nullable=False, index=True)

    league_id = Column(Integer, ForeignKey('competitions.id'), nullable=False)
    competition = relationship("Competition", back_populates="players")

    club_id = Column(Integer, ForeignKey('clubs.id'), nullable=False)
    club = relationship("Club", back_populates="players")

Base.metadata.create_all(engine)

# Pydantic Models (Dataclass)

class Competition(BaseModel):
    id: str
    name: str

class Club(BaseModel):
    id: int
    club_name: str
    league_id: str

class Player(BaseModel):
    pass


class PredictRequest(BaseModel):
    model_name: str
    player_name: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

get_db()

# Endpoints
@app.get("/competitions/")
def get_competitions(db: Session = Depends(get_db)):
    competitions = db.query(Competition).all()
    if not competitions:
        raise HttpException(status_code=status.HTTP_404_NOT_FOUND, detail="No competitions found")
    return competitions

@app.post("/competitions/")
def create_competition(db: Session = Depends(get_db)):
    try:
        competitions = df_to_dict('../data/clean/competitions.csv')
        for competition in competitions:
            db_competition = Competition(id=competition['id'], name=competition['name'])
            db.add(db_competition)
        db.commit()
        return {"message": "Competitions created successfully"}
    except FileNotFoundError as e:
        raise HttpException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@app.get("/clubs/")
def get_clubs(db: Session = Depends(get_db)):
    clubs = db.query(Club).all()
    if not clubs:
        raise HttpException(status_code=status.HTTP_404_NOT_FOUND, detail="No clubs found")
    return clubs

@app.post("/clubs/")
def create_clubs(db: Session = Depends(get_db)):
    try:
        clubs = df_to_dict('../data/clean/clubs.csv')
        for club in clubs:
            db_club = Club(id=club['id'], club_name=club['club_name'], league_id=club['league_id'])
            db.add(db_club)
        db.commit()
        return {"message": "Clubs created successfully"}
    except FileNotFoundError as e:
        raise HttpException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@app.get("/players/")
def get_players(db: Session = Depends(get_db)):
    players = db.query(Player).all()
    if not players:
        raise HttpException(status_code=status.HTTP_404_NOT_FOUND, detail="No players found")
    return players

@app.post("/players/")
def create_players(db: Session = Depends(get_db)):
    try:
        players = df_to_dict('../data/clean/players.csv')
        for player in players:
            db_player = Player(id=player['id'], name=player['name'], position=player['position'])
            db.add(db_player)
        db.commit()
        return {"message": "Players created successfully"}
    except FileNotFoundError as e:
        raise HttpException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
