import chess
import torch
import numpy as np

# 1. Cihaz Seçimi ve Yapay Zeka Modelinin Yüklenmesi
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class BetaOneNet(torch.nn.Module):
    def __init__(self):
        super(BetaOneNet, self).__init__()
        # 1. Katman (64 Filtre)
        self.conv1 = torch.nn.Conv2d(12, 64, kernel_size=3, padding=1)
        # 2. Katman (128 Filtre)
        self.conv2 = torch.nn.Conv2d(64, 128, kernel_size=3, padding=1)
        # 3. Katman (128 Filtre - Yeni Eklenen Katman)
        self.conv3 = torch.nn.Conv2d(128, 128, kernel_size=3, padding=1)
        
        # Tam Bağlı Katmanlar (Fully Connected)
        self.fc1 = torch.nn.Linear(128 * 8 * 8, 256)
        self.score_output = torch.nn.Linear(256, 1) # Adı fc2'den score_output'a dönüştü

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = torch.relu(self.conv3(x)) # Yeni katman işlemden geçiyor
        
        # Matrisi düzleştiriyoruz
        x = x.view(-1, 128 * 8 * 8)
        
        x = torch.relu(self.fc1(x))
        x = torch.tanh(self.score_output(x)) # -1 ile +1 arasına sıkıştırır
        return x

# Canavarın 1000 oyunluk beynini buraya bağlıyoruz
ai_model = BetaOneNet().to(device)
try:
    ai_model.load_state_dict(torch.load("betaone.pt", map_location=device))
    ai_model.eval()
    print("✅ BetaOne Yapay Zeka Beyni Hibrit Motora Başarıyla Enjekte Edildi!")
except FileNotFoundError:
    print("⚠️ 'betaone.pt' dosyası bulunamadı! Model rastgele tahminler üretecek.")

# 2. Tahtayı Yapay Zekanın Anlayacağı Matrise Çevirme
def board_to_matrix(board):
    matrix = np.zeros((12, 8, 8), dtype=np.float32)
    piece_map = {
        chess.PAWN: 0, chess.KNIGHT: 1, chess.BISHOP: 2, 
        chess.ROOK: 3, chess.QUEEN: 4, chess.KING: 5
    }
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            channel = piece_map[piece.piece_type]
            if piece.color == chess.BLACK:
                channel += 6
            row = 7 - chess.square_rank(square)
            col = chess.square_file(square)
            matrix[channel][row][col] = 1.0
    return matrix

# 3. Gelişmiş Hibrit Puanlama (Yapar Zeka Sezgisi + Klasik Kurallar + Aktivite)
def evaluate_hybrid_board(board):
    # Kesin bitiş durumları kontrolü
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    # A) Saf Yapay Zeka Sezgisi (.pt modelinden gelen puan)
    mat = board_to_matrix(board)
    tensor_input = torch.tensor(mat, dtype=torch.float32).unsqueeze(0).to(device)
    with torch.no_grad():
        ai_score = ai_model(tensor_input).item() * 500  # Puan ölçeğini genişletiyoruz

    # B) Klasik Taş Değerleri (Tembelliği ve kör taş feda etmeyi önlemek için)
    material_score = 0
    piece_values = {
        chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
        chess.ROOK: 500, chess.QUEEN: 900
    }
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            val = piece_values.get(piece.piece_type, 0)
            if piece.color == chess.WHITE:
                material_score += val
            else:
                material_score -= val

    # C) Aktivite (Mobility) Bonusu (Kaleyi git-gel yapmaktan kurtaran kırbaç!)
    mobility_score = len(list(board.legal_moves)) * 2
    if board.turn == chess.BLACK:
        mobility_score = -mobility_score

    # Üç gücü birleştiriyoruz: Sezgi + Materyal + Taş Aktivitesi
    return ai_score + material_score + mobility_score

# 4. ALFA-BETA BUDAMALI HİBRİT MİNİMAX ALGORİTMASI
def minimax_alpha_beta(board, depth, alpha, beta, is_maximizing):
    # Derinlik bittiyse veya oyun durduysa hibrit analiz yap
    if depth == 0 or board.is_game_over():
        return evaluate_hybrid_board(board)

    # Korkaklık ve Konum Tekrarı Kırbacı!
    if board.is_repetition(2):
        return -5000 if is_maximizing else 5000

    if is_maximizing:
        max_eval = -float('inf')
        # Alfa-Beta verimi için hamleleri kabaca sıralayabiliriz (Örn: Önce taş yemeler)
        moves = sorted(board.legal_moves, key=lambda m: board.is_capture(m), reverse=True)
        
        for move in moves:
            board.push(move)
            eval_score = minimax_alpha_beta(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            
            # Alfa-Beta Budama Noktası: Rakip buraya asla izin vermez, dalı kes!
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        moves = sorted(board.legal_moves, key=lambda m: board.is_capture(m), reverse=True)
        
        for move in moves:
            board.push(move)
            eval_score = minimax_alpha_beta(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            
            # Alfa-Beta Budama Noktası
            if beta <= alpha:
                break
        return min_eval

# 5. Ana Hamle Bulucu (Kök Noktası)
def find_best_move(board, depth=5): # Varsayılan gücü depth=5 yapıyoruz! Ultra 9 bunu yer!
    best_move = None
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None

    is_white = (board.turn == chess.WHITE)
    alpha = -float('inf')
    beta = float('inf')

    # Akıllı arama başlangıcı
    if is_white:
        best_score = -float('inf')
        for move in legal_moves:
            board.push(move)
            # Konum tekrarı riskini kapıda engelle
            if board.is_repetition(2):
                board.pop()
                continue
            score = minimax_alpha_beta(board, depth - 1, alpha, beta, False)
            board.pop()
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, score)
    else:
        best_score = float('inf')
        for move in legal_moves:
            board.push(move)
            if board.is_repetition(2):
                board.pop()
                continue
            score = minimax_alpha_beta(board, depth - 1, alpha, beta, True)
            board.pop()
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, score)

    # Eğer her şey kilitlenirse en azından ilk yasal hamleyi yap
    return best_move if best_move else legal_moves[0]