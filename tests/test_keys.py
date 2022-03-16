import brownie
from brownie import ZERO_ADDRESS, accounts


def test_key_permissions(registry, rando):
    with brownie.reverts():
        registry.setKey("controller", ZERO_ADDRESS, {"from": rando})


def test_add_read_key(registry, gov):
    key = "controller"
    address1 = "0x63cF44B2548e4493Fd099222A1eC79F3344D9682"
    address2 = "0x63cF44B2548e4493Fd099222A1eC79F3344D9683"

    ## set a new key
    tx = registry.setKey(key, address1, {"from": gov})
    assert registry.getTargetOfKey(key) == address1
    assert registry.getKeysOfTarget(address1) == [key]
    assert registry.keysCount() == 1
    assert tx.events["SetKey"][0] == {"key": key, "at": address1}
    assert tx.events["AddKey"][0] == {"key": key}

    ## change value of a key
    tx = registry.setKey(key, address2, {"from": gov})
    assert registry.getTargetOfKey(key) == address2
    assert registry.getKeysOfTarget(address1) == []
    assert registry.keysCount() == 1
    assert tx.events["SetKey"][0] == {"key": key, "at": address2}
    assert "AddKey" not in tx.events


def test_delete_key(registry, gov):
    key = "controller"
    address = "0x63cF44B2548e4493Fd099222A1eC79F3344D9682"
    registry.setKey(key, address, {"from": gov})
    tx = registry.deleteKey(key, {"from": gov})
    assert registry.getTargetOfKey(key) == ZERO_ADDRESS
    assert registry.getKeysOfTarget(address) == []
    assert registry.keysCount() == 0
    assert tx.events["DeleteKey"][0] == {"key": key}


def test_get_multiple_keys_of_address(registry, gov):
    address = "0x63cF44B2548e4493Fd099222A1eC79F3344D9682"
    key1 = "controller1"
    key2 = "controller2"
    registry.setKey(key1, address, {"from": gov})
    registry.setKey(key2, address, {"from": gov})
    keys = registry.getKeysOfTarget(address)
    assert len(keys) == 2
    assert keys[0] == key1
    assert keys[1] == key2
