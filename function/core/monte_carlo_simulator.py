import json
import csv
import random
from collections import Counter
import matplotlib.pyplot as plt

class MonteCarloSimulator:
    def __init__(self,
                 deck_data_csv,
                 cards_info_path,
                 init_conditions_path,
                 log_path,
                 result_path,
                 trial_count=100000):

        self.deck_data_csv = deck_data_csv
        self.cards_info_path = cards_info_path
        self.init_conditions_path = init_conditions_path
        self.log_path = log_path
        self.result_path = result_path
        self.trial_count = trial_count

        self.deck_data = self.load_deck_csv(deck_data_csv)
        self.cards_info = self.load_json(cards_info_path)
        self.init_conditions = self.load_json(init_conditions_path)
        self.deck = self.create_deck()
        self.success_counter = Counter()
        self.fail_counter = Counter()

    def load_json(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_deck_csv(self, path):
        deck = {}
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    name = row[0].strip()
                    try:
                        count = int(row[1].strip())
                        deck[name] = count
                    except ValueError:
                        continue
        return deck

    def create_deck(self):
        deck = []
        for name, count in self.deck_data.items():
            deck.extend([name] * count)
        return deck

    def is_expandable(self, hand):
        for card in hand:
            condition = self.init_conditions.get(card)
            if condition is None:
                continue

            if condition.get("必要枚数", 0) == 0:
                return True  # 単体初動

            others = [c for c in hand if c != card]
            match_count = sum(
                any(keyword in self.cards_info.get(c, {}).get("info", "") for keyword in condition["依存フィルタ"])
                for c in others
            )
            if match_count >= condition["必要枚数"]:
                return True

        return False

    def run_simulation(self):
        with open(self.log_path, 'w', encoding='utf-8') as log:
            for i in range(1, self.trial_count + 1):
                hand = random.sample(self.deck, 5)
                if self.is_expandable(hand):
                    self.success_counter.update(hand)
                    log.write(f"[{i}] 展開成功: {hand}\n")
                else:
                    self.fail_counter.update(hand)
                    log.write(f"[{i}] 展開失敗: {hand}\n")

        self.export_result()
        self.plot_graph()

    def export_result(self):
        results = {}
        all_cards = set(self.success_counter.keys()) | set(self.fail_counter.keys())
        with open(self.result_path, 'w', encoding='utf-8') as f:
            f.write("カード名,寄与率,成功回数,失敗回数\n")
            for card in sorted(all_cards):
                success = self.success_counter[card]
                fail = self.fail_counter[card]
                total = success + fail
                rate = success / total if total > 0 else 0.0
                results[card] = rate
                f.write(f"{card},{rate:.4f},{success},{fail}\n")

    def plot_graph(self):
        card_scores = {
            card: self.success_counter[card] / (self.success_counter[card] + self.fail_counter[card])
            for card in set(self.deck)
            if (self.success_counter[card] + self.fail_counter[card]) > 0
        }
        sorted_items = sorted(card_scores.items(), key=lambda x: x[1])

        names = [name for name, _ in sorted_items]
        values = [score for _, score in sorted_items]

        plt.figure(figsize=(12, 6))
        plt.barh(names, values, color='skyblue')
        plt.xlabel("寄与率")
        plt.title("カード別寄与率（展開成功の貢献度）")
        plt.tight_layout()
        plt.savefig(self.result_path.replace(".txt", ".png"))
        plt.close()

# --- 使用例 ---
simulator = MonteCarloSimulator(
	deck_data_csv=r'D:\_user_template_\Documents\PG\python_game_play_ygo_3\resource\Deck1.csv',
	cards_info_path=r'D:\_user_template_\Documents\PG\python_game_play_ygo_3\resource\image\cards_info.json',
	init_conditions_path=r'D:\_user_template_\Documents\PG\python_game_play_ygo_3\resource\image\init_conditions.json',
	log_path=r'D:\_user_template_\Documents\PG\python_game_play_ygo_3\export\log\sim_log.txt',
	result_path=r'D:\_user_template_\Documents\PG\python_game_play_ygo_3\export\log\sim_result.txt',
	trial_count=100000
 )
simulator.run_simulation()
