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
    # Rando can't demote

    with brownie.reverts():
        registry.demote("v1", vault, 2, {"from": rando})


def test_vault_demotion_order(registry, vault, vault_one, vault_two, gov):
    # Demotion can be only happen in one direction
    # If a user try to increase the status of a vault using the demote function the function should revert

    # Can't demote from experimental to guarded
    registry.promote("v1", vault, 0, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 0) == [[vault], [""]]
    with brownie.reverts():
        registry.demote("v1", vault, 1, {"from": gov})

    # Can't demote from experimental to open
    registry.promote("v1", vault_one, 0, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 0) == [[vault,vault_one], ["",""]]
    with brownie.reverts():
        registry.demote("v1", vault_one, 2, {"from": gov})

    # Can't demote from guarded to open
    registry.promote("v1", vault_two, 1, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 1) == [[vault_two], [""]]
    with brownie.reverts():
        registry.demote("v1", vault_two, 2, {"from": gov})
