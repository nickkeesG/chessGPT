import chess
import random
import json

from query_gpt import GPTPlayer
from custom_chess import move_to_list, execute_move

def random_legal_select(player, past_moves, board):
    '''Randomly select a legal move
    '''
    legal_moves = [m for m in board.legal_moves]

    return move_to_list(random.choice(legal_moves), board)

def random_illegal_select(player, past_moves, board):
    '''Randomly select any move (including illegal moves)
    '''
    piece = random.choice(chess.PIECE_SYMBOLS[1:])
    if board.turn == chess.WHITE:
        piece = piece.upper()

    from_square = random.choice(chess.SQUARE_NAMES) 
    to_square = random.choice(chess.SQUARE_NAMES)

    return [piece, from_square, to_square]

def gpt_legal_select(player, past_moves, board):
    '''Sample a legal move from GPT
    '''
    move, _ = player.play(past_moves, board)
    return move

def gpt_illegal_select(player, past_moves, board):
    '''Sample any move from GPT (including illegal moves)
    '''
    move, _ = player.play(past_moves, board, only_legal = False)
    return move

def adversarial_legal_select(player, past_moves, board):
    '''Adversarially sample a legal move from GPT
    '''
    move, _ = player.play(past_moves, board, adversarial = True)
    return move

def adversarial_illegal_select(player, past_moves, board):
    '''Adversarially sample any move from GPT (including illegal moves)
    '''
    move, _ = player.play(past_moves, board, only_legal = False, adversarial = True)
    return move

GENERATORS = {"RAND_LEGAL": random_legal_select, 
              "RAND_ILLEGAL": random_illegal_select, 
              "GPT_LEGAL": gpt_legal_select, 
              "GPT_ILLEGAL": gpt_illegal_select, 
              "ADV_LEGAL_GPT": adversarial_legal_select,
              "ADV_ILLEGAL_GPT": adversarial_illegal_select}

def generate_trajectory(generator_name, N):
    
    generator = GENERATORS[generator_name]

    board = chess.Board()
    past_moves = []
    player = GPTPlayer('85M_step_20000')

    for i in range(N):
        move = generator(player, past_moves, board)
        #print("\t", move)

        if move is None:
            break
        
        board = execute_move(move, board, only_legal = False)
        past_moves.append(move)

        if board.outcome() != None:
            break

    return past_moves, board

if __name__ == "__main__":
    generator_names = list(GENERATORS.keys())

    results_dict = {} 

    try:
        f = open('trajectories.json', 'r')
        results_dict = json.load(f)
        f.close()
        print("Loaded file")
    except:
        print("Did not load file")
        for name in generator_names:
            resuts_dict[name] = []

    for i in range(100):
        for name in generator_names:
            print(name)
            for j in range(10):
                print("\t\t\t", j)
                past_moves, board = generate_trajectory(name, 40)
                results_dict[name].append({"trajectory": past_moves})

        with open('trajectories.json', 'w') as f:
            print("saved results")
            json.dump(results_dict, f)
        
        

