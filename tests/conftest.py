import pytest
from brownie import *


@pytest.fixture
def rando(accounts):
  return accounts[6]

@pytest.fixture
def user(accounts):
  return accounts[2]

@pytest.fixture
def strategistGuild(accounts):
  return accounts[7]

@pytest.fixture
def gov(accounts):
  return accounts[0]

@pytest.fixture
def registry(gov, BadgerRegistry):
    registry = gov.deploy(BadgerRegistry,gov)
    yield registry

@pytest.fixture
def devGov(accounts, registry, gov):
  registry.setDev(accounts[3], {"from": gov})
  registry.setStrategistGuild(accounts[7], {"from": gov})
  
  return accounts[3]
  

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
