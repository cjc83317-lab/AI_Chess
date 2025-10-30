import chess

piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Simplified piece-square tables (mirrored for black)
pawn_table = [
     0,  5,  5, -10, -10,  5,  5,  0,
     0, 10, -5,   0,   0, -5, 10,  0,
     0, 10, 10,  20,  20, 10, 10,  0,
     5, 20, 20,  30,  30, 20, 20,  5,
    10, 20, 20,  30,  30, 20, 20, 10,
     5, 10, 10,  20,  20, 10, 10,  5,
     5,  5,  5, -10, -10,  5,  5,  5,
     0,  0,  0,   0,   0,  0,  0,  0
]

knight_table = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,   0,   5,   5,   0, -20, -40,
    -30,   5,  10,  15,  15,  10,   5, -30,
    -30,   0,  15,  20,  20,  15,   0, -30,
    -30,   5,  15,  20,  20,  15,   5, -30,
    -30,   0,  10,  15,  15,  10,   0, -30,
    -40, -20,   0,   0,   0,   0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

def mirror(table):
    return table[::-1]

def evaluate_board(board):
    if board.is_checkmate():
        return -99999 if board.turn else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            sign = 1 if piece.color == chess.WHITE else -1
            score += sign * value

            # Positional bonus
            if piece.piece_type == chess.PAWN:
                pst = pawn_table if piece.color == chess.WHITE else mirror(pawn_table)
                score += sign * pst[square]
            elif piece.piece_type == chess.KNIGHT:
                pst = knight_table if piece.color == chess.WHITE else mirror(knight_table)
                score += sign * pst[square]

    # Bishop pair bonus
    if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
        score += 30
    if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
        score -= 30

    # King safety (simple): penalize if not castled
    if not board.has_kingside_castling_rights(chess.WHITE) and not board.has_queenside_castling_rights(chess.WHITE):
        score -= 20
    if not board.has_kingside_castling_rights(chess.BLACK) and not board.has_queenside_castling_rights(chess.BLACK):
        score += 20

    return score