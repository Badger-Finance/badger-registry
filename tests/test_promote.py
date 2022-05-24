import brownie
from brownie import ZERO_ADDRESS, accounts


def test_vault_promotion(registry, vault, rando, gov):

    # Author adds vault to their list
    registry.add(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", {"from": rando})
    assert registry.getVaults("v1", rando) == [[vault, "v1", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    # Random user attempts to promote vault and reverts
    with brownie.reverts():
        registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 1, {"from": rando})

    # Gov user attempts to promote vault with bad metadata and reverts
    with brownie.reverts():
        registry.promote(vault, "v1", "DCA-BTC-CVX", 1, {"from": gov})

    # Governance is able to promote vault
    tx = registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 1, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 1) == [[vault, "v1", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    event = tx.events["PromoteVault"][0]
    assert event["vault"] == vault

    # Promoted to a higher status
    tx = registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 2, {"from": gov})
    assert len(tx.events) == 1
    assert registry.getFilteredProductionVaults("v1", 2) == [[vault, "v1", "2", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

def test_vault_promotion_by_strategist_guild(registry, vault, strategistGuild):
    registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 1, {"from": strategistGuild})
    assert registry.getFilteredProductionVaults("v1", 1) == [[vault, "v1", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

def test_vault_promotion_step_staging(registry, vault, rando, gov):
    registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 1, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 1) == [[vault, "v1", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 2, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 2) == [[vault, "v1", "2", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    ## After promoting a vault to the next steps, it's no longer in the previous step
    assert registry.getFilteredProductionVaults("v1", 1) == []

def test_vault_promotion_step_prod(registry, vault, rando, gov):
    registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 1, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 1) == [[vault, "v1", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 3, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 3) == [[vault, "v1", "3", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    ## After promoting a vault to the next steps, it's no longer in the previous steps
    assert registry.getFilteredProductionVaults("v1", 0) == []

def test_vault_promotion_step_deprecated(registry, vault, rando, gov):
    registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 0, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 0) == [[vault, "v1", "0", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 3, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 3) == [[vault, "v1", "3", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    ## After promoting a vault to the next steps, it's no longer in the previous steps
    assert registry.getFilteredProductionVaults("v1", 0) == []

def test_vault_promotion_permissions(registry, vault, rando, gov, devGov):
  ## If devGov promotes, the only step is 0
  # 
  # If gov promotes, it goes to any step
  # Rando can't promote 

  with brownie.reverts():
    registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 2, {"from": rando})
  
  ## Even though we put 2 here, we still only go to 0 because devGov is limited to it
  registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 2, {"from": devGov})
  assert registry.getFilteredProductionVaults("v1", 1) == [[vault, "v1", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]
  assert registry.getFilteredProductionVaults("v1", 2) == []

  ## Gov can promote to anything
  registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 2, {"from": gov})
  ## And promoting cleans up lower ranks
  assert registry.getFilteredProductionVaults("v1", 1) == []
  assert registry.getFilteredProductionVaults("v1", 2) == [[vault, "v1", "2", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]
