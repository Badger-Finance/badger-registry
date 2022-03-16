import brownie
from brownie import ZERO_ADDRESS, AdminUpgradeabilityProxy, BadgerRegistry, StringsUtils


def test_initialize(registry, gov, strategist_guild):
    assert registry.governance() == gov
    for i in range(len(strategist_guild)):
        registry.strategistGuild(i) == strategist_guild[i]
    assert registry.multiSigThreshold() == len(strategist_guild) / 2 + 1
    assert registry.versions(0) == "v1"
    assert registry.versions(1) == "v2"
    assert registry.productionMetadatas(0) == ""


## Check if the key migrator doesn't ruin anything
def test_initialize_with_reverse_key_initialization(gov, dev, strategist_guild):
    StringsUtils.deploy({"from": dev})
    registry = BadgerRegistry.deploy({"from": dev})
    args = [gov, strategist_guild, len(strategist_guild) / 2 + 1, False]
    proxy = AdminUpgradeabilityProxy.deploy(
        registry,
        dev,
        registry.initialize.encode_input(*args),
        {"from": dev},
    )
    AdminUpgradeabilityProxy.remove(proxy)
    proxy = BadgerRegistry.at(proxy)

    proxy.setDev(dev, {"from": gov})

    key = "controller"
    key_address = "0x63cF44B2548e4493Fd099222A1eC79F3344D9682"
    proxy.setKey(key, key_address, {"from": gov})

    args = [ZERO_ADDRESS, [], 0, True]
    registry = BadgerRegistry.deploy({"from": dev})
    BadgerRegistry.remove(proxy)
    proxy = AdminUpgradeabilityProxy.at(proxy)
    proxy.upgradeToAndCall(
        registry, registry.initialize.encode_input(*args), {"from": dev}
    )
    AdminUpgradeabilityProxy.remove(proxy)
    proxy = BadgerRegistry.at(proxy)

    assert proxy.getKeysOfTarget(key_address) == [key]
