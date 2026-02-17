import copy
import random

from chess_to_the_death.entity.player import Player
from chess_to_the_death.util.definition import Outcome, PieceChar, PieceValues


def choose_move(game_state, depth: int = 3):
    """
    Return a (from_pos, to_pos) tuple for the best move found.
    """
    max_player = game_state.currentPlayer()
    moves = _get_all_moves(game_state)
    if not moves:
        return None

    best_score = None
    best_moves = []
    for from_pos, to_pos in moves:
        next_state = _simulate_move(game_state, from_pos, to_pos)
        if not next_state:
            continue
        score = _minimax(next_state, depth - 1, max_player, False, -10**9, 10**9)
        if best_score is None or score > best_score:
            best_score = score
            best_moves = [(from_pos, to_pos)]
        elif score == best_score:
            best_moves.append((from_pos, to_pos))

    if not best_moves:
        return None
    return random.choice(best_moves)


def _minimax(game_state, depth: int, max_player: str, is_max: bool, alpha: float, beta: float):
    terminal_score = _terminal_score(game_state, max_player)
    if terminal_score is not None:
        return terminal_score
    if depth <= 0:
        return _evaluate(game_state, max_player)

    moves = _get_all_moves(game_state)
    if not moves:
        return _evaluate(game_state, max_player)

    if is_max:
        best = -10**9
        for from_pos, to_pos in moves:
            next_state = _simulate_move(game_state, from_pos, to_pos)
            if not next_state:
                continue
            score = _minimax(next_state, depth - 1, max_player, False, alpha, beta)
            if score > best:
                best = score
            alpha = max(alpha, best)
            if beta <= alpha:
                break  # Beta cutoff
        return best

    best = 10**9
    for from_pos, to_pos in moves:
        next_state = _simulate_move(game_state, from_pos, to_pos)
        if not next_state:
            continue
        score = _minimax(next_state, depth - 1, max_player, True, alpha, beta)
        if score < best:
            best = score
        beta = min(beta, best)
        if beta <= alpha:
            break  # Alpha cutoff
    return best


def _simulate_move(game_state, from_pos: tuple, to_pos: tuple):
    next_state = copy.deepcopy(game_state)

    piece = next_state.getPiece(from_pos)
    if not piece:
        return None
    options_move, options_attack = next_state.getOptions(piece)
    action = next_state.action(piece, to_pos, options_move, options_attack)
    if not action:
        return None

    if action == Outcome.PAWN_PROMOTION:
        next_state.placePiece(to_pos, PieceChar.QUEEN)
    if action != Outcome.GAME_FINISHED:
        next_state.nextTurn(False)
    return next_state


def _get_all_moves(game_state):
    moves = []
    for piece in game_state.pieces:
        if piece._player != game_state.currentPlayer():
            continue
        options_move, options_attack = game_state.getOptions(piece)
        from_pos = piece.getPos()
        for pos in options_move + options_attack:
            moves.append((from_pos, pos))
    return moves


def _terminal_score(game_state, max_player: str):
    outcome = game_state.playerWon()
    if outcome == Outcome.NONE:
        return None
    if outcome in (Outcome.DRAW, Outcome.DRAW_REPITITION, Outcome.STALEMATE):
        return 0
    if outcome in (Outcome.WHITE_WON, Outcome.BLACK_WON):
        winner = Player.PLAYER_W if outcome == Outcome.WHITE_WON else Player.PLAYER_B
        return 10**6 if max_player == winner else -10**6
    return 0


def _evaluate(game_state, max_player: str) -> float:
    score = 0.0
    for piece in game_state.pieces:
        value = PieceValues.VALUES[piece._name]
        value += piece.health / max(piece.maxHealth, 1)
        value += piece.damage / 100.0
        if piece._player == max_player:
            score += value
        else:
            score -= value
    return score
