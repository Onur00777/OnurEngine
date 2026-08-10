from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chess

# main.py dosyamızdaki bot mantığını içeri aktarıyoruz
from main import find_best_move

app = FastAPI()

# Next.js'ten gelecek isteklere izin vermek için CORS ayarı (Çok Önemli!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Next.js'ten gelecek verinin yapısı (FEN formatında tahta dizilimi)
class BoardState(BaseModel):
    fen: str

@app.post("/get_move")
def get_move(state: BoardState):
    # Gelen FEN dizilimini (tahtanın o anki metin halini) satranç tahtasına çevir
    board = chess.Board(state.fen)
    
    # Motorumuza en iyi hamleyi buldur (Şimdilik derinlik 3'te bırakıyoruz)
    best_move = find_best_move(board, depth=3)
    
    if best_move:
        return {"move": best_move.uci()}
    return {"move": None}