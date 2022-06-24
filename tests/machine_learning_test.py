from loguru import logger

import os
from dotenv import load_dotenv
import requests
import pathlib

from beez.transaction.Transaction import Transaction
from beez.transaction.TransactionType import TransactionType
from beez.wallet.Wallet import Wallet
from beez.BeezUtils import BeezUtils
from beez.Types import WalletAddress
from beez.challenge.Challenge import Challenge
from beez.challenge.MLChallenge import MLChallenge
from beez.transaction.ChallengeTX import ChallengeTX
from beez.challenge.ChallengeType import ChallengeType


#### Machine Learning
import torch
import torch.nn as nn
import torch.nn.functional as F
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split


load_dotenv()  # load .env

NODE_API_PORT = os.environ.get("NODE_API_PORT", default=8176)
URI = os.environ.get("FIRST_SERVER_IP", default="192.168.1.61")


def postChallengeTransaction(senderWallet: Wallet, amount, txType: TransactionType, challenge: Challenge):

    tx = senderWallet.createChallengeTransaction(amount, txType, challenge) 
    url = f"http://{URI}:{NODE_API_PORT}/challenge"

    package = {'challenge': BeezUtils.encode(tx)}
    request = requests.post(url, json=package)

    logger.info(f"ok?: {request}")


def sum(a: int,b: int):
    """
    Returns the sum of two given integers.

    Parameters:
        a (int): The first value
        b (int): The second value

    Returns:
        sum (int): The sum of the two inputs.
    """
    return a + b


class ANN(nn.Module):
    def __init__(self):
       super().__init__()
       self.fc1 = nn.Linear(in_features=4, out_features=16)
       self.fc2 = nn.Linear(in_features=16, out_features=12)
       self.output = nn.Linear(in_features=12, out_features=3)
 
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.output(x)
        return x


def test_machine_learning_challenge():
    # Before to test Alice wallet must have some Tokens into the wallet!
    # Run exchange_transcation_test before!!!

    # Imports and Dataset

    # csv_url = "https://www.andreaminini.com/data/andreaminini/iris_training.csv"
    # csv_url_origin = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
    
    # csv_url_2 = "https://datahub.io/machine-learning/iris/r/iris.csv"
    # iris = pd.read_csv(csv_url_2)

    # print(iris.head())

    # mappings = {
    #     'Iris-setosa': 0,
    #     'Iris-versicolor': 1,
    #     'Iris-virginica': 2
    # }

    # iris['class'] = iris['class'].apply(lambda x: mappings[x])

    # print("############### \n")
    # print(iris.head())

    # Train/Test Split

    # X = iris.drop('class', axis=1).values
    # y = iris['class'].values

    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # X_train = torch.FloatTensor(X_train)
    # X_test = torch.FloatTensor(X_test)
    # y_train = torch.LongTensor(y_train)
    # y_test = torch.LongTensor(y_test)

    # print("###########")
    # print(X_train)

    # Defining a Neural Network Model
    model = ANN()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)   
    loss = 0

    # Model Training
    # epochs = 100
    # loss_arr = []

    # for i in range(epochs):
    #     y_hat = model.forward(X_train)
    #     loss = criterion(y_hat, y_train)
    #     loss_arr.append(loss)
    
    #     if i % 10 == 0:
    #         print(f'Epoch: {i} Loss: {loss}')
    
    #     optimizer.zero_grad()
    #     loss.backward()
    #     optimizer.step()

    ### Return the model as result!!!

    # Model Evaluation
    # preds = []

    # with torch.no_grad():
    #     for val in X_test:
    #         y_hat = model.forward(val)
    #         preds.append(y_hat.argmax().item())


    # df = pd.DataFrame({'Y': y_test, 'YHat': preds})
    # df['Correct'] = [1 if corr == pred else 0 for corr, pred in zip(df['Y'], df['YHat'])]   

    # accuracy = df['Correct'].sum() / len(df)

    # print(f"accuracy: {accuracy}")

    # # Import the alice private key
    currentPath = pathlib.Path().resolve()
    alicePrivateKeyPath = f"{currentPath}/beez/keys/alicePrivateKey.pem"

    # # Generate a standard transaction
    AliceWallet = Wallet()
    AliceWallet.fromKey(alicePrivateKeyPath)

    reward = 1000
    type = TransactionType.CHALLENGE.name
    iteration = 6
    owner = AliceWallet.publicKeyString()

    challengeType = ChallengeType.IRIS.name

    # # Define the challenge
    mlChallenge = MLChallenge(owner, sum, reward, iteration, challengeType, model, criterion, optimizer, loss)

    postChallengeTransaction(AliceWallet, reward, type, mlChallenge)

    # assert beezNode.ip == localIP
    assert 5 == 5

    