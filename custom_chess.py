import chess
from typing import List

def move_to_list(move: chess.Move, board: chess.Board) -> List[str]:
    uci = move.uci()

    start_piece = board.piece_at(move.from_square).symbol()

    #if board.turn == chess.WHITE:
    #    start_piece = start_piece.upper()

    if move.promotion is not None:
        end_piece = chess.piece_symbol(move.promotion)
        if board.turn == chess.WHITE:
            end_piece = end_piece.upper()
        return [start_piece, uci[:2], uci[2:4], end_piece]
    else:
        return [start_piece, uci[:2], uci[2:4]]

def move_to_string(move: chess.Move) -> str:
    l = move_to_list(move)
    return " ".join(l)

def list_to_move(l) -> chess.Move:
    from_square = chess.parse_square(l[1])
    to_square = chess.parse_square(l[2])

    if len(l) > 3:
        symbol = l[3]
        promotion = chess.Piece.from_symbol(l[3]).piece_type
    else:
        promotion = None

    return chess.Move(from_square, to_square, promotion)

#Execute the move. If it is a legal move, it will be interpreted normally. If it is an illegal move, then the space the start square will be made empty, and a piece of the type given by the move will be placed on the end square. If the start square was empty to begin with, a piece will materialize out nothing. If the start square has a different piece type on it, that piece will be converted to whatever piece was given by the move description.
def execute_move(move: List, board: chess.Board, only_legal = True):
    chess_move = list_to_move(move)
    
    if only_legal:
        assert(board.piece_at(chess_move.from_square) != None)
        assert(move[0] == board.piece_at(chess_move.from_square).symbol())
        assert(chess_move in board.legal_moves)
        board.push(chess_move)
    else:
        if ((board.piece_at(chess_move.from_square) != None) and 
          (move[0] == board.piece_at(chess_move.from_square).symbol()) and
          (chess_move in board.legal_moves)):
            board.push(chess_move)
        else:
            if chess_move.promotion:
                piece = chess.Piece(chess_move.promotion, board.turn)
            else:
                piece = chess.Piece.from_symbol(move[0])
            board.remove_piece_at(chess_move.from_square)
            board.set_piece_at(chess_move.to_square, piece)

            board.turn = chess.WHITE if board.turn == chess.BLACK else chess.BLACK

    return board
            

