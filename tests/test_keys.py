import brownie
from brownie import ZERO_ADDRESS, accounts


def test_key_permissions(registry, rando):
    with brownie.reverts():
        registry.addKey("controller", ZERO_ADDRESS, {"from": rando})


def test_add_read_key(registry, gov):
    addTx = registry.addKey(
        "controller", "0x63cF44B2548e4493Fd099222A1eC79F3344D9682", {"from": gov}
    )
    assert (
        registry.getAddressOfKey("controller")
        == "0x63cF44B2548e4493Fd099222A1eC79F3344D9682"
    )

    assert (
        registry.getKeyOfAddress("0x63cF44B2548e4493Fd099222A1eC79F3344D9682")
        == "controller"
    )
    assert registry.keysCount() == 1

    event = addTx.events["KeyAdded"][0]
    assert event["key"] == "controller"
    assert event["at"] == "0x63cF44B2548e4493Fd099222A1eC79F3344D9682"


def test_delete_key(registry, gov):
    registry.addKey(
        "controller", "0x63cF44B2548e4493Fd099222A1eC79F3344D9682", {"from": gov}
    )
    removeTx = registry.deleteKey("controller", {"from": gov})

    assert registry.getAddressOfKey("controller") == ZERO_ADDRESS
    assert registry.getKeyOfAddress("0x63cF44B2548e4493Fd099222A1eC79F3344D9682") == ""
    assert registry.keysCount() == 0

    event = removeTx.events["KeyDeleted"][0]
    assert event["key"] == "controller"
    assert event["at"] == "0x63cF44B2548e4493Fd099222A1eC79F3344D9682"
