import random
from dataclasses import dataclass, field
from typing import Optional

from config import RANKS, CARDS_PER_PLAYER, STARTING_LIVES


def build_deck():
    deck = []
    for rank in RANKS:
        deck.extend([rank] * 4)
    random.shuffle(deck)
    return deck


@dataclass
class Player:
    user_id: int
    username: str
    hand: list = field(default_factory=list)
    lives: int = STARTING_LIVES
    alive: bool = True


@dataclass
class PendingPlay:
    player_id: int
    cards: list
    claimed_rank: str


class GameSession:
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.players: dict[int, Player] = {}
        self.order: list[int] = []
        self.state = "registration"  # registration | playing | finished
        self.turn_index = 0
        self.pending: Optional[PendingPlay] = None

    def add_player(self, user_id, username):
        if user_id in self.players:
            return False
        self.players[user_id] = Player(user_id, username)
        self.order.append(user_id)
        return True

    @property
    def player_count(self):
        return len(self.players)

    def start(self):
        deck = build_deck()
        for uid in self.order:
            p = self.players[uid]
            p.hand = [deck.pop() for _ in range(min(CARDS_PER_PLAYER, len(deck)))]
        self.state = "playing"
        self.turn_index = 0

    def current_player(self) -> Player:
        uid = self.order[self.turn_index]
        return self.players[uid]

    def alive_players(self):
        return [self.players[uid] for uid in self.order if self.players[uid].alive]

    def advance_turn(self):
        n = len(self.order)
        for _ in range(n):
            self.turn_index = (self.turn_index + 1) % n
            if self.players[self.order[self.turn_index]].alive:
                break

    def next_alive_after(self, uid):
        n = len(self.order)
        idx = self.order.index(uid)
        for i in range(1, n + 1):
            cand = self.order[(idx + i) % n]
            if self.players[cand].alive:
                return cand
        return None

    def check_winner(self):
        alive = self.alive_players()
        if len(alive) == 1:
            return alive[0].user_id
        for p in alive:
            if len(p.hand) == 0:
                return p.user_id
        return None


# chat_id -> GameSession
games: dict[int, GameSession] = {}
# user_id -> which chat's game they belong to (for private-chat routing)
active_game_for_user: dict[int, int] = {}
# user_id -> set of hand-card indices currently selected (temp UI state)
selections: dict[int, set] = {}
