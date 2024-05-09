import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

from evil_player import EvilPlayer
from raise_player import RaisedPlayer
from random_player import RandomPlayer
from Group11Player import Group11Player
from call_player import CallPlayer
import random as rand
import matplotlib.pyplot as plt
from pypokerengine.api.game import setup_config, start_poker

#WEIGHTS:
#TRIFOLD_0 0 - 1
#TRIFOLD_1 0 - 1
#TRIFOLD_2 0 - 1
#TRIFOLD_3 0 - 1

## Percentage to call over raise
#SUIT_CALL 0 ~ 1
#NUMBER_CALL 0 ~ 1
#HIGH_CALL 0 ~ 1

## 1 - 10, bad is lower
#BAD_HAND 0 - 9
#MID_HAND 0 - 9

class trainEvilJr():

    def __init__(self):
        self.weights = [0,0,0,0,0,0,0,1,4]
        self.override_accept_rate = 0.1
        self.update_rate = 0.5
        self.fade_rate = 0.99
        self.mem = [[0], [0], [0], [0], [0], [0], [0], [0], [0]]
        self.runs = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.weight_names = ['TRIFOLD_0',
                             'TRIFOLD_1',
                             'TRIFOLD_2',
                             'TRIFOLD_3',
                             'SUIT_CALL',
                             'NUMBER_CALL',
                             'HIGH_CALL',
                             'BAD_HAND',
                             'MID_HAND']

    # Returns override rate
    def update_random_weight(self):
        chosen_weight = rand.randint(0, len(self.weights) - 3)
        init_value = self.weights[chosen_weight]
        override_rate = self.override_accept_rate * self.fade_rate**(self.runs[chosen_weight])
        self.runs[chosen_weight] = self.runs[chosen_weight] + 1

        if chosen_weight < 7:
            # TODO: Decide better algorithm
            modification = rand.uniform(-self.update_rate, self.update_rate)
            modification *= self.fade_rate**self.runs[chosen_weight]
            new_value = init_value + modification
            # print("NEW_VALUE = ", new_value)
            new_value = max(min(new_value, 1), 0)
            # new_value = abs(new_value % 1)
            # print("NEW_VALUE = ", new_value)
        else:
            if rand.uniform(-1, 1) < 0:
                new_value = init_value + 1
                if chosen_weight == 7 and new_value == self.weights[8]:
                    return override_rate
                elif new_value > 9:
                    return override_rate
            else:
                new_value = init_value - 1
                if chosen_weight == 8 and new_value == self.weights[7]:
                    return override_rate
                elif new_value < 0:
                    return override_rate

        self.weights[chosen_weight] = new_value
        self.mem[chosen_weight].append(new_value)
        return override_rate

    def get_plots(self):
        for i in range(len(self.mem)):
            print("X = ", list(range(len(self.mem[i]))))
            print("Y = ", self.mem[i])
            plt.plot(list(range(len(self.mem[i]))), self.mem[i], color='pink')
            plt.title(f"{self.weight_names[i]} over {len(self.mem[i])} updates")
            plt.ylabel(f"{self.weight_names[i]}")
            plt.xlabel("Number of Updates")
            plt.savefig(f"plot_output/weight_plt_{self.weight_names[i]}")
            plt.show()

    def play_game(self, you, enemy):
        config = setup_config(max_round=1000, initial_stack=1000, small_blind_amount=10)
        config.register_player(name="you", algorithm=you)
        config.register_player(name="enemy", algorithm=enemy)
        game_result = start_poker(config, verbose=0)
        your_pot = game_result['players'][0]['stack']
        enemy_pot = game_result['players'][1]['stack']
        return your_pot > enemy_pot

    def train(self, iters):
        # known_good_weights = [0.3281547950071396, 0.8747720058096283, 0.5847482152699021, 0.7214578804204361, 0.012928631272851085, 0.5746492140001189, 0.4095508933413212, 1, 4]
        known_experts = [EvilPlayer(), RaisedPlayer(), CallPlayer()]
        random_weights = [*[rand.uniform(0, 1) for x in range(7)], rand.randint(0, 8)]
        random_weights.append(rand.randint(random_weights[7] + 1, 9))

        # print(random_weights)

        random_trained_expert = Group11Player(random_weights)
        experts = [*known_experts, random_trained_expert]

        for i in range(iters):
            print(i)
            expert = rand.choice(experts[:3])
            # expert = experts[0]
            override_rate = self.update_random_weight()
            new_agent = Group11Player(self.weights)
            if rand.uniform(0, 1) < override_rate:
                experts[len(experts) - 1] = new_agent
            else:
                agent_won = self.play_game(new_agent, expert)
                if agent_won:
                    experts[len(experts) - 1] = new_agent

        print(f"runs: {sum(self.runs)}")
        self.get_plots()

def play_game(you, enemy):
        config = setup_config(max_round=1000, initial_stack=1000, small_blind_amount=10)
        config.register_player(name="you", algorithm=you)
        config.register_player(name="enemy", algorithm=enemy)
        game_result = start_poker(config, verbose=0)
        your_pot = game_result['players'][0]['stack']
        enemy_pot = game_result['players'][1]['stack']
        return your_pot > enemy_pot

def train_hand_cutoffs(weights, iters):
    win_rate_matrix = [[], [], [], [], [], [], [], [], [], []]
    known_experts = [EvilPlayer(), RaisedPlayer(), CallPlayer()]
    trained_expert = Group11Player(weights)
    experts = [*known_experts, trained_expert]

    best_i = trained_expert.weights[7]
    best_j = trained_expert.weights[8]
    best_wr = 0

    for i in list(range(10)):
        for j in list(range(10)):
            if j >= i:
                new_weights = [*weights]
                new_weights[7] = i
                new_weights[8] = j
                print(new_weights)
                new_expert = Group11Player(new_weights)
                win_rate = 0
                for _ in range(iters):
                    expert = rand.choice(experts[:3])
                    if play_game(new_expert, expert):
                        print(f"{i, j} You win")
                        win_rate += 1
                    else:
                        print(f"{i, j} You lose")
                win_rate = win_rate/iters
                if win_rate > best_wr:
                    best_wr = win_rate
                    best_i = i
                    best_j = j
            win_rate_matrix[i].append(win_rate)
    print(best_i, best_j)
    print(win_rate_matrix)
    return best_i, best_j, win_rate_matrix


#INSPIRED BY RANDOM STACKOVERFLOW POST
def plot_hand_cutoffs(best_i, best_j, data):
    ax = plt.axes(projection="3d")
    z = np.array(data)
    y = np.arange(len(z))
    x = np.arange(len(z[0]))
    (x ,y) = np.meshgrid(x,y)
    ax.plot_surface(x,y,z)
    ax.set(xlabel = "MID HAND", ylabel = "BAD HAND", zlabel = "WIN RATE", title= f"WIN RATE over HAND CUTOFFS\nMAX AT {best_i, best_j}")
    plt.show()


if __name__ == '__main__':
    professor = trainEvilJr()
    best_i, best_j, data = train_hand_cutoffs([0.3281547950071396, 0.8747720058096283, 0.5847482152699021, 0.7214578804204361, 0.012928631272851085, 0.5746492140001189, 0.4095508933413212, 1, 4], 100)
    plot_hand_cutoffs(best_i, best_j, data)
    #professor.train(5000)
    #print(professor.weights)
