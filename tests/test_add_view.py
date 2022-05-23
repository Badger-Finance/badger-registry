import brownie
from brownie import ZERO_ADDRESS, accounts

def test_user_can_add_remove_vault(registry, vault, rando, gov):
    # Author adds vault to their list
    tx = registry.add(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", {"from": rando})
    assert registry.getVaults("v1", rando) == [[vault, "v1", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    # User attempts to add vault with bad metadata and reverts
    with brownie.reverts():
        registry.add(vault, "v1", "DCA-BTC-CVX", {"from": rando})

    event = tx.events["NewVault"][0]
    assert event["vault"] == vault

    # Same vault cannot be added twice (nothing happens)
    tx = registry.add(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", {"from": rando})
    assert len(tx.events) == 0

    # Only author can remove vault from their list (nothing happens)
    tx = registry.remove(vault, {"from": gov})
    assert len(tx.events) == 0
    

    # Author attempts to remove vault with address not on list (nothing happens)
    tx = registry.remove(ZERO_ADDRESS, {"from": gov})
    assert len(tx.events) == 0

    # Author can remove their own vault from list
    tx = registry.remove(vault, {"from": rando})
    assert registry.getVaults("v1", rando) == []

    event = tx.events["RemoveVault"][0]
    assert event["vault"] == vault


def test_user_can_add_remove_multiple_vaults(registry, vault_one, vault_two, vault_three, rando):
    # Author creates and adds vault1 to registry
    vault1 = vault_one

    registry.add(vault1, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", {"from": rando})
    assert registry.getVaults("v1", rando) == [[vault1, "v1", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    # Author creates and adds vault2 to registry
    vault2 = vault_two

    registry.add(vault2, "v1", "name=ETH-CVX,protocol=Badger,behavior=DCA", {"from": rando})
    assert registry.getVaults("v1", rando) == [[vault1, "v1", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"], [vault2, "v1", "1", "name=ETH-CVX,protocol=Badger,behavior=DCA"]]

    # Author creates and adds vault3 to registry
    vault3 = vault_three

    registry.add(vault3, "v1", "name=MATIC-CVX,protocol=Badger,behavior=DCA", {"from": rando})
    assert registry.getVaults("v1", rando) == [[vault1, "v1", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"], [vault2, "v1", "1", "name=ETH-CVX,protocol=Badger,behavior=DCA"], [vault3, "v1", "1", "name=MATIC-CVX,protocol=Badger,behavior=DCA"]]

    # Author can remove their own vault from list
    tx = registry.remove(vault1, {"from": rando})
    event = tx.events["RemoveVault"][0]
    assert event["vault"] == vault1
    
    # NOTE: Order of entries change when vaults are removed from sets
    assert registry.getVaults("v1", rando) == [[vault3, "v1", "1", "name=MATIC-CVX,protocol=Badger,behavior=DCA"], [vault2, "v1", "1", "name=ETH-CVX,protocol=Badger,behavior=DCA"]]
