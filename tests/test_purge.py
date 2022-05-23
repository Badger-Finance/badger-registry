import brownie
from brownie import ZERO_ADDRESS, accounts


def test_vault_purge(registry, vault, rando, gov):
  
    # Test bad purge
    with brownie.reverts():
        registry.purge(vault, {"from": gov})
  
    registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 2, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 2) == [[vault, "v1", "2", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    # Random user attempts to purge vault and reverts
    with brownie.reverts():
        registry.purge(vault, {"from": rando})

    # Governance is able to purge vault
    tx = registry.purge(vault, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 1) == []

    event = tx.events["PurgeVault"][0]
    assert event["author"] == gov
    assert event["version"] == "v1"
    assert event["metadata"] == "name=BTC-CVX,protocol=Badger,behavior=DCA"
    assert event["vault"] == vault
    assert event["status"] == 2

    # Same vault cannot be purged twice 
    with brownie.reverts():
        registry.purge(vault, {"from": gov})

def test_vault_purge_permissions(registry, vault_one, vault_two, vault_three, rando, gov, devGov, strategistGuild):
  ## Only governance, strategistGuild, devGovernance can purge
  # Rando can't purge

  registry.promote(vault_one, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 3, {"from": gov})
  registry.promote(vault_two, "v2", "name=ETH-CVX,protocol=Badger,behavior=DCA", 1, {"from": gov})
  assert registry.getFilteredProductionVaults("v1", 3) == [[vault_one, "v1", "3", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]
  assert registry.getFilteredProductionVaults("v2", 1) == [[vault_two, "v2", "1", "name=ETH-CVX,protocol=Badger,behavior=DCA"]]

  # Randoms no purge
  with brownie.reverts():
    registry.purge(vault_one, {"from": rando})

  # devGov no purge
  with brownie.reverts():
    registry.purge(vault_one, {"from": devGov})

  ## Gov can purge
  registry.purge(vault_one, {"from": gov})

  assert registry.getFilteredProductionVaults("v1", 3) == []
  assert registry.getFilteredProductionVaults("v2", 1) == [[vault_two, "v2", "1", "name=ETH-CVX,protocol=Badger,behavior=DCA"]]

  ## strategistGuild can purge
  registry.purge(vault_two, {"from": strategistGuild})

  assert registry.getFilteredProductionVaults("v1", 3) == []
  assert registry.getFilteredProductionVaults("v2", 1) == []
