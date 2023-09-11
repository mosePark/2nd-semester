# -*- coding: utf-8 -*-
"""RNN

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hZZTjUEQ_u7Vct9hWwPz3yxFCj8pAJkp
"""
# 서울시립대 전종준 교수님 4050 11주차 특강

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

device = 'cuda' if torch.cuda.is_available() else 'cpu'
torch.manual_seed(1)
if device == 'cuda':
    torch.cuda.manual_seed_all(1)

# Load data
df = pd.read_csv('.../stock_data.csv')

df.head()

x_0 = np.array(df['Close'][0:-1])
x_1 = np.array(df['Close'][1:])
x = np.log(1-(x_1-x_0)/x_0)

# Define hyperparameters
seq_len = 6
hidden_size = 5
num_layers = 1
learning_rate = 0.001
num_epochs = 100

rnn = nn.RNN(input_size = 1, hidden_size = 5, num_layers = 1, batch_first = True)

rnn

"""- Batch_first = False 인 경우에 (seq, batch, feature) 로 input data x 를 입력한다. (Default 값으로 지정되어 있다)
- Batch_first = True 인 경우에 (batch, seq, feature) 로 input data x 를 입력한다.
- 출력값 역시 Batch_first 옵션을 따른다.

"""

# 2개 샘플 만들기
print(x[0:6])
print(x[1:7])
x_data = np.concatenate([x[0:6],x[1:7]], axis = 0)
print(x_data)
x_data = x_data.reshape(2,6,1)
input = torch.tensor(x_data).float()
print(input.shape)
print(input.dtype)

"""h0 만들기
- Batch_first = True 와 상관없이 (num_layers*D, batch, hidden_size) 로 h0 를 입력한다.  (만약 bidirectional 이면 D = 2, 아니면 D = 1)
- 위의 예제에서는 2개 샘플, 1개 층, 5차원이므로 (1,2,5)를 입력한다.



"""

h0 = torch.randn(1, 2, 5)
h0.dtype

output, hn = rnn(input, h0)
print("output")
print(output)
print(output.shape)
print("hn")
print(hn)
print(hn.shape)

"""Batch_first=True 이므로 output 의 형태는 (batch, seq, feature) 로 이루어진다.
- output[0,:,:] 은 첫 번째 input에 대한 rnn feature 행렬인데, 행벡터가 rnn 각 노드에서 hidden feature 에 해당한다.
- hn[:,0,:] 은 관측치 두개에 대한 마지막 hidden feature 값인데, hn[:,0,:] 은 첫번째 input에 대한 hidden feature vector에 해당한다.
"""

# Define the RNN model
class myRNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super(myRNN, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.rnn = nn.RNN(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        out, _ = self.rnn(x, h0)
        out = out[:, -1, :]
        out = self.fc(out)
        return out

x[0:12]

# window size 설정
window_size = 6
# 입력 시퀀스와 출력 시퀀스 정의
def create_inout_sequences(input_data, window_size):
    inout_seq = []
    L = len(input_data)
    for i in range(L - window_size):
        train_seq = input_data[i:(i+window_size)].reshape(window_size,1)
        train_seq = train_seq.astype(np.float32)
        train_label = input_data[(i+window_size):(i+window_size+1)]
        train_label = train_label.astype(np.float32)
        inout_seq.append((train_seq ,train_label))
    return inout_seq

# 입력 시퀀스와 출력 시퀀스 생성
train_data = create_inout_sequences(x, window_size)
print('input:', train_data[0][0].shape)
print('output:', train_data[0][1].shape)
print('train_data:', len(train_data))

# 데이터를 batch 단위로 나누기
batch_size = 10
train_loader = torch.utils.data.DataLoader(train_data, shuffle=False, batch_size=batch_size)

# batch 단위로 데이터 출력
for i, (inputs, labels) in enumerate(train_loader):
    print(f'Batch {i}:')
    #print('Inputs: \n', inputs)
    print(inputs.shape)
    #print('Labels: \n', labels)
    print(labels.shape)
    break

model = myRNN(1, hidden_size, num_layers).to(device)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

for i, (inputs, labels) in enumerate(train_loader):
  input = inputs.to(device)
  label = labels.to(device)
  output = model(input)
  print(output)
  #print(input.shape)
  break

for i, (inputs, labels) in enumerate(train_loader):
  input = inputs.to(device)
  label = labels.to(device)
  output = model(input)
  loss = criterion(output, label)
  print(loss)
  break

model = myRNN(1, hidden_size, num_layers).to(device)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
optimizer.zero_grad()

for i, (inputs, labels) in enumerate(train_loader):
  input = inputs.to(device)
  label = labels.to(device)
  output = model(input)
  loss = criterion(output, label)
  optimizer.zero_grad()
  loss.backward()
  optimizer.step()
print(loss)

model = myRNN(1, hidden_size, num_layers).to(device)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
optimizer.zero_grad()

num_epochs = 10
for epoch in range(num_epochs):
  for i, (inputs, labels) in enumerate(train_loader):
    input = inputs.to(device)
    label = labels.to(device)
    output = model(input)
    loss = criterion(output, label)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
  print(loss)
