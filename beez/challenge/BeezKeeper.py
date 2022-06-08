from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional
from loguru import logger
import requests
import copy
import threading
import os
from dotenv import load_dotenv
import time

#### Machine Learning
import torch
import torch.nn as nn
import torch.nn.functional as F
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# for function
import random

load_dotenv()  # load .env

if TYPE_CHECKING:
    from beez.Types import Prize, ChallengeID, PublicKeyString
    from beez.transaction.ChallengeTX import ChallengeTX
    from beez.challenge.Challenge import Challenge
    from beez.challenge.MLChallenge import MLChallenge

from beez.BeezUtils import BeezUtils
from beez.challenge.ChallengeState import ChallengeState



class BeezKeeper():
    """
    keeps track of each Challenge.
    Every time that a block is added to the Blockchain, the beezKeeper will update the challenge based
    on the transactions accured.
    """
    def __init__(self):
        self.challenges : Dict[ChallengeID : Challenge] = {}
        # Download the dataset for silulation
        self.getIrisDataset()
        
    
    def getIrisDataset(self):
        csv_url = "https://datahub.io/machine-learning/iris/r/iris.csv"
        self.iris = pd.read_csv(csv_url)

        # replace labels with numbers
        mappings = {
            'Iris-setosa': 0,
            'Iris-versicolor': 1,
            'Iris-virginica': 2
        }
        
        self.iris['class'] = self.iris['class'].apply(lambda x: mappings[x])

        logger.info(f"Iris Dataset imported.")

    
    def set(self, challenge: Challenge):
        challengeID : ChallengeID = challenge.id
        reward = challenge.reward

        if challengeID in self.challenges.keys():
            logger.info(f"Challenge already created, update the challenge {challengeID}")
            self.challenges[challengeID] = challenge
        else:
            # new challenge! Thinkto broadcast the challenge and no more!
            logger.info(f"Challenge id: {challengeID} of reward {reward} tokens kept. Challenge STATE: {challenge.state}")
            self.challenges[challengeID] = challenge

    def get(self, challengeID: ChallengeID) -> Optional[Challenge]:
        if challengeID in self.challenges.keys():
            return self.challenges[challengeID]
        else:
            return None

    def challegeExists(self, challengeID: ChallengeID) -> bool:
        if challengeID in self.challenges.keys():
            return True
        else:
            return False

    def delete(self, challengeID: ChallengeID):
        if challengeID in self.challenges.keys():
            logger.warning(f"remove the closed challenge!")
            self.challenges.pop(challengeID)
       
    def acceptChallenge(self, challenge: Challenge):
        logger.info(f"accept challengeid: {challenge.id}")
        logger.info(f"Current ChallengeState: {challenge.state}")
        isAccepted = False

        if challenge.state == ChallengeState.CREATED.name:

            localChallenge : Challenge = self.challenges[challenge.id]
            localChallenge.state = ChallengeState.ACCEPTED.name
            self.challenges[challenge.id] = localChallenge

            logger.info(f"Updated localKeeper ChallengeState: {localChallenge.state}")
            isAccepted = True
        
        return isAccepted


    def workOnMLChallenge(self, challenge: MLChallenge):
        logger.info(f"work on IRIS DATASET challenge...! {challenge.id}")

        logger.info(self.iris.head())


        challengeStateOpen = challenge.state == ChallengeState.OPEN.name if  True else False
    
        logger.info(f"Machine Learning challenge state: {challengeStateOpen}")

        if challengeStateOpen:
            if challenge.counter < challenge.iteration + 1:
                logger.info(f"counter: {challenge.counter} : iteration: {challenge.iteration}")

                # execute the calculus
                # Train/Test Split
                X = self.iris.drop('class', axis=1).values
                y = self.iris['class'].values

                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                X_train = torch.FloatTensor(X_train)
                X_test = torch.FloatTensor(X_test)
                y_train = torch.LongTensor(y_train)
                y_test = torch.LongTensor(y_test)

                logger.info(f"challenge model: {challenge.model}")

                model = challenge.model
                criterion = challenge.criterion
                optimizer = challenge.optimizer

                # Do one epoch (iteration)
                y_hat = model.forward(X_train)
                loss = criterion(y_hat, y_train)
                optimizer.step()

                if challenge.counter % 2 == 0:
                    logger.warning(f'Epoch: {challenge.counter} Loss: {loss}')

                time.sleep(2)


                # Show Accuracy
                # Model Evaluation
                preds = []

                with torch.no_grad():
                    for val in X_test:
                        y_hat = model.forward(val)
                        preds.append(y_hat.argmax().item())


                df = pd.DataFrame({'Y': y_test, 'YHat': preds})
                df['Correct'] = [1 if corr == pred else 0 for corr, pred in zip(df['Y'], df['YHat'])]   

                accuracy = df['Correct'].sum() / len(df)

                logger.warning(f"Epoch: {challenge.counter} -- Accuracy: {accuracy}")

                time.sleep(2)

                # update the values
                challenge.model = model
                challenge.optimizer = optimizer
                challenge.loss = loss
                challenge.counter = challenge.counter + 1
                
                # Store the new version of the Challenge
                self.set(challenge)
                
                localChallenge = self.get(challenge.id)

                return localChallenge

            else:
                logger.info(f"counter: {challenge.counter} : iteration: {challenge.iteration}")
                logger.warning(f"Challenge must be closed: {challenge.id}")

                # update the values
                challenge.state = ChallengeState.CLOSED.name
                # Store the new version of the Challenge
                self.set(challenge)
                
                localChallenge = self.get(challenge.id)

                return localChallenge

            
        logger.warning(f"It was not possible to perform the calculus: {challenge.id}")
        return None


    def workOnChallenge(self, challenge: Challenge) -> Optional[Challenge]:
        logger.info(f"work on challenge...! {challenge.id}")

        challengeStateOpen = challenge.state == ChallengeState.OPEN.name if True else False

        logger.info(f"challengeStateOpen {challengeStateOpen}")
        
        if challengeStateOpen:
            if challenge.counter < challenge.iteration + 1:
                logger.info(f"counter: {challenge.counter} : iteration: {challenge.iteration}")

                # execute the calculus
                logger.info(f"challenge function: {challenge.sharedFunction.__doc__}")
                sharedfunction = challenge.sharedFunction
                # logger.info(f"challenge function: {type(sharedfunction)}")
                # inputA = random.randint(0, 100)
                # inputB = random.randint(0, 100)

                inputA = 2
                inputB = 2

                logger.info(f"inputA {inputA}")
                logger.info(f"inputB {inputB}")

                calculusResult = sharedfunction(inputA, inputB)

                # update the values
                challenge.result = challenge.result + calculusResult
                challenge.counter = challenge.counter + 1
                
                # Store the new version of the Challenge
                self.set(challenge)
                logger.info(f"Partial Result: {challenge.result}")

                localChallenge = self.get(challenge.id)

                return localChallenge

            else:
                logger.info(f"counter: {challenge.counter} : iteration: {challenge.iteration}")
                logger.warning(f"Challenge must be closed: {challenge.id}")

                # update the values
                challenge.state = ChallengeState.CLOSED.name
                # Store the new version of the Challenge
                self.set(challenge)
                
                localChallenge = self.get(challenge.id)

                return localChallenge

            
        logger.warning(f"It was not possible to perform the calculus: {challenge.id}")
        return None

    def update(self, receivedChallenge: Challenge) -> bool:
        # do a copy of the local challenge!
        challengeExists = self.challegeExists(receivedChallenge.id)
        if challengeExists:
            logger.info(f"Update the local version of the Challenge")
            self.challenges[receivedChallenge.id] = receivedChallenge


    # TODO: Generate the rewarding function!!!