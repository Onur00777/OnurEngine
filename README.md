# OnurEngine (BetaOne)

A hybrid chess engine that combines classical chess evaluation with a deep learning model I trained myself. It utilizes a combination of mathematical move calculation and an artificial intelligence network.

The BetaOne model was trained on **Google Colab** (using data from approximately 1,000 games), and the weights (`betaone.pt`) were subsequently transferred to this repository. The engine evaluates the board using a CNN and selects the best move via minimax search. Interfaces for playing the game are also included in the project. ## Features

- **Hybrid evaluation:** PyTorch model (`betaone.pt`) + classical piece values
- **Search:** Minimax-based move selection
- **API:** `POST /get_move` via FastAPI (FEN → UCI move)
- **Interfaces:**
- Flask + chessboard.js (`app.py`)
- Next.js + `react-chessboard` (`satranc-arayuzu/`)

## Project Structure

```
OnurEngine/
├── main.py              # Engine, model, and search logic
├── api.py               # FastAPI backend
├── app.py               # Flask desktop/web interface
├── gui.py / gui_ai.py   # Additional GUI experiments
├── betaone.pt           # Main model weights
├── betaone_alphago.pt   # Alternative model
├── betaone_eski.pt      # Old model backup
└── satranc-arayuzu/     # Next.js chess interface
```

## Requirements

**Python**

- Python 3.10+
- `chess`, `torch`, `numpy`, `fastapi`, `uvicorn`, `flask`, `pydantic`

Example installation:

```bash
pip install -r requirements.txt
```

**Next.js Interface**

- Node.js 18+

```bash
cd satranc-arayuzu
npm install
```

## Running the Project

### 1) Engine API (FastAPI)

From the project root:

```bash
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/get_move ^
-H "Content-Type: application/json" ^
-d "{\"fen\": \"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}"
```

### 2) Flask interface

```bash
python app.py
```

### 3) Next.js interface

Ensure the API is running on port `8000`, then:

```bash
cd satranc-arayuzu
npm run dev
```

Browser: [http://localhost:3000](http://localhost:3000)

You play as White; the engine generates moves for Black.

## Model notes

- Training environment: **Google Colab**
- Weights file: `betaone.pt` in the root directory (downloaded from Colab and placed in the project)
- The engine loads this file; if missing, it will still run, but evaluations will be random/weak
- `betaone_alphago.pt` and `betaone_eski.pt` are alternative/backup weights

## Development ideas

- Make search depth adjustable
- Add an opening book
- Document the model training pipeline in the repository
- Restrict CORS settings for production

## License

Currently a private project. A license may be added in the future.
