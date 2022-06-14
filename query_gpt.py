import chess
import requests
import torch
from torch.nn import functional as F
from typing import List

from custom_chess import move_to_list

EPSILON = 0.00000001 

class GPTPlayer():
    ''' Chess player capable of querying GPT 
    '''
    
    def __init__(self, model_name):
        self.model_name = model_name

    def play(self, 
             past_moves: List[List], 
             board: chess.Board,
             only_legal = True,
             adversarial = False):
        
        legal_moves = [move_to_list(m, board) for m in board.legal_moves]

        context = (
            "elo_end " + " ".join([' '.join(m) for m in past_moves])
            if len(past_moves)
            else "elo_end"
        )

        new_move = []
        for k in range(4):
            r = self.request_API(context, 1)
            logits = torch.tensor(list(r.json()["logprobs"][0].values()))
            returned_moves = list(r.json()["logprobs"][0].keys())
            probs = F.softmax(logits, dim=-1)

            #invert the probability distribution if adversarial
            if adversarial:
                probs = [1 / (p + EPSILON) for p in probs]
                probs = [p / sum(probs) for p in probs]
                probs = torch.tensor(probs)

            if only_legal == True:
                assert not legal_moves is [] , "no legal moves possible"
                legal_tokens = [m[k] for m in legal_moves]
            else:
                if k == 0 or k == 3:
                    legal_tokens = [s for s in chess.PIECE_SYMBOLS[1:]] + [s.upper() for s in chess.PIECE_SYMBOLS[1:]]
                else: 
                    legal_tokens = chess.SQUARE_NAMES
            
            for i, m in enumerate(returned_moves):
                if m not in legal_tokens:
                    probs[i] = 0

            if probs.sum() <= 0:
                for i, m in enumerate(returned_moves):
                    if m in legal_moves:
                        probs[i] = 1

            probs /= probs.sum()

            ix = torch.multinomial(probs, num_samples=1)
            context += f" {returned_moves[ix]}"
            new_move.append(returned_moves[ix])

            legal_moves = [m for m in legal_moves if m[k] == returned_moves[ix]]
            
            if k == 2:
                if ((new_move[0] == 'p' and new_move[2][1] == '1') or
                    (new_move[0] == 'P' and new_move[2][1] == '8')):
                    continue
                else:
                    break

        return new_move, None

    def request_API(self, 
                    prompt, 
                    max_length, 
                    temperature = None,
                    top_k=None,
                    sample_bool = True,
                    headers={"accept": "application/json"},
                    data = ""):

        model_name = self.model_name 
        base_url = "https://adf4-207-53-234-8.ngrok.io/completion?"
        prompt_html = prompt.replace(" ", "%20")
        post_string = f"{base_url}prompt={prompt_html}&max_length={str(max_length)}&model_name={model_name}"

        if temperature is not None:
            post_string += f"&temperature={str(temperature)}"
        if sample_bool is not None:
            post_string += f"&sample={sample_bool}"
        if top_k is not None:
            post_string += f"&top_k={top_k}"

        return requests.post(post_string, headers=headers, data=data)


