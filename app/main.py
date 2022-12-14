import jwt

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from tortoise import fields 
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model 
from pydantic import BaseModel
import pickle
import pandas as pd
from model.musicmodel import *
from model.temp import *
from models.serviceModels import babyName
import babygenerator

app = FastAPI(title="Music and Movie Recommender Integration System & Technology 2022/2023")
JWT_SECRET = 'myjwtsecret'

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(50, unique=True)
    password_hash = fields.CharField(128)

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)

User_Pydantic = pydantic_model_creator(User, name='User')
UserIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True)

class musicItem(Model):
    name = fields.TextField(50)
    year = fields.IntField(pk=False, minimum=1925, maximum=2022)
musicPydantic = pydantic_model_creator(musicItem)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

async def authenticate_user(username: str, password: str):
    user = await User.get(username=username)
    if not user:
        return False 
    if not user.verify_password(password):
        return False
    return user 

@app.post('/users', response_model=User_Pydantic)
async def create_user(user: UserIn_Pydantic):
    user_obj = User(username=user.username, password_hash=bcrypt.hash(user.password_hash))
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj)
        
@app.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    user_obj = await User_Pydantic.from_tortoise_orm(user)

    token = jwt.encode(user_obj.dict(), JWT_SECRET)

    return {'access_token' : token, 'token_type' : 'bearer'}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    return await User_Pydantic.from_tortoise_orm(user)
     

async def recom(music: musicPydantic, token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    user = await User.get(id=payload.get('id'))
    if user:
        music_obj = musicItem(name=music.name, year=music.year)
    return await musicPydantic.from_tortoise_orm(music_obj)

@app.post("/musicrecommendation")
async def recommendation(item: musicPydantic = Depends(recom) ):
    songs = recommend_songs([{"name" : item.name, "year" : item.year}], model)
    return songs

@app.post("/mood_generator")
async def generate_mood(item: musicPydantic = Depends(recom)):
    songs = get_music_mood([{"name" : item.name, "year" : item.year}])
    return songs


@app.post("/quotes_generator")
async def generate_quotes(item: musicPydantic = Depends(recom)):
    songs = get_quotes(get_music_mood([{"name" : item.name, "year" : item.year}])['mood'], "only_quotes")
    return songs

@app.post("/quotes_movie_generator")
async def generate_quotes_movie(item: musicPydantic = Depends(recom)):
    songs = get_quotes(get_music_mood([{"name" : item.name, "year" : item.year}])['mood'], "all")
    return songs

@app.post("/generate_all")
async def generate_all(item: musicPydantic = Depends(recom)):
    all = get_all([{"name" : item.name, "year" : item.year}], "mood")
    return all

@app.post("/generate_all_by_lyrics")
async def generate_all_by_lyrics(item: musicPydantic = Depends(recom)):
    all = get_all([{"name" : item.name, "year" : item.year}], "lyrics")
    return all

@app.get('/users/me', response_model=User_Pydantic)
async def get_user(user: User_Pydantic = Depends(get_current_user)):
    return user    


@app.post('/babynamegenerator/')
async def babynames_generator_based_on_movie_and_song(item: babyName, current_user:User = Depends(get_current_user)):
    final_nama = babygenerator.babynameGenerator(item.jenis_kelamin, item.jumlah_huruf_minimal, item.jumlah_huruf_maksimal, item.jumlah_nama, item.judul_film, item.judul_lagu, item.tahun_lagu)
    # result = babygenerator.babynameGenerator(item.judul_film, item.judul_lagu, item.tahun_lagu)
    return final_nama

register_tortoise(
    app, 
    db_url='sqlite://db.sqlite3',
    modules={'models': ['main']},
    generate_schemas=True,
    add_exception_handlers=True
)
