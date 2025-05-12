import random
import time
import math
from collections import Counter

# Rank: 2-14 j=11, q=12, K=13, A=14)
# Suit: hdcs

class PokerBot:
    def __init__(self):
        self.ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        self.suits = ['h', 'd', 'c', 's']
        self.rank_names = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
        
    def create_deck(self):
        return [(rank, suit) for rank in self.ranks for suit in self.suits]
    
    def card_to_string(self, card):
        rank, suit = card
        if rank in self.rank_names:
            rank_str = self.rank_names[rank]
        else:
            rank_str = str(rank)
        return f"{rank_str}{suit}"
    
    def shuffle_deck(self, deck):
        shuffled = deck.copy()
        random.shuffle(shuffled)
        return shuffled
    
    def draw_card(self, deck):
        return deck.pop(0)
    
    def make_decision(self, hole_cards, community_cards, time_limit=10):
        start_time = time.time()
        wins = 0
        simulations = 0
        
        full_deck = self.create_deck()
        known_cards = hole_cards + community_cards
        remaining_deck = [card for card in full_deck if card not in known_cards]
        
        remaining_community_cards = 5 - len(community_cards)
        
        while time.time() - start_time < time_limit:
            deck_copy = remaining_deck.copy()
            random.shuffle(deck_copy)
            opponent_hole_cards = [deck_copy.pop() for _ in range(2)]
            
            simulated_community = community_cards.copy()
            simulated_community.extend([deck_copy.pop() for _ in range(remaining_community_cards)])
            
            player_hand = self.evaluate_hand(hole_cards + simulated_community)
            opponent_hand = self.evaluate_hand(opponent_hole_cards + simulated_community)
            
            if self.compare_hands(player_hand, opponent_hand) >= 0:  # Win or tie
                wins += 1
            
            simulations += 1
        
        win_probability = wins / simulations if simulations > 0 else 0
        decision = "stay" if win_probability >= 0.5 else "fold"
        
        return {
            "decision": decision,
            "win_probability": win_probability,
            "simulations": simulations,
            "elapsed_time": time.time() - start_time
        }
    
    def evaluate_hand(self, cards):
        assert len(cards) == 7, "Hand must contain exactly 7 cards"
        
        best_hand = None
        best_value = -1
        
        for hand in self.get_all_combinations(cards, 5):
            hand_value = self.calculate_hand_value(hand)
            if hand_value > best_value:
                best_value = hand_value
                best_hand = hand
        return best_hand, best_value
    
    def get_all_combinations(self, cards, r):
        result = []
        self._generate_combinations(cards, r, 0, [], result)
        return result
    
    def _generate_combinations(self, cards, r, index, current, result):
        if len(current) == r:
            result.append(current[:])
            return
        
        if index >= len(cards):
            return
        current.append(cards[index])
        self._generate_combinations(cards, r, index + 1, current, result)

        current.pop()
        self._generate_combinations(cards, r, index + 1, current, result)

    def calculate_hand_value(self, hand):
        assert len(hand) == 5, "Hand must contain exactly 5 cards"
        sorted_hand = sorted(hand, key=lambda x: x[0], reverse=True)
        if self.is_flush(hand) and self.is_straight(hand):
            return 8 * 10**10 + self.high_card_value(sorted_hand)
        if self.is_four_of_a_kind(hand):
            rank_counts = Counter([card[0] for card in hand])
            four_rank = max(rank_counts.keys(), key=lambda x: rank_counts[x] if rank_counts[x] == 4 else 0)
            kicker_rank = min(rank_counts.keys(), key=lambda x: rank_counts[x] if rank_counts[x] == 1 else 15)
            return 7 * 10**10 + four_rank * 10**5 + kicker_rank
        if self.is_full_house(hand):
            rank_counts = Counter([card[0] for card in hand])
            three_rank = max(rank_counts.keys(), key=lambda x: rank_counts[x] if rank_counts[x] == 3 else 0)
            two_rank = max(rank_counts.keys(), key=lambda x: rank_counts[x] if rank_counts[x] == 2 else 0)
            return 6 * 10**10 + three_rank * 10**5 + two_rank
        if self.is_flush(hand):
            return 5 * 10**10 + self.high_card_value(sorted_hand)
        if self.is_straight(hand):
            return 4 * 10**10 + self.high_card_value(sorted_hand)
        if self.is_three_of_a_kind(hand):
            rank_counts = Counter([card[0] for card in hand])
            three_rank = max(rank_counts.keys(), key=lambda x: rank_counts[x] if rank_counts[x] == 3 else 0)
            kickers = sorted([r for r in rank_counts.keys() if rank_counts[r] == 1], reverse=True)
            return 3 * 10**10 + three_rank * 10**5 + kickers[0] * 10**3 + kickers[1]
        if self.is_two_pair(hand):
            rank_counts = Counter([card[0] for card in hand])
            pairs = sorted([r for r in rank_counts.keys() if rank_counts[r] == 2], reverse=True)
            kicker = next(r for r in rank_counts.keys() if rank_counts[r] == 1)
            return 2 * 10**10 + pairs[0] * 10**5 + pairs[1] * 10**3 + kicker
        if self.is_one_pair(hand):
            rank_counts = Counter([card[0] for card in hand])
            pair_rank = max(rank_counts.keys(), key=lambda x: rank_counts[x] if rank_counts[x] == 2 else 0)
            kickers = sorted([r for r in rank_counts.keys() if rank_counts[r] == 1], reverse=True)
            return 1 * 10**10 + pair_rank * 10**5 + kickers[0] * 10**3 + kickers[1] * 10 + kickers[2]
        return self.high_card_value(sorted_hand)

    def high_card_value(self, sorted_hand):
        value = 0
        multiplier = 1
        for card in sorted_hand:
            value += card[0] * multiplier
            multiplier *= 100
        return value

    def is_flush(self, hand):
        return len(set(card[1] for card in hand)) == 1

    def is_straight(self, hand):
        ranks = sorted([card[0] for card in hand])

        #ace
        if set(ranks) == {14, 2, 3, 4, 5}:
            return True
        return len(set(ranks)) == 5 and max(ranks) - min(ranks) == 4

    def is_four_of_a_kind(self, hand):
        rank_counts = Counter([card[0] for card in hand])
        return 4 in rank_counts.values()

    def is_full_house(self, hand):
        rank_counts = Counter([card[0] for card in hand])
        return 3 in rank_counts.values() and 2 in rank_counts.values()

    def is_three_of_a_kind(self, hand):
        rank_counts = Counter([card[0] for card in hand])
        return 3 in rank_counts.values() and not 2 in rank_counts.values()

    def is_two_pair(self, hand):
        rank_counts = Counter([card[0] for card in hand])
        return list(rank_counts.values()).count(2) == 2

    def is_one_pair(self, hand):
        rank_counts = Counter([card[0] for card in hand])
        return list(rank_counts.values()).count(2) == 1 and not 3 in rank_counts.values()

    def compare_hands(self, hand1, hand2):
        _, value1 = hand1
        _, value2 = hand2

        if value1 > value2:
            return 1
        elif value1 < value2:
            return -1
        else:
            return 0

    def mcts_decision(self, hole_cards, community_cards, time_limit=10):
        start_time = time.time()
        simulations = 0
        wins = 0
        full_deck = self.create_deck()
        known_cards = hole_cards + community_cards
        remaining_deck = [card for card in full_deck if card not in known_cards]
        opponent_hands = {}
        
        while time.time() - start_time < time_limit:
            if simulations > 0:
                if not opponent_hands:
                    for i, card1 in enumerate(remaining_deck):
                        for card2 in remaining_deck[i+1:]:
                            opponent_hands[(card1, card2)] = {"wins": 0, "plays": 0}
                best_ucb = -float('inf')
                opponent_hole_cards = None
                
                for hand, stats in opponent_hands.items():
                    if stats["plays"] == 0:
                        opponent_hole_cards = hand
                        break
                    
                    exploitation = stats["wins"] / stats["plays"]
                    exploration = math.sqrt(2 * math.log(simulations) / stats["plays"])
                    ucb = exploitation + exploration
                    
                    if ucb > best_ucb:
                        best_ucb = ucb
                        opponent_hole_cards = hand
            else:
                deck_copy = remaining_deck.copy()
                random.shuffle(deck_copy)
                opponent_hole_cards = (deck_copy[0], deck_copy[1])
                opponent_hands[opponent_hole_cards] = {"wins": 0, "plays": 0}
            
            available_cards = [card for card in remaining_deck if card not in opponent_hole_cards]
            remaining_community_count = 5 - len(community_cards)
            random.shuffle(available_cards)
            simulated_community = community_cards + available_cards[:remaining_community_count]
            
            player_hand = self.evaluate_hand(hole_cards + simulated_community)
            opponent_hand = self.evaluate_hand(list(opponent_hole_cards) + simulated_community)
            result = self.compare_hands(player_hand, opponent_hand)
            player_win = result >= 0
            
            if player_win:
                wins += 1
            
            simulations += 1
            opponent_hands[opponent_hole_cards]["plays"] += 1
            if player_win:
                opponent_hands[opponent_hole_cards]["wins"] += 1
        
        win_probability = wins / simulations if simulations > 0 else 0
        decision = "stay" if win_probability >= 0.5 else "fold"
        
        return {
            "decision": decision,
            "win_probability": win_probability,
            "simulations": simulations,
            "elapsed_time": time.time() - start_time
        }

