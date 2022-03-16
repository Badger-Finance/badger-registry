"""
    Deploy the Strategy Logic and the Proxy
"""
from typing import List
from scripts.helpers.connect_account import connect_account
import click
from brownie import (
    BadgerRegistry,
    StringsUtils,
    AdminUpgradeabilityProxy,
    config,
    web3,
    project,
)

## Load ContractContainers from Badger Vaults

proxyAdmin = web3.toChecksumAddress("0xB10b3Af646Afadd9C62D663dd5d226B15C25CdFA")


def deploy_registry_logic(logic, libraries: List = []):
    """
    Deploy the strat logic
    """
    dev = connect_account()

    if click.confirm("Deploy New Registry"):
        args = [dev.address, [], 1, False]  ## Give yourself governance

        for l in libraries:
            if len(l) == 0:
                l.deploy({"from": dev})

        strat_logic = logic.deploy({"from": dev})
        registry_proxy = AdminUpgradeabilityProxy.deploy(
            strat_logic,
            proxyAdmin,
            strat_logic.initialize.encode_input(*args),
            {"from": dev},
        )

        ## We delete from deploy and then fetch again so we can interact
        AdminUpgradeabilityProxy.remove(registry_proxy)
        registry_proxy = logic.at(registry_proxy.address)

        print(registry_proxy)
        print(dir(registry_proxy))
        click.echo(f"New Registry Release deployed [{registry_proxy.address}]")

        return registry_proxy


def main():
    strat = deploy_registry_logic(BadgerRegistry, [StringsUtils])
    return strat
