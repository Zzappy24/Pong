import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class DQN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        #self.fc2 = nn.Linear(hidden_size, hidden_size)
        #self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.fc4 = nn.Linear(hidden_size, hidden_size)
        self.fc5 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        #x = F.relu(self.fc2(x))
        #x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        x = self.fc5(x)
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.device = torch.device("mps" if torch.cuda.is_available() else "cpu")
        self.model = model.to(self.device)
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float).to(self.device)
        next_state = torch.tensor(next_state, dtype=torch.float).to(self.device)
        action = torch.tensor(action, dtype=torch.long).to(self.device)
        reward = torch.tensor(reward, dtype=torch.float).to(self.device)

        #print(state, done)

        if len(state.shape) == 1:
            state = state.unsqueeze(0)
            next_state = next_state.unsqueeze(0)
            action = action.unsqueeze(0)
            reward = reward.unsqueeze(0)
            #print(done, (done, ))
            done = (done, )

        # 1: predicted Q values with the current state
        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Q_new

        # 2: Q_new = r + y * max(next_predicted Q value) -> only do this if not done
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()


    def train_step_epoch(self, states, actions, rewards, next_states, dones, epochs=20):
        for epoch in range(epochs):
            for i in range(len(states)):
                state = torch.tensor(states[i], dtype=torch.float).to(self.device)
                next_state = torch.tensor(next_states[i], dtype=torch.float).to(self.device)
                action = torch.tensor(actions[i], dtype=torch.long).to(self.device)
                reward = torch.tensor(rewards[i], dtype=torch.float).to(self.device)
                done = dones[i]

                if len(state.shape) == 1:
                    state = state.unsqueeze(0)
                    next_state = next_state.unsqueeze(0)
                    action = action.unsqueeze(0)
                    reward = reward.unsqueeze(0)

                pred = self.model(state)
                target = pred.clone()

                Q_new = reward
                if not done:
                    Q_new = reward + self.gamma * torch.max(self.model(next_state))

                target[0][torch.argmax(action).item()] = Q_new

                self.optimizer.zero_grad()
                loss = self.criterion(target, pred)
                loss.backward()
                self.optimizer.step()