def deal_random_cards(deck, num_cards):
    dealt_cards = []
    for _ in range(num_cards):
        if not deck:
            raise ValueError("Deck is empty, cannot deal more cards")
        card_index = random.randint(0, len(deck) - 1)
        dealt_cards.append(deck.pop(card_index))
    return dealt_cards

def main():
    bot = PokerBot()
    
    # Create and shuffle a new deck
    deck = bot.create_deck()
    random.shuffle(deck)
    
    # preflop
    hole_cards = deal_random_cards(deck, 2)
    print(f"Your hole cards: {[bot.card_to_string(card) for card in hole_cards]}")
    result = bot.make_decision(hole_cards, [])

    print("Pre-flop")
    print(f"Decision: {result['decision']}")
    print(f"Win probability: {result['win_probability']:.4f}")
    print(f"Simulations run: {result['simulations']}")
    print(f"Time used: {result['elapsed_time']:.2f} seconds")

    if result['decision'] == "fold":
        return
    
    
    # flop
    community_cards = deal_random_cards(deck, 3)
    print(f"\nFlop: {[bot.card_to_string(card) for card in community_cards]}")
    result = bot.mcts_decision(hole_cards, community_cards)
    print("\nPre-turn")
    print(f"Decision: {result['decision']}")
    print(f"Win probability: {result['win_probability']:.4f}")
    print(f"Simulations run: {result['simulations']}")
    print(f"Time used: {result['elapsed_time']:.2f} seconds")
    
    if result['decision'] == "fold":
        return
    
    # turn
    turn_card = deal_random_cards(deck, 1)[0]
    community_cards.append(turn_card)

    print(f"\nTurn: {bot.card_to_string(turn_card)}")
    print(f"Community cards: {[bot.card_to_string(card) for card in community_cards]}")
    result = bot.mcts_decision(hole_cards, community_cards, time_limit=10)
    print("\nPre-river")
    print(f"Decision: {result['decision']}")
    print(f"Win probability: {result['win_probability']:.4f}")
    print(f"Simulations run: {result['simulations']}")
    print(f"Time used: {result['elapsed_time']:.2f} seconds")
    
    if result['decision'] == "fold":
        return
    
    # river
    river_card = deal_random_cards(deck, 1)[0]
    community_cards.append(river_card)
    print(f"\nRiver: {bot.card_to_string(river_card)}")
    print(f"Community cards: {[bot.card_to_string(card) for card in community_cards]}")
    
    # opponent
    if result['decision'] == "stay":
        opponent_hole_cards = deal_random_cards(deck, 2)
        print(f"\nOpponent's hole cards: {[bot.card_to_string(card) for card in opponent_hole_cards]}")
        
        player_hand, player_value = bot.evaluate_hand(hole_cards + community_cards)
        opponent_hand, opponent_value = bot.evaluate_hand(opponent_hole_cards + community_cards)
        
        result = bot.compare_hands((player_hand, player_value), (opponent_hand, opponent_value))
        
        if result > 0:
            print("\nYou win!")
        elif result < 0:
            print("\nOpponent wins!")
        else:
            print("\nIt's a tie!")
        
        print(f"Your best hand: {[bot.card_to_string(card) for card in player_hand]}")
        print(f"Opponent's best hand: {[bot.card_to_string(card) for card in opponent_hand]}")

if __name__ == "__main__":
    main()

