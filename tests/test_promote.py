import brownie
from brownie import ZERO_ADDRESS, accounts


def test_vault_promotion(registry, vault, rando, gov):

    # Author adds vault to their list
    registry.add("v1", vault, {"from": rando})
    assert registry.getVaults("v1", rando) == [vault]

    # Random user attempts to promote vault and reverts
    with brownie.reverts():
        registry.promote("v1", vault, 0, {"from": rando})

    # Governance is able to promote vault
    tx = registry.promote("v1", vault, 0, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 0) == [vault]

    event = tx.events["PromoteVault"][0]
    assert event["vault"] == vault

    # Same vault cannot be promoted twice (nothing happens)
    tx = registry.promote("v1", vault, 0, {"from": gov})
    assert len(tx.events) == 0


def test_vault_promotion_step_staging(registry, vault, rando, gov):
    registry.promote("v1", vault, 0, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 0) == [vault]

    registry.promote("v1", vault, 1, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 1) == [vault]

    ## After promoting a vault to the next steps, it's no longer in the previous step
    assert registry.getFilteredProductionVaults("v1", 0) == []

def test_vault_promotion_step_prod(registry, vault, rando, gov):
    registry.promote("v1", vault, 0, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 0) == [vault]

    registry.promote("v1", vault, 2, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 2) == [vault]

    ## After promoting a vault to the next steps, it's no longer in the previous steps
    assert registry.getFilteredProductionVaults("v1", 0) == []



def test_vault_promotion_permissions(registry, vault,vault_one, rando, gov, devGov,strategistGuild):
  ## If devGov promotes, the only step is 0
  # 
  # If gov promotes, it goes to any step
  # Rando can't promote 

  with brownie.reverts():
    registry.promote("v1", vault, 2, {"from": rando})
  
  ## Even though we put 2 here, we still only go to 0 because devGov is limited to it
  registry.promote("v1", vault, 2, {"from": devGov})
  assert registry.getFilteredProductionVaults("v1", 0) == [vault]
  assert registry.getFilteredProductionVaults("v1", 2) == []

  ## strategistGuild can promote to anything
  registry.promote("v1", vault, 2, {"from": strategistGuild})  
  ## And promoting cleans up lower ranks
  assert registry.getFilteredProductionVaults("v1", 0) == []
  assert registry.getFilteredProductionVaults("v1", 2) == [vault]

## Gov can promote to anything
  registry.promote("v1", vault_one, 2, {"from": gov})  
  ## And promoting cleans up lower ranks
  assert registry.getFilteredProductionVaults("v1", 0) == []
  assert registry.getFilteredProductionVaults("v1", 2) == [vault,vault_one]

