import brownie
from brownie import ZERO_ADDRESS, accounts


def test_update_metadata(registry, vault, rando, gov):
    # Author adds vault to their list
    registry.add(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", {"from": rando})
    assert registry.getVaults("v1", rando) == [[vault, "v1", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    registry.promote(vault, "v1", "name=BTC-CVX,protocol=Badger,behavior=DCA", 1, {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 1) == [[vault, "v1", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

    # Random user attempts to update metadata
    with brownie.reverts("!auth"):
        registry.updateMetadata(vault, "name=BTC-BADGER,protocol=Balancer,behavior=Ecosystem", {"from": rando})

    registry.setDeveloper(rando, {"from": gov})
    assert registry.developer() == rando
    
    # Developer attempts to update metadata
    with brownie.reverts("!auth"):
        registry.updateMetadata(vault, "name=BTC-BADGER,protocol=Balancer,behavior=Ecosystem", {"from": rando})

    # Gov attempts to update bad metadata
    with brownie.reverts("BadgerRegistry: Invalid Name"):
        registry.updateMetadata(vault, "CVX-BTC-DCA", {"from": gov})

    registry.updateMetadata(vault, "name=BTC-BADGER,protocol=Balancer,behavior=Ecosystem", {"from": gov})
    assert registry.getFilteredProductionVaults("v1", 1) == [[vault, "v1", "1", "name=BTC-BADGER,protocol=Balancer,behavior=Ecosystem"]]
