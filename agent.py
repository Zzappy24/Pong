import torch
import random
import numpy as np
from collections import deque
from main import PongGame
from model import QTrainer, DQN#, Linear_QNet
from helper import plot
import threading
import time
#from main import collision

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class PongAgent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # Randomness
        self.gamma = 0.9  # Discount rate
        self.epsilon_decay = 0.995
        self.memory = deque(maxlen=MAX_MEMORY)
        #self.model = Linear_QNet(8, 256, 3)  # Pong a 3 actions (monter, descendre, ne rien faire)
        self.model = DQN(5, 256, 3) 
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
    
    def decay_epsilon(self):
        self.epsilon *= self.epsilon_decay

    def get_state(self, game):
        state = []
        indices_derniers_carrés = [20 - 1 + i * 20 for i in range(20)]


        # Ajoutez une représentation binaire de la présence de la balle dans chaque zone
        for i, zone in enumerate(game.zones):
            #if i in [3, 4, 9, 10, 16, 17, 21, 22, 27, 28, 33, 34]:
                if zone.rect.colliderect(game.balle):
                    state.append(1)
                else:
                    state.append(0)
                if i in indices_derniers_carrés and zone.rect.colliderect(game.raquette_droite):
                    state.append(1)
                else:
                    state.append(0)
                
        
                

        # Ajoutez d'autres informations dont vous avez besoin
        state.extend([game.direction_balle_x, game.direction_balle_y])

        return np.array(state, dtype=int)
    

    def get_state2(self, game, final_move):
        # Position de la raquette
        raquette_top = game.raquette_droite.top
        raquette_bottom = game.raquette_droite.bottom
        #print(game.raquette_droite) 
        raquette_temp_bottom = game.raquette_droite.copy()
        raquette_temp_bottom.x -=20
        raquette_temp_bottom.y -= 30
        raquette_temp_up = game.raquette_droite.copy()
        raquette_temp_up.x -=20
        raquette_temp_up.y += 30

        # Position de la balle
        balle_x = game.balle.x
        balle_y = game.balle.y

        # Direction de la balle
        direction_x = game.direction_balle_x
        direction_y = game.direction_balle_y
        #collision_raquette_up = 1 if game.collision(raquette_temp_bottom) else 0
        #collision_raquette_bottom = 1 if game.collision(raquette_temp_up) else 0
        if final_move[0]==1:
            move = 0
        if final_move[1]==1:
            move = 1
        if final_move[2]==1:
            move = 2
        
        #raquette_temp_bottom

        # Construire le state
        state = [
            # Position verticale de la raquette
            #raquette_top,
            #raquette_bottom,

            game.raquette_droite.x,
            game.raquette_droite.y,

            move,
            #collision_raquette_up,
            #collision_raquette_bottom,
            # Position horizontale et verticale de la balle
            balle_x,
            balle_y,

            # Direction de la balle
            #direction_x,
            #direction_y
        ]

        return np.array(state, dtype=int)
        
        """
        def get_state(self, game):
                ball_x, ball_y = game.balle.x, game.balle.y
                racket_y = game.raquette_droite.y

                # Direction de la raquette (vers le haut, vers le bas, ou immobile)
                racket_up = 1 if game.raquette_droite.y < game.hauteur_fenetre // 2 - 50 else 0
                racket_down = 1 if game.raquette_droite.y > game.hauteur_fenetre // 2 - 50 else 0

                # Direction de la balle (vers la gauche, vers la droite)
                ball_left = 1 if game.direction_balle_x == -1 else 0
                ball_right = 1 if game.direction_balle_x == 1 else 0

                # Position relative de la balle par rapport à la raquette (à gauche, à droite, alignée)
                ball_left_of_racket = 1 if ball_x < game.raquette_droite.x else 0
                ball_right_of_racket = 1 if ball_x > game.raquette_droite.x else 0
                ball_aligned_with_racket = 1 if ball_x == game.raquette_droite.x else 0

                state = [
                    racket_y,
                    ball_x,
                    ball_y,
                    racket_up,
                    racket_down,
                    ball_left,
                    ball_right,
                    ball_left_of_racket,
                    ball_right_of_racket,
                    ball_aligned_with_racket
                ]

                return np.array(state, dtype=int)
                """

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):

        print(len(self.memory))
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def train(self, epochs=1):
        for epoch in range(epochs):
            if len(self.memory) > BATCH_SIZE:
                mini_sample = random.sample(self.memory, BATCH_SIZE)
            else:
                mini_sample = self.memory

            states, actions, rewards, next_states, dones = zip(*mini_sample)
            self.trainer.train_step(states, actions, rewards, next_states, dones)

    def get_action(self, state):
        #self.epsilon *= 0.995
        self.epsilon = 200 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 400) < self.epsilon:
            move = random.randint(0, 2)
            print(move) 
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            #print("move", move)
            #print("final_move", final_move)
            #print(final_move, move)
            final_move[move] = 1

        return final_move#move


def train_pong():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = PongAgent()
    game = PongGame(800, 600, 10, 5)


    while True: #agent.n_games < 1000:  # Vous pouvez ajuster le nombre d'épisodes
        #state_old = agent.get_state(game)
        try:
            final_move
        except Exception:
            final_move=[0,0,1]
        
        state_old = agent.get_state2(game,final_move)

        final_move = agent.get_action(state_old)
        score, reward, done= game.step(final_move)
        #state_new = np.array(state_new, dtype=int)

        #state_new = agent.get_state(game)
        state_new = agent.get_state2(game,final_move)


        #print(state_old, state_new)
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent.remember(state_old, final_move, reward, state_new, done)
        #total_score = score
        #print(state_old, state_new)
        #print(score)
        if done or score == 20:
            #print(score)
            #print(len(agent.memory))
            game.reinitialiser_partie()

            agent.n_games += 1
            
            #game = PongGame(800, 600, 5, 2.5)  # Réinitialiser le jeu
            agent.train_long_memory()
            #agent.decay_epsilon()

            if score > record:
                record = score
                agent.model.save()

                plot_scores.append(score)
                total_score += score
                mean_score = total_score / agent.n_games
                plot_mean_scores.append(mean_score)
                print("test")
                plot(plot_scores, plot_mean_scores, True)

            #print('Game', agent.n_games, 'Score', total_score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores,False)
            #total_score = 0
           

def train_pong_epoch():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = PongAgent()
    game = PongGame(800, 600, 10, 5)

    while True:
        state_old = agent.get_state2(game)
        final_move = agent.get_action(state_old)
        score, reward, done = game.step(final_move)
        state_new = agent.get_state2(game, final_move)

        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent.remember(state_old, final_move, reward, state_new, done)

        if done or score == 20:
            game.reinitialiser_partie()
            agent.n_games += 1

            agent.train(epochs=5)  # Choisir le nombre d'époques souhaité

            if score > record:
                record = score
                agent.model.save()

                plot_scores.append(score)
                total_score += score
                mean_score = total_score / agent.n_games
                plot_mean_scores.append(mean_score)
                print("test")
                plot(plot_scores, plot_mean_scores, True)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores, False)


if __name__ == '__main__':
    train_pong()
