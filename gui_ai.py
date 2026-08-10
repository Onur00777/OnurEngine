import tkinter as tk
import chess
import torch
import torch.nn as nn
import numpy as np

# 1. Colab'deki Sinir Ağı Mimarisi ile Birebir Aynı Yapıyı Kuruyoruz
class BetaOneNet(nn.Module):
    def __init__(self):
        super(BetaOneNet, self).__init__()
        self.conv1 = nn.Conv2d(12, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(128, 128, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(128 * 8 * 8, 256)
        self.score_output = nn.Linear(256, 1)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = torch.relu(self.conv3(x))
        x = x.view(-1, 128 * 8 * 8)
        x = torch.relu(self.fc1(x))
        return torch.tanh(self.score_output(x))

# 2. Tahtayı Sayılara Döndüren Yardımcı Fonksiyon
def board_to_matrix(board):
    matrix = np.zeros((12, 8, 8), dtype=np.float32)
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            piece_type = piece.piece_type - 1
            color_offset = 0 if piece.color == chess.WHITE else 6
            layer = piece_type + color_offset
            row = 7 - chess.square_rank(square)
            col = chess.square_file(square)
            matrix[layer][row][col] = 1.0
    return torch.tensor(matrix).unsqueeze(0)

# Beyni Yüklüyoruz
device = torch.device("cpu") # Masaüstünde tahmin yaparken CPU (Ultra 9) fazlasıyla yeterli ve hiç yorulmaz!
ai_model = BetaOneNet()
try:
    ai_model.load_state_dict(torch.load("betaone.pt", map_location=device))
    ai_model.eval()
    print("-> BetaOne Satranç Beyni Başarıyla Laptopa Yüklendi!")
except FileNotFoundError:
    print("HATA: 'betaone.pt' dosyası bulunamadı! Lütfen Colab'den indirip bu klasöre atın.")

# 3. ARAYÜZ SINIFI
class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BETAONE v1.0 - Real AI Engine")
        self.board = chess.Board()
        self.selected_square = None
        
        self.light_color = "#f0d9b5"
        self.dark_color = "#b58863"
        self.select_color = "#829769"
        self.highlight_color = "#cdd26a" # Son hamle vurgusu
        
        self.piece_symbols = {
            'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
            'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'
        }
        
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        self.create_widgets()
        self.draw_board()

    def create_widgets(self):
        self.status_label = tk.Label(self.root, text="Sıra sizde! (Beyazlar)", font=("Helvetica", 14, "bold"), pady=10)
        self.status_label.pack()
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack()
        
        for r in range(8):
            for c in range(8):
                btn = tk.Button(self.board_frame, font=("Courier", 32), width=3, height=1,
                                command=lambda row=r, col=c: self.square_clicked(row, col))
                btn.grid(row=r, column=c)
                self.buttons[r][c] = btn

    def draw_board(self):
        last_move = self.board.peek() if self.board.move_stack else None
        for r in range(8):
            for c in range(8):
                square = chess.square(c, 7 - r)
                piece = self.board.piece_at(square)
                
                if square == self.selected_square:
                    bg_color = self.select_color
                elif last_move and square in (last_move.from_square, last_move.to_square):
                    bg_color = self.highlight_color
                else:
                    bg_color = self.light_color if (r + c) % 2 == 0 else self.dark_color
                    
                text = self.piece_symbols.get(piece.symbol(), "") if piece else ""
                self.buttons[r][c].config(text=text, bg=bg_color, activebackground=bg_color)
        self.root.update()

    def square_clicked(self, row, col):
        if self.board.is_game_over() or self.board.turn == chess.BLACK:
            return
            
        clicked_square = chess.square(col, 7 - row)
        
        if self.selected_square is None:
            piece = self.board.piece_at(clicked_square)
            if piece and piece.color == chess.WHITE:
                self.selected_square = clicked_square
                self.draw_board()
        else:
            move = chess.Move(self.selected_square, clicked_square)
            piece = self.board.piece_at(self.selected_square)
            if piece and piece.piece_type == chess.PAWN and chess.square_rank(clicked_square) in [0, 7]:
                move.promotion = chess.QUEEN
                
            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None
                self.draw_board()
                
                if self.board.is_game_over():
                    self.status_label.config(text=f"Oyun Bitti! Sonuç: {self.board.result()}")
                else:
                    self.bot_turn()
            else:
                self.selected_square = None
                self.draw_board()

    def bot_turn(self):
        self.status_label.config(text="BetaOne Sinir Ağını Çalıştırıyor...")
        self.root.update()
        
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return

        best_move = None
        best_score = float('inf') # Siyah (AI) en düşük skoru (kendisi lehine olanı) arıyor
        
        # Gerçek AI Seçim Mantığı: Tüm hamleleri sinir ağına soruyoruz
        for move in legal_moves:
            self.board.push(move)
            with torch.no_grad():
                matrix = board_to_matrix(self.board)
                score = ai_model(matrix).item()
            self.board.pop()
            
            if score < best_score:
                best_score = score
                best_move = move
        
        if best_move:
            self.board.push(best_move)
            self.draw_board()
            if self.board.is_game_over():
                self.status_label.config(text=f"Oyun Bitti! Sonuç: {self.board.result()}")
            else:
                self.status_label.config(text="Sıra sizde!")

if __name__ == "__main__":
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()