import brownie
from brownie import ZERO_ADDRESS, accounts


# The demote function can move the vaults to the following states
# experimental
# deprecated
# guarded
# The following state is not intended
# open


def test_vault_demotion_step_experimental(
    registry, vault, vault_one, rando, gov, devGov, strategistGuild
):
    # Demote vault from open to experimental
    registry.promote("v1", vault, 2, {"from": gov})
    tx = registry.demote("v1", vault, 0, {"from": gov})
    event = tx.events["DemoteVault"][0]
    assert event["vault"] == vault
    assert event["status"] == 0


def test_vault_demotion_step_deprecated(
    registry, vault, vault_one, rando, gov, devGov, strategistGuild
):
    # Demote vault from open to deprecated
    registry.promote("v1", vault, 2, {"from": gov})
    tx = registry.demote("v1", vault, 3, {"from": gov})
    event = tx.events["DemoteVault"][0]
    assert event["vault"] == vault
    assert event["status"] == 3


def test_vault_demotion_step_deprecated(
    registry, vault, vault_one, rando, gov, devGov, strategistGuild
):
    # Demote vault from open to guarded
    registry.promote("v1", vault, 2, {"from": gov})
    tx = registry.demote("v1", vault, 1, {"from": gov})
    event = tx.events["DemoteVault"][0]
    assert event["vault"] == vault
    assert event["status"] == 1


def test_vault_demotion_step_prod(
    registry, vault, vault_one, rando, gov, devGov, strategistGuild
):
    # Can't demote vault from deprecated to open because it makes no sense
    registry.promote("v1", vault, 2, {"from": gov})
    registry.demote("v1", vault, 3, {"from": gov})
    with brownie.reverts():
        registry.demote("v1", vault, 2, {"from": gov})


def test_vault_demotion_permissions(
    registry, vault, vault_one, rando, gov, devGov, strategistGuild
):
    # Rando can't promote

    with brownie.reverts():
        registry.demote("v1", vault, 2, {"from": rando})
