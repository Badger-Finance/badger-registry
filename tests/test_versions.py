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


def test_version_guard(registry, rando, gov, devGov, vault, vault_one, strategistGuild):
    registry.addVersions("v10", {"from": gov})

    # Can add supported version
    registry.add("v10", vault, "my-meta-data1", {"from": rando})

    with brownie.reverts():
        registry.add("v-unknown", vault_one, "my-meta-data1", {"from": rando})
