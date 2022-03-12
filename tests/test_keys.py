import brownie
from brownie import ZERO_ADDRESS, accounts


def test_key_permissions(registry, rando):
    with brownie.reverts():
        registry.set("controller", ZERO_ADDRESS, {"from": rando})


def test_add_read_key(registry, gov):
    registry.set(
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


def test_delete_key(registry, gov):
    registry.set(
        "controller", "0x63cF44B2548e4493Fd099222A1eC79F3344D9682", {"from": gov}
    )
    registry.deleteKey("controller", {"from": gov})
    assert registry.getAddressOfKey("controller") == ZERO_ADDRESS
    assert registry.getKeyOfAddress("0x63cF44B2548e4493Fd099222A1eC79F3344D9682") == ""
    assert registry.keysCount() == 0
