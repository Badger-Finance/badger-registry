import brownie
from brownie import ZERO_ADDRESS, accounts


def test_vault_demote(registry, vault, rando, gov):
    registry.promote("v1", "DCA-BTC-CVX", vault, 0, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 0) == [[vault, "v1", "DCA-BTC-CVX"]]

    # Random user attempts to demote vault and reverts
    with brownie.reverts():
        registry.demote("v1", "DCA-BTC-CVX", vault, 0, {"from": rando})

    # Governance is able to demote vault
    tx = registry.demote("v1", "DCA-BTC-CVX", vault, 0, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 0) == []

    event = tx.events["DemoteVault"][0]
    assert event["author"] == gov
    assert event["version"] == "v1"
    assert event["metadata"] == "DCA-BTC-CVX"
    assert event["vault"] == vault
    assert event["status"] == 0

    # Same vault cannot be demote twice (nothing happens)
    tx = registry.demote("v1", "DCA-BTC-CVX", vault, 0, {"from": gov})
    assert len(tx.events) == 0



def test_vault_demote_permissions(registry, vault_one, vault_two, vault_three, rando, gov, devGov, strategistGuild):
  ## Only governance, strategistGuild, devGovernance can demote
  # Rando can't demote

  registry.promote("v1", "DCA-BTC-CVX", vault_one, 0, {"from": gov})
  registry.promote("v2", "DCA-ETH-CVX", vault_two, 1, {"from": gov})
  registry.promote("v1", "DCA-BTC-CVX", vault_three, 2, {"from": gov})
  assert registry.getFilteredProductionVaults("v1", 0) == [[vault_one, "v1", "DCA-BTC-CVX"]]
  assert registry.getFilteredProductionVaults("v2", 1) == [[vault_two, "v2", "DCA-ETH-CVX"]]
  assert registry.getFilteredProductionVaults("v1", 2) == [[vault_three, "v1", "DCA-BTC-CVX"]]
  assert registry.getFilteredProductionVaultsByMetadataAndStatus("DCA-BTC-CVX", 0) == [[vault_one, "v1", "DCA-BTC-CVX"]]
  assert registry.getFilteredProductionVaultsByMetadataAndStatus("DCA-ETH-CVX", 1) == [[vault_two, "v2", "DCA-ETH-CVX"]]
  assert registry.getFilteredProductionVaultsByMetadataAndStatus("DCA-BTC-CVX", 2) == [[vault_three, "v1", "DCA-BTC-CVX"]]

  with brownie.reverts():
    registry.demote("v1", "DCA-BTC-CVX", vault_one, 0, {"from": rando})
  
  ## devGov can demote
  registry.demote("v1", "DCA-BTC-CVX", vault_one, 0, {"from": devGov})

  assert registry.getFilteredProductionVaults("v1", 0) == []
  assert registry.getFilteredProductionVaults("v2", 1) == [[vault_two, "v2", "DCA-ETH-CVX"]]
  assert registry.getFilteredProductionVaults("v1", 2) == [[vault_three, "v1", "DCA-BTC-CVX"]]
  assert registry.getFilteredProductionVaultsByMetadataAndStatus("DCA-BTC-CVX", 0) == []
  assert registry.getFilteredProductionVaultsByMetadataAndStatus("DCA-ETH-CVX", 1) == [[vault_two, "v2", "DCA-ETH-CVX"]]
  assert registry.getFilteredProductionVaultsByMetadataAndStatus("DCA-BTC-CVX", 2) == [[vault_three, "v1", "DCA-BTC-CVX"]]

  ## Gov can demote
  registry.demote("v2", "DCA-ETH-CVX", vault_two, 1, {"from": gov})

  assert registry.getFilteredProductionVaults("v1", 0) == []
  assert registry.getFilteredProductionVaults("v2", 1) == []
  assert registry.getFilteredProductionVaults("v1", 2) == [[vault_three, "v1", "DCA-BTC-CVX"]]
  assert registry.getFilteredProductionVaultsByMetadataAndStatus("DCA-BTC-CVX", 0) == []
  assert registry.getFilteredProductionVaultsByMetadataAndStatus("DCA-ETH-CVX", 1) == []
  assert registry.getFilteredProductionVaultsByMetadataAndStatus("DCA-BTC-CVX", 2) == [[vault_three, "v1", "DCA-BTC-CVX"]]

  ## strategistGuild can demote
  registry.demote("v1", "DCA-BTC-CVX", vault_three, 2, {"from": strategistGuild})

  assert registry.getFilteredProductionVaults("v1", 0) == []
  assert registry.getFilteredProductionVaults("v2", 1) == []
  assert registry.getFilteredProductionVaults("v1", 2) == []
  assert registry.getFilteredProductionVaultsByMetadataAndStatus("DCA-BTC-CVX", 0) == []
  assert registry.getFilteredProductionVaultsByMetadataAndStatus("DCA-ETH-CVX", 1) == []
  assert registry.getFilteredProductionVaultsByMetadataAndStatus("DCA-BTC-CVX", 2) == []

