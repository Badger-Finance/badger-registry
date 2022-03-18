import brownie
from eth_account import Account
import pytest
from brownie import *


@pytest.fixture
def rando(accounts):
    return accounts[6]


@pytest.fixture
def user(accounts):
    return accounts[2]


@pytest.fixture
def gov(accounts):
    return accounts[0]


@pytest.fixture
def alt_gov(accounts):
    return accounts[7]


@pytest.fixture
def dev(accounts):
    return accounts[1]


@pytest.fixture
def strategist_guild(accounts):
    return [accounts[3], accounts[4], accounts[5]]


@pytest.fixture
def alt_strategist_guild(gov, alt_gov, dev):
    return [gov, alt_gov, dev]


@pytest.fixture
def registry(gov, strategist_guild: list, BadgerRegistry):
    registry = gov.deploy(BadgerRegistry)
    registry.initialize(gov, strategist_guild, len(strategist_guild) / 2 + 1, False)
    yield registry


@pytest.fixture
def devGov(dev, registry, gov):
    registry.setDev(dev, {"from": gov})
    return dev


@pytest.fixture
def vault():
    yield "0x19D97D8fA813EE2f51aD4B4e04EA08bAf4DFfC28"


@pytest.fixture
def vault_one():
    yield "0xd04c48A53c111300aD41190D63681ed3dAd998eC"


@pytest.fixture
def vault_two():
    yield "0x2B5455aac8d64C14786c3a29858E43b5945819C0"


@pytest.fixture
def vault_three():
    yield "0x235c9e24D3FB2FAFd58a2E49D454Fdcd2DBf7FF1"


## Forces reset before each test
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass
