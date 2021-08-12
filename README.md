# badger-registry
On Chain Registry for V1, V2 Vaults as well as Known Addresses via extensibly key address pairs


## Deployment Addresses

Mainnet
https://etherscan.io/address/0xfda7eb6f8b7a9e9fcfd348042ae675d1d652454f

Polygon:
https://polygonscan.com/address/0xfda7eb6f8b7a9e9fcfd348042ae675d1d652454f

## Example Usage - Keys
### Get the Address of the Controller for this network
```registry.get("controller")```

## Example Usage - Vaults

### Retrieve Live Production Vault that use V1 Architecture

```registry.getFilteredProductionVaults("v1", 2);```

### Retrieve Experimental V2 Production Vaults
```registry.getFilteredProductionVaults("v2", 0);```

### Get all Production Vaults, separated by Version and Type
```registry.getProductionVaults();```

## Brownie Usage

1. Run The Console ```brownie console```
2. Get the registry ```Registry.at("ADDRESS FOR THE NETWORK YOU WANT")```
3. Get the keys ```Registry.get("whatever")```

