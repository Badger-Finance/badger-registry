import brownie
from brownie import ZERO_ADDRESS, accounts


def test_vault_demote(registry, vault, vault_two, rando, gov):
    registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 2, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 2) == [[vault, "v1", "2", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    # Random user attempts to demote vault and reverts
    with brownie.reverts("!auth"):
        registry.demote(vault, 0, {"from": rando})

    # Vault must exist
    with brownie.reverts("BadgerRegistry: Vault does not exist"):
        registry.demote(vault_two, 2, {"from": gov})

    # Must be demoting (2 -> 3)
    with brownie.reverts("BadgerRegistry: Vault is not being demoted"):
        registry.demote(vault, 3, {"from": gov})

    # Governance is able to demote vault
    tx = registry.demote(vault, 1, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 1) == [[vault, "v1", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    event = tx.events["DemoteVault"][0]
    assert event["author"] == gov
    assert event["version"] == "v1"
    assert event["metadata"] == "name=BTC-CVX,protocol=Badger,behavior=DCA"
    assert event["vault"] == vault
    assert event["status"] == 1

    # Same vault cannot be demote twice (nothing happens)
    tx = registry.demote(vault, 0, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 0) == [[vault, "v1", "0", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    event = tx.events["DemoteVault"][0]
    assert event["author"] == gov
    assert event["version"] == "v1"
    assert event["metadata"] == "name=BTC-CVX,protocol=Badger,behavior=DCA"
    assert event["vault"] == vault
    assert event["status"] == 0

    # Must be demoting (0 -> 0)
    with brownie.reverts("BadgerRegistry: Vault is not being demoted"):
        registry.demote(vault, 0, {"from": gov})


def test_vault_demote_permissions(registry, vault_one, vault_two, vault_three, rando, gov, devGov, strategistGuild):
  ## Only governance, strategistGuild, devGovernance can demote
  # Rando can't demote

  registry.promote(vault_one, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 3, {"from": gov})
  registry.promote(vault_two, "v2", "name=ETH-CVX,protocol=Badger,behavior=DCA", 1, {"from": gov})
  registry.promote(vault_three, "v1.5", "name=BTC-CVX,protocol=Badger,behavior=DCA", 2, {"from": gov})
  assert registry.getFilteredProductionVaults("v1", 3) == [[vault_one, "v1", "3", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]
  assert registry.getFilteredProductionVaults("v2", 1) == [[vault_two, "v2", "1", "name=ETH-CVX,protocol=Badger,behavior=DCA"]]
  assert registry.getFilteredProductionVaults("v1.5", 2) == [[vault_three, "v1.5", "2", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

  with brownie.reverts():
    registry.demote(vault_one, 0, {"from": rando})
  
  ## devGov can demote
  registry.demote(vault_one, 0, {"from": devGov})

  assert registry.getFilteredProductionVaults("v1", 3) == []
  assert registry.getFilteredProductionVaults("v1", 0) == [[vault_one, "v1", "0", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]
  assert registry.getFilteredProductionVaults("v2", 1) == [[vault_two, "v2", "1", "name=ETH-CVX,protocol=Badger,behavior=DCA"]]
  assert registry.getFilteredProductionVaults("v1.5", 2) == [[vault_three, "v1.5", "2", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

  ## Gov can demote
  registry.demote(vault_two, 0, {"from": gov})

  assert registry.getFilteredProductionVaults("v1", 0) == [[vault_one, "v1", "0", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]
  assert registry.getFilteredProductionVaults("v2", 1) == []
  assert registry.getFilteredProductionVaults("v2", 0) == [[vault_two, "v2", "0", "name=ETH-CVX,protocol=Badger,behavior=DCA"]]
  assert registry.getFilteredProductionVaults("v1.5", 2) == [[vault_three, "v1.5", "2", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

  ## strategistGuild can demote
  registry.demote(vault_three, 0, {"from": strategistGuild})

  assert registry.getFilteredProductionVaults("v1", 0) == [[vault_one, "v1", "0", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]
  assert registry.getFilteredProductionVaults("v2", 0) == [[vault_two, "v2", "0", "name=ETH-CVX,protocol=Badger,behavior=DCA"]]
  assert registry.getFilteredProductionVaults("v1.5", 2) == []
  assert registry.getFilteredProductionVaults("v1.5", 0) == [[vault_three, "v1.5", "0", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]
