import brownie
from brownie import ZERO_ADDRESS


def test_add_version(registry, gov):
    version = "v3"
    tx = registry.addVersion(version, {"from": gov})
    assert registry.versions(2) == version
    assert tx.events["AddVersion"][0] == {"version": version}


def test_add_version_permissions(registry, rando):
    version = "v3"
    with brownie.reverts():
        registry.addVersion(version, {"from": rando})


def test_add_metadata(registry, gov):
    metadata = "MyMetadata"
    tx = registry.addMetadata(metadata, {"from": gov})
    assert registry.productionMetadatas(1) == metadata
    assert tx.events["AddMetadata"][0] == {"metadata": metadata}


def test_add_metadata_permissions(registry, rando):
    metadata = "MyMetadata"
    with brownie.reverts():
        registry.addMetadata(metadata, {"from": rando})
