from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional
import uuid

#### Machine Learning
import torch
import torch.nn as nn
import torch.nn.functional as F
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split


if TYPE_CHECKING:
    from beez.Types import Prize, PublicKeyString

from beez.challenge.Challenge import Challenge

    
class MLChallenge(Challenge):

    def __init__(self, ownerPublicKey: PublicKeyString, sharedFunction: Callable[[], Any], reward: Prize, iteration: int, model, criterion, optimizer, loss):
        super().__init__(ownerPublicKey, sharedFunction, reward, iteration)
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.loss = loss

