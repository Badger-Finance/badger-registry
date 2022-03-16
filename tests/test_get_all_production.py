import brownie
from brownie import ZERO_ADDRESS, accounts

def test_get_production_vaults(registry, vault, vault_one, vault_two, vault_three, vault_four, gov, devGov):
  ## If devGov promotes, the only step is 0
  # 
  # If gov promotes, it goes to any step
  # Rando can't promote 
  
  ## Even though we put 2 here, we still only go to 0 because devGov is limited to it
  registry.promote("v1", "DCA-BTC-CVX", vault_one, 0, {"from": devGov})

  ## Gov can promote to anything
  registry.promote("v2", "DCA-ETH-CVX", vault_two, 1, {"from": gov})
  registry.promote("v1", "DCA-BTC-CVX", vault_three, 2, {"from": gov})
  registry.promote("v2", "DCA-MATIC-CVX", vault_four, 3, {"from": gov})

  assert registry.getFilteredProductionVaults("v1", 0) == [[vault_one, "v1", "DCA-BTC-CVX"]]
  assert registry.getFilteredProductionVaults("v2", 1) == [[vault_two, "v2", "DCA-ETH-CVX"]]
  assert registry.getFilteredProductionVaults("v1", 2) == [[vault_three, "v1", "DCA-BTC-CVX"]]
  assert registry.getFilteredProductionVaults("v2", 3) == [[vault_four, "v2", "DCA-MATIC-CVX"]]

  result = registry.getProductionVaults()

  assert result[0] == ("v1", 0, [[vault_one, "DCA-BTC-CVX"]])
  assert result[1] == ("v1", 1, [])
  assert result[2] == ("v1", 2, [[vault_three, "DCA-BTC-CVX"]])
  assert result[3] == ("v1", 3, [])
  assert result[4] == ("v2", 0, [])
  assert result[5] == ("v2", 1, [[vault_two, "DCA-ETH-CVX"]])
  assert result[6] == ("v2", 2, [])
  assert result[7] == ("v2", 3, [[vault_four, "DCA-MATIC-CVX"]])

def test_get_filtered_production_vaults_by_metadata_and_status(registry, vault_one, vault_two, vault_three, vault_four, gov):
  registry.promote("v1", "DCA-BTC-CVX", vault_one, 0, {"from": gov})
  registry.promote("v2", "DCA-ETH-CVX", vault_two, 1, {"from": gov})
  registry.promote("v1", "DCA-BTC-CVX", vault_three, 2, {"from": gov})
  registry.promote("v1", "DCA-ETH-CVX", vault_four, 1, {"from": gov})

  assert registry.getFilteredProductionVaultsByMetadataAndStatus("DCA-BTC-CVX", 0) == [[vault_one, "v1", "DCA-BTC-CVX"]]
  assert registry.getFilteredProductionVaultsByMetadataAndStatus("DCA-ETH-CVX", 1) == [[vault_two, "v2", "DCA-ETH-CVX"], [vault_four, "v1", "DCA-ETH-CVX"]]
  assert registry.getFilteredProductionVaultsByMetadataAndStatus("DCA-BTC-CVX", 2) == [[vault_three, "v1", "DCA-BTC-CVX"]]
