from pydantic import BaseModel, Field
from typing import Optional

class movieItem(BaseModel):
    judul_film: str
    
class babyName(BaseModel):
    jenis_kelamin: str
    jumlah_huruf_minimal: int
    jumlah_huruf_maksimal: int
    jumlah_nama:  int
    judul_film : str
    judul_lagu : str
    tahun_lagu : int
    
# class movieSchema(BaseModel):
#     id : int
#     judul_film: str
#     genres : str
    