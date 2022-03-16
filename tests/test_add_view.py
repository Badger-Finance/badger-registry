import brownie
import pytest
from brownie import ZERO_ADDRESS, accounts


@pytest.mark.parametrize("metadata", ["", "MyMetadata"])
def test_user_can_add_remove_vault(registry, vault, rando, gov, metadata):
    # Author adds vault to their list
    tx = registry.add("v1", metadata, vault, {"from": rando})
    assert registry.getVaults("v1", metadata, rando) == [vault]

    event = tx.events["NewVault"][0]
    assert event["vault"] == vault

    # Same vault cannot be added twice (nothing happens)
    tx = registry.add("v1", metadata, vault, {"from": rando})
    assert len(tx.events) == 0

    # Only author can remove vault from their list (nothing happens)
    tx = registry.remove("v1", metadata, vault, {"from": gov})
    assert len(tx.events) == 0

    # Author attempts to remove vault with address not on list (nothing happens)
    tx = registry.remove("v1", metadata, ZERO_ADDRESS, {"from": gov})
    assert len(tx.events) == 0

    # Author can remove their own vault from list
    tx = registry.remove("v1", metadata, vault, {"from": rando})
    assert registry.getVaults("v1", metadata, rando) == []

    event = tx.events["RemoveVault"][0]
    assert event["vault"] == vault


@pytest.mark.parametrize("metadata", ["", "MyMetadata"])
def test_user_can_add_remove_multiple_vaults(
    registry, vault_one, vault_two, vault_three, rando, metadata
):
    # Author creates and adds vault1 to registry
    vault1 = vault_one

    registry.add("v1", metadata, vault1, {"from": rando})
    assert registry.getVaults("v1", metadata, rando) == [vault1]

    # Author creates and adds vault2 to registry
    vault2 = vault_two

    registry.add("v1", metadata, vault2, {"from": rando})
    assert registry.getVaults("v1", metadata, rando) == [vault1, vault2]

    # Author creates and adds vault3 to registry
    vault3 = vault_three

    registry.add("v1", metadata, vault3, {"from": rando})
    assert registry.getVaults("v1", metadata, rando) == [vault1, vault2, vault3]

    # Author can remove their own vault from list
    tx = registry.remove("v1", metadata, vault1, {"from": rando})
    event = tx.events["RemoveVault"][0]
    assert event["vault"] == vault1

    # NOTE: Order of entries change when vaults are removed from sets
    assert registry.getVaults("v1", metadata, rando) == [vault3, vault2]
