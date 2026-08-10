import tkinter as tk
import chess
from main import find_best_move # Hibrit motorundan hamle çeken fonksiyonun

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ONUR ENGINE v2.0 - Masaüstü")
        self.board = chess.Board()
        self.selected_square = None
        
        # --- RENK PALETİ ---
        self.light_color = "#f0d9b5"
        self.dark_color = "#b58863"
        self.select_color = "#829769" # Kendi taşına tıkladığında çıkacak renk
        self.highlight_color = "#cdd26a" # SON HAMLE VURGUSU İÇİN Lichess sarı/yeşili
        
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
        # Tahtada daha önce hamle yapıldıysa o hamleyi (last_move) yakalıyoruz
        last_move = self.board.peek() if self.board.move_stack else None

        for r in range(8):
            for c in range(8):
                square = chess.square(c, 7 - r)
                piece = self.board.piece_at(square)
                
                # --- KARE RENGİNİ BELİRLEME MANTIĞI ---
                if square == self.selected_square:
                    bg_color = self.select_color # Seçtiğimiz taşın karesi
                elif last_move and (square == last_move.from_square or square == last_move.to_square):
                    bg_color = self.highlight_color # Son hamlenin kalktığı ve konduğu kareleri vurgula
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
            
            # Piyon terfisi kontrolü
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
                piece = self.board.piece_at(clicked_square)
                if piece and piece.color == chess.WHITE:
                    self.selected_square = clicked_square
                    self.draw_board()
                else:
                    self.selected_square = None
                    self.draw_board()

    def bot_turn(self):
        self.status_label.config(text="BetaOne düşünüyor...")
        self.root.update()
        
        bot_move = find_best_move(self.board, depth=3)
        if bot_move:
            self.board.push(bot_move)
            self.draw_board()
            
            if self.board.is_game_over():
                self.status_label.config(text=f"Oyun Bitti! Sonuç: {self.board.result()}")
            else:
                self.status_label.config(text="Sıra sizde!")

if __name__ == "__main__":
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()