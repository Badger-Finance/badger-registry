"""
    Deploy the Strategy Logic and the Proxy
"""
from scripts.helpers.connect_account import connect_account
import click
from brownie import BadgerRegistry, AdminUpgradeabilityProxy, config, web3, project

## Load ContractContainers from Badger Vaults

ETH_REGISTRY_CONFIG = {
    'proxyAdmin': web3.toChecksumAddress("0x20Dce41Acca85E8222D6861Aa6D23B6C941777bF"),
    'techOps': web3.toChecksumAddress("0x86cbD0ce0c087b482782c181dA8d191De18C8275"),
}
POLYGON_REGISTRY_CONFIG = {
    'proxyAdmin': web3.toChecksumAddress("0x9208E6c28959c47E58344d5f84d88F07Fca96CFC"),
    'techOps': web3.toChecksumAddress("0xeb7341c89ba46CC7945f75Bd5dD7a04f8FA16327"),
}
ARBITRUM_REGISTRY_CONFIG = {
    'proxyAdmin': web3.toChecksumAddress("0xBA77f65a97433d4362Db5c798987d6f0bD28faA3"),
    'techOps': web3.toChecksumAddress("0x292549E6bd5a41aE4521Bb8679aDA59631B9eD4C"),
}
FANTOM_REGISTRY_CONFIG = {
    'proxyAdmin': web3.toChecksumAddress("0x20Dce41Acca85E8222D6861Aa6D23B6C941777bF"),
    'techOps': web3.toChecksumAddress("0x781E82D5D49042baB750efac91858cB65C6b0582"),
}

def deploy_registry_logic(logic):
    """
    Deploy the strat logic
    """
    dev = connect_account()
    config = ETH_REGISTRY_CONFIG

    if click.confirm("Deploy New Registry"):
        args = [
            config['techOps'],
            config['techOps'],
        ]

        strat_logic = logic.deploy({'from': dev}, publish_source=True)
        registry_proxy = AdminUpgradeabilityProxy.deploy(strat_logic, config['proxyAdmin'], strat_logic.initialize.encode_input(*args), {'from': dev}, publish_source=True)
        
        ## We delete from deploy and then fetch again so we can interact
        AdminUpgradeabilityProxy.remove(registry_proxy)
        registry_proxy = logic.at(registry_proxy.address)

        print(registry_proxy)
        print(dir(registry_proxy))
        click.echo(f"New Registry Release deployed [{registry_proxy.address}]")

        return registry_proxy

def main():
    strat = deploy_registry_logic(BadgerRegistry)
    return strat