import brownie
from brownie import ZERO_ADDRESS, accounts

def test_get_production_vaults(registry, vault, vault_one, vault_two, vault_three, vault_four, gov, devGov):
  ## If devGov promotes, the only step is 0
  # 
  # If gov promotes, it goes to any step
  # Rando can't promote 
  
  ## Even though we put 2 here, we still only go to 1 because devGov is limited to it
  registry.promote(vault_one, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 0, {"from": devGov})
  assert registry.getFilteredProductionVaults("v1", 1) == [[vault_one, "v1", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]
  registry.demote(vault_one, 0, {"from": gov})

  ## Gov can promote to anything
  registry.promote(vault_two, "v2", "name=ETH-CVX,protocol=Badger,behavior=DCA", 1, {"from": gov})
  registry.promote(vault_three, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 2, {"from": gov})
  registry.promote(vault_four, "v2", "name=MATIC-CVX,protocol=Badger,behavior=DCA", 3, {"from": gov})

  assert registry.getFilteredProductionVaults("v1", 0) == [[vault_one, "v1", "0", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]
  assert registry.getFilteredProductionVaults("v2", 1) == [[vault_two, "v2", "1", "name=ETH-CVX,protocol=Badger,behavior=DCA"]]
  assert registry.getFilteredProductionVaults("v1", 2) == [[vault_three, "v1", "2", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]
  assert registry.getFilteredProductionVaults("v2", 3) == [[vault_four, "v2", "3", "name=MATIC-CVX,protocol=Badger,behavior=DCA"]]

  result = registry.getProductionVaults()

  assert result[0] == ("v1", 0, [[vault_one, "name=BTC-CVX,protocol=Badger,behavior=DCA"]])
  assert result[1] == ("v1", 1, [])
  assert result[2] == ("v1", 2, [[vault_three, "name=BTC-CVX,protocol=Badger,behavior=DCA"]])
  assert result[3] == ("v1", 3, [])
  assert result[4] == ("v1.5", 0, [])
  assert result[5] == ("v1.5", 1, [])
  assert result[6] == ("v1.5", 2, [])
  assert result[7] == ("v1.5", 3, [])
  assert result[8] == ("v2", 0, [])
  assert result[9] == ("v2", 1, [[vault_two, "name=ETH-CVX,protocol=Badger,behavior=DCA"]])
  assert result[10] == ("v2", 2, [])
  assert result[11] == ("v2", 3, [[vault_four, "name=MATIC-CVX,protocol=Badger,behavior=DCA"]])
