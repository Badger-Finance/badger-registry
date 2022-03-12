import brownie
from brownie import ZERO_ADDRESS, accounts


def test_key_permissions(registry, rando):
    with brownie.reverts():
        registry.set("controller", ZERO_ADDRESS, {"from": rando})


def test_add_read_key(registry, gov):
    registry.set(
        "controller", "0x63cF44B2548e4493Fd099222A1eC79F3344D9682", {"from": gov})
    assert registry.keyByAddress("0x63cF44B2548e4493Fd099222A1eC79F3344D9682") == "controller"
    assert registry.get(
        "controller") == "0x63cF44B2548e4493Fd099222A1eC79F3344D9682"
    assert registry.keysCount() == 1


def test_delete_key(registry, rando, gov):
    registry.set(
        "controller", "0x63cF44B2548e4493Fd099222A1eC79F3344D9682", {"from": gov})
    # should revert if not gov
    with brownie.reverts():
        registry.deleteKey("controller", {"from": rando})
    registry.deleteKey("controller",  {"from": gov})
    assert registry.get("controller") == ZERO_ADDRESS
    assert registry.keysCount() == 0


def test_delete_keys(registry, rando, gov):
    registry.set("controller", "0x63cF44B2548e4493Fd099222A1eC79F3344D9682", {"from": gov})
    registry.set("ibBTC", "0xc4E15973E6fF2A35cC804c2CF9D2a1b817a8b40F", {"from": gov})
    # should revert if not gov
    with brownie.reverts():
        registry.deleteKeys(["controller", "ibBTC"], {"from": rando})
    registry.deleteKeys(["controller", "ibBTC"],  {"from": gov})
    assert registry.get("controller") == ZERO_ADDRESS
    assert registry.get("ibBTC") == ZERO_ADDRESS
    assert registry.keysCount() == 0
