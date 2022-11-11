"""Beez blockchain - python types."""

from typing import NewType

PublicKeyString = NewType("PublicKeyString", str)
Address = NewType("Address", str)  # like 192.168.1.209
Stake = NewType("Stake", int)
Prize = NewType("Prize", int)
ChallengeID = NewType("ChallengeID", str)
WalletAddress = NewType("WalletAddress", str)
