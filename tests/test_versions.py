import brownie
from brownie import ZERO_ADDRESS, accounts


def test_version_permissions(registry, rando, gov, devGov, strategistGuild):
    # Rando can't add version
    with brownie.reverts():
        registry.addVersions("v10", {"from": rando})

    # Dev can't add version
    with brownie.reverts():
        registry.addVersions("v10", {"from": devGov})

    # Strategist can't add version
    with brownie.reverts():
        registry.addVersions("v10", {"from": strategistGuild})

    # Only gov can add version
    tx = registry.addVersions("v10", {"from": gov})

    event = tx.events["AddVersion"][0]
    assert event["version"] == "v10"
