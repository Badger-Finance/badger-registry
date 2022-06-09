# badger-registry

This is a preserved README for v1 registry.
On Chain Registry for V1, V2 Vaults as well as Known Addresses via extensibly key address pairs

## Deployment Addresses

Mainnet
https://etherscan.io/address/0xfda7eb6f8b7a9e9fcfd348042ae675d1d652454f

Polygon:
https://polygonscan.com/address/0xfda7eb6f8b7a9e9fcfd348042ae675d1d652454f

Arbitrum:
https://arbiscan.io/address/0xFda7eB6f8b7a9e9fCFd348042ae675d1d652454f#code

Fantom
https://ftmscan.com/address/0xFda7eB6f8b7a9e9fCFd348042ae675d1d652454f

## Example Usage - Keys
### Get the Address of the Controller for this network
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
2. Get the registry ```registry = BadgerRegistry.at("ADDRESS FOR THE NETWORK YOU WANT")```
3. Get the keys ```registry.get("whatever")```


## More details

### Find keys without knowing what they are
Go spam `keys(uint)` with various indexes until you run out of range

### Find versions without knowing what they are
Go spam `versions(uint)` with various indexes until you run out of range

### Find Production Steps / Status for Vaults
Check the Enum `VaultStatus` for the steps


## List of Keys (incomplete)

By defintion the list of keys is incomplete, just iterate over the `keys(uint256)` to find them
Some of these keys may be missing in some deployments
While not a security vulnerability this may impact some of our flows
Please do create a ISSUE if you find a missing key

This is a list of keys we use at Badger to standardize cross-chain deployments

- controller
- guardian
- keeper
- badgerTree
- governance
- developer


- proxyAdminDev
- proxyAdminTimelock
- governanceTimelock
- timelock

- keeperAccessControl
- rewardsLogger

- BADGER
- ibBTC


## Use Cases from V2

### Get key name by address
`keyByAddress(address) external view returns (string)`

### Deprecated Vault Status
New Status, deprecated

### StrategistGuild
Fast Multisig that can do some major changes but can be replaced by governance

### Deletion of Keys
`deleteKey(string memory key)`

### Deletion of Vaults
`purge(address vault)`

