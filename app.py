from flask import Flask, render_template_string, request, jsonify
import chess
from main import find_best_move

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>BetaOne by Onur Yüksek</title>
    <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>
    <style>
        body { 
            background-color: #121214; 
            color: #e4e4e7; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            height: 100vh; 
            margin: 0; 
            padding: 20px;
        }
        h1 { margin-bottom: 10px; color: #f4f4f5; font-size: 28px; letter-spacing: 1px; }
        #board { width: 480px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.75); border: 4px solid #3f3f46; border-radius: 6px; overflow: hidden; }
        .status-box { margin-top: 25px; background-color: #27272a; padding: 14px 28px; border-radius: 8px; border: 1px solid #3f3f46; font-size: 16px; font-weight: 600; min-width: 250text-align: center; box-shadow: inset 0 2px 4px rgba(0,0,0,0.3); }
        
        /* Son yapılan hamlenin karelerini vurgulamak için şık bir efekt */
        .highlight-move {
            box-shadow: inset 0 0 3px 3px rgba(245, 158, 11, 0.7) !important;
            background-color: rgba(245, 158, 11, 0.3) !important;
        }
    </style>
</head>
<body>
    <h1>BetaOne by Onur Yüksek</h1>
    <div id="board"></div>
    <div class="status-box" id="status">⚪ Sıra Sende, Hamleni Yap!</div>

    <script>
        var board = null;
        var fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

        function removeHighlights() {
            $('#board .square-55d63').removeClass('highlight-move');
        }

        function highlightMove(source, target) {
            removeHighlights();
            $('#board .square-' + source).addClass('highlight-move');
            $('#board .square-' + target).addClass('highlight-move');
        }

        function onDragStart (source, piece, position, orientation) {
            if (piece.search(/^b/) !== -1 || $('#status').text().includes('Analiz')) {
                return false;
            }
        }

        function onDrop (source, target) {
            if (source === target) return;
            
            var moveUCI = source + target;
            $('#status').text('⚫ BetaOne Analiz Yapıyor (Derinlik: 3)...');

            $.ajax({
                url: '/make_move',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ fen: fen, move: moveUCI }),
                success: function (data) {
                    if (data.error) {
                        $('#status').text('⚪ Sıra Sende, Hamleni Yap!');
                        board.position(fen, false);
                    } else {
                        // Oyuncunun hamlesini görsel olarak işaretle
                        highlightMove(source, target);
                        
                        fen = data.next_fen;
                        board.position(fen);
                        
                        // Eğer bot bir karşılık verdiyse onun hamlesini de tahtada parlat!
                        if (data.bot_move) {
                            var botSrc = data.bot_move.substring(0, 2);
                            var botTgt = data.bot_move.substring(2, 4);
                            setTimeout(function() {
                                highlightMove(botSrc, botTgt);
                                if (data.is_over) {
                                    $('#status').text('🏁 Oyun Bitti!');
                                } else {
                                    $('#status').text('⚪ Sıra Sende, Hamleni Yap!');
                                }
                            }, 250);
                        } else {
                            if (data.is_over) $('#status').text('🏁 Oyun Bitti!');
                        }
                    }
                },
                error: function() {
                    alert("Sunucu bağlantısı koptu!");
                    $('#status').text('⚪ Sıra Sende, Hamleni Yap!');
                }
            });
        }

        var config = {
            draggable: true,
            position: 'start',
            onDragStart: onDragStart,
            onDrop: onDrop,
            // Şık cboard.com modern taş setini internetten çekiyoruz
            pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png'
        };
        board = ChessBoard('board', config);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/make_move', methods=['POST'])
def make_move():
    data = request.json
    current_fen = data.get('fen')
    user_move_uci = data.get('move')
    
    board = chess.Board(current_fen)
    
    try:
        move = chess.Move.from_uci(user_move_uci)
        if move in board.legal_moves:
            board.push(move)
        else:
            move_promo = chess.Move.from_uci(user_move_uci + "q")
            if move_promo in board.legal_moves:
                board.push(move_promo)
            else:
                return jsonify({"error": "Geçersiz hamle"})
    except:
        return jsonify({"error": "Geçersiz hamle"})
        
    if board.is_game_over():
        return jsonify({"next_fen": board.fen(), "bot_move": None, "is_over": True})
        
    bot_move = find_best_move(board, depth=3)
    
    if bot_move:
        board.push(bot_move)
        return jsonify({
            "next_fen": board.fen(),
            "bot_move": bot_move.uci(),
            "is_over": board.is_game_over()
        })
        
    return jsonify({"next_fen": board.fen(), "bot_move": None, "is_over": board.is_game_over()})

if __name__ == '__main__':
    app.run(debug=True, port=5000)