import brownie
import pytest
import itertools
from brownie import ZERO_ADDRESS, accounts


@pytest.mark.parametrize("metadata", ["", "MyMetadata"])
@pytest.mark.parametrize("state", [0, 1, 2, 3])
def test_vault_promotion(registry, vault, gov, metadata, state):
    version = "v1"
    tx = registry.promote(version, metadata, vault, state, {"from": gov})
    assert tx.events["PromoteVault"][0] == {
        "author": gov,
        "version": version,
        "metadata": metadata,
        "vault": vault,
        "status": state,
    }
    assert registry.getFilteredProductionVaults(version, metadata, state) == [vault]

    ## After promoting a vault to the next steps, it's no longer in the previous step
    if state != 0:
        assert vault not in registry.getFilteredProductionVaults(version, metadata, 0)


@pytest.mark.parametrize("metadata", ["", "MyMetadata"])
@pytest.mark.parametrize("state", [0, 1, 2, 3])
def test_vault_promotion(registry, vault, devGov, metadata, state):
    version = "v1"
    tx = registry.promote(version, metadata, vault, state, {"from": devGov})
    assert tx.events["PromoteVault"][0] == {
        "author": devGov,
        "version": version,
        "metadata": metadata,
        "vault": vault,
        "status": 0,
    }
    if state != 0:
        assert registry.getFilteredProductionVaults(version, metadata, state) == []
    assert registry.getFilteredProductionVaults(version, metadata, 0) == [vault]


@pytest.mark.parametrize("metadata", ["", "MyMetadata"])
def test_vault_promotion_permissions_and_getProductionVaults(
    registry, vault, vault_one, vault_two, vault_three, gov, devGov, rando, metadata
):
    ## Rando can't promote
    # If devGov promotes, the only step is 0
    # If gov promotes, it goes to any step

    ## Rando can't promote
    with brownie.reverts():
        registry.promote("v2", metadata, vault, 0, {"from": rando})

    ## Even though we put 2 here, we still only go to 0 because devGov is limited to it
    registry.promote("v1", metadata, vault, 2, {"from": devGov})

    ## Gov can promote to anything
    registry.promote("v2", metadata, vault_one, 1, {"from": gov})
    registry.promote("v1", metadata, vault_two, 2, {"from": gov})
    registry.promote("v2", metadata, vault_three, 3, {"from": gov})

    assert registry.getFilteredProductionVaults("v1", metadata, 0) == [vault]
    assert registry.getFilteredProductionVaults("v2", metadata, 1) == [vault_one]
    assert registry.getFilteredProductionVaults("v1", metadata, 2) == [vault_two]
    assert registry.getFilteredProductionVaults("v2", metadata, 3) == [vault_three]

    if metadata != "":
        registry.addMetadata(metadata, {"from": gov})

    result = registry.getProductionVaults()

    if metadata == "":
        assert result[0] == ("v1", 0, [vault], metadata)
        assert result[1] == ("v2", 0, [], metadata)
        assert result[2] == ("v1", 1, [], metadata)
        assert result[3] == ("v2", 1, [vault_one], metadata)
        assert result[4] == ("v1", 2, [vault_two], metadata)
        assert result[5] == ("v2", 2, [], metadata)
        assert result[6] == ("v1", 3, [], metadata)
        assert result[7] == ("v2", 3, [vault_three], metadata)
    else:
        assert result[0] == ("v1", 0, [], "")
        assert result[1] == ("v2", 0, [], "")
        assert result[2] == ("v1", 0, [vault], metadata)
        assert result[3] == ("v2", 0, [], metadata)
        assert result[4] == ("v1", 1, [], "")
        assert result[5] == ("v2", 1, [], "")
        assert result[6] == ("v1", 1, [], metadata)
        assert result[7] == ("v2", 1, [vault_one], metadata)
        assert result[8] == ("v1", 2, [], "")
        assert result[9] == ("v2", 2, [], "")
        assert result[10] == ("v1", 2, [vault_two], metadata)
        assert result[11] == ("v2", 2, [], metadata)
        assert result[12] == ("v1", 3, [], "")
        assert result[13] == ("v2", 3, [], "")
        assert result[14] == ("v1", 3, [], metadata)
        assert result[15] == ("v2", 3, [vault_three], metadata)


@pytest.mark.parametrize("metadata", ["", "MyMetadata"])
@pytest.mark.parametrize("state", [0, 1, 2, 3])
def test_vault_demotion(registry, vault, vault_one, devGov, gov, metadata, state):
    version = "v1"

    registry.promote(version, metadata, vault_one, state, {"from": devGov})
    registry.promote(version, metadata, vault, state, {"from": gov})

    if state == 0:
        assert registry.getFilteredProductionVaults(version, metadata, 0) == [
            vault_one,
            vault,
        ]
    else:
        assert registry.getFilteredProductionVaults(version, metadata, 0) == [vault_one]
        assert registry.getFilteredProductionVaults(version, metadata, state) == [vault]

    tx = registry.demote(version, metadata, vault, state)
    assert registry.getFilteredProductionVaults(version, metadata, 0) == [vault_one]
    if state != 0:
        assert registry.getFilteredProductionVaults(version, metadata, state) == []
    assert tx.events["DemoteVault"][0] == {
        "author": gov,
        "version": version,
        "metadata": metadata,
        "vault": vault,
        "status": state,
    }


@pytest.mark.parametrize("metadata", ["", "MyMetadata"])
@pytest.mark.parametrize("state", [0, 1, 2, 3])
def test_vault_demotion_permissions(registry, vault, rando, gov, metadata, state):
    version = "v1"
    registry.promote(version, metadata, vault, state, {"from": gov})
    with brownie.reverts():
        registry.demote(version, metadata, vault, state, {"from": rando})


def test_vault_promote_using_strategist_guild(registry, vault, gov, strategist_guild):
    versions = ["v1", "v2"]
    metadatas = ["", "MyMetadata"]
    states = [1, 2]

    i = 0
    for comb in itertools.product(versions, metadatas, states):
        tx = registry.promote(
            comb[0], comb[1], vault, comb[2], {"from": strategist_guild[i % 3]}
        )
        assert "PromoteVault" not in tx.events
        i += 1

    tx = registry.promote(
        versions[0], metadatas[0], vault, states[0], {"from": strategist_guild[1]}
    )
    assert tx.events["PromoteVault"][0] == {
        "author": strategist_guild[1],
        "version": versions[0],
        "metadata": metadatas[0],
        "vault": vault,
        "status": states[0],
    }
    assert registry.getFilteredProductionVaults(
        versions[0], metadatas[0], states[0]
    ) == [vault]
    assert (
        registry.getFilteredProductionVaults(versions[0], metadatas[0], states[1]) == []
    )
