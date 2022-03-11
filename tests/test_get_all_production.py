import brownie
from brownie import ZERO_ADDRESS, accounts


def test_vault_promotion_permissions(
    registry, vault, vault_one, vault_two, vault_three, gov, devGov
):
    ## If devGov promotes, the only step is 0
    #
    # If gov promotes, it goes to any step
    # Rando can't promote

    ## Even though we put 2 here, we still only go to 0 because devGov is limited to it
    registry.promote("v1", vault_one, 0, {"from": devGov})

    ## Gov can promote to anything
    registry.promote("v2", vault_two, 1, {"from": gov})
    registry.promote("v1", vault_three, 2, {"from": gov})

    assert registry.getFilteredProductionVaults("v1", 0) == [[vault_one], [""]]
    assert registry.getFilteredProductionVaults("v2", 1) == [[vault_two], [""]]
    assert registry.getFilteredProductionVaults("v1", 2) == [[vault_three], [""]]

    result = registry.getProductionVaults()

    assert result[0] == ("v1", 0, [vault_one])
    assert result[1] == ("v2", 0, [])
    assert result[2] == ("v1", 1, [])
    assert result[3] == ("v2", 1, [vault_two])
    assert result[4] == ("v1", 2, [vault_three])
    assert result[5] == ("v2", 2, [])
