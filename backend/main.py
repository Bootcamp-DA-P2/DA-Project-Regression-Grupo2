from fastapi import FastAPI, HTTPException, status, Depends

from sqlalchemy.orm import Session, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from pydantic import BaseModel

import pandas as pd

import os

# Comando para lanzar el backend desde la carpeta backend
# uvicorn main:app --reload

def df_to_dict(path):
    try:
        df = pd.read_csv(path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"File {path} not found.")
        return df.to_dict('records')
    except Exception as e:
        raise Exception(f'Error: {e}')

app = FastAPI(title='Football Data API') 

# Database setup
engine = create_engine('sqlite:///fotball_data.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class CompetitionORM(Base):
    __tablename__ = 'competitions'
    id = Column(String, primary_key=True, nullable=False, index=True)
    name = Column(String, unique=True, index=True)

    clubs = relationship("ClubORM", back_populates="competition")
    players = relationship("PlayerORM", back_populates="competition")

class ClubORM(Base):
    __tablename__ = 'clubs'
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    club_name = Column(String, unique=True, nullable=False, index=True)
    league_id = Column(Integer, ForeignKey('competitions.id'), nullable=False)

    competition = relationship("CompetitionORM", back_populates="clubs")
    players = relationship("PlayerORM", back_populates="club")


class PlayerORM(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    position = Column(String, nullable=False, index=True)
    last_season = Column(Integer, nullable=False)
    country_of_birth = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    position = Column(String, nullable=False)
    height_in_cm = Column(String, nullable=False)
    club_name = Column(String, nullable=False)
    market_value_in_eur = Column(Integer, nullable=False)

    league_id = Column(Integer, ForeignKey('competitions.id'), nullable=False)
    competition = relationship("CompetitionORM", back_populates="players")

    club_id = Column(Integer, ForeignKey('clubs.id'), nullable=False)
    club = relationship("ClubORM", back_populates="players")


Base.metadata.create_all(engine)

# Pydantic Schemas (Dataclass)
class CompetitionSchema(BaseModel):
    id:   str
    name: str

    class Config:
        from_attributes = True

class ClubSchema(BaseModel):
    id:        int
    club_name: str
    league_id: int

    class Config:
        from_attributes = True

class PlayerSchema(BaseModel):
    id:                  int
    name:                str
    last_season:         int
    club_id:             int
    country_of_birth:    str
    age:                 int
    position:            str
    height_in_cm:        str
    league_id:           int
    club_name:           str
    market_value_in_eur: int

    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Endpoints
@app.get("/competitions/")
def get_competitions(db: Session = Depends(get_db)):
    competitions = db.query(CompetitionORM).all()
    if not competitions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No competitions found")
    return competitions

@app.post("/competitions/")
def create_competition(csv_path= "../data/clean/competitions_clean.csv", db: Session = Depends(get_db)):
    try:
        competitions = df_to_dict(csv_path)
        for competition in competitions:
            db_competition = CompetitionORM(id=competition['competition_id'], name=competition['name'])
            db.add(db_competition)
        db.commit()
        return {"message": "Competitions created successfully"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@app.get("/clubs/")
def get_clubs(db: Session = Depends(get_db)):
    clubs = db.query(ClubORM).all()
    if not clubs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No clubs found")
    return clubs

@app.post("/clubs/")
def create_clubs(csv_path: str = "../data/clean/clubs_clean.csv",db: Session = Depends(get_db)):
    try:
        clubs = df_to_dict(csv_path)
        for club in clubs:
            db_club = ClubORM(id=club['club_id'], club_name=club['club_name'], league_id=club['league_id'])
            db.add(db_club)
        db.commit()
        return {"message": "Clubs created successfully"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@app.get("/players/")
def get_players(db: Session = Depends(get_db)):
    players = db.query(PlayerORM).all()
    if not players:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No players found")
    return players

@app.post("/players/")
def create_players(db: Session = Depends(get_db)):
    try:
        players = df_to_dict('../data/clean/players_clean.csv')
        for player in players:
            db.add(PlayerORM(
                id                  = player["player_id"],
                name                = player["name"],
                position            = player["position"],
                last_season         = player["last_season"],
                country_of_birth    = player["country_of_birth"],
                age                 = player["age"],
                height_in_cm        = player["height_in_cm"],
                club_name           = player["club_name"],
                market_value_in_eur = player["market_value_in_eur"],
                league_id           = player["league_id"],
                club_id             = player["club_id"]
            ))
        db.commit()
        return {"message": "Players created successfully"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
