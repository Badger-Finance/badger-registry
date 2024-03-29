<div> 
  <img align="right" src="docs/images/new_badger.png" height="150" width="150" />
</div>

# Badger Registry

NOTE: If you're finding this from Immunefi, all Vaults and Strategies listed in the live registries are in scope, as well as the contracts listed under keys.

The Badger Registry is the source of truth for any vaults or infrastructure curated and operated by Badger DAO.
The most current version of the registry is [version v0.2.1](https://github.com/Badger-Finance/badger-registry/releases/tag/v0.2.1).

The entities governing the Badger Registry are `governance`, `developer`, and the `strategistGuild`.
Officially endorsed vaults will be considered `production` vaults, available on the provided views.

All vaults in development, or considered by the DAO may be submitted by `developer` or the `strategistGuild`.

The registry proxy is deployed at the following address: 

```text
0xdc602965F3e5f1e7BAf2446d5564b407d5113A06
```

Thre registry logix deployed at the following address:

```text
0x00000b7665850f6b1e99447a68db1e83d8deafe3
```

This registry is currently deployed on the following networks:

- Ethereum
- Polygon
- Arbitrum
- Fantom

The registry also contains a set of key value mappings for the project infrastructure per chain.
These values may differ across chains.
However, a set of consistent keys for key infrastructure will always be included.
A non exhaustive list of these keys follows:

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

## Development

First, install node requirements.

```bash
yarn install
```

Then, set a virtual environment.

```bash
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Documentation

- Add Docusaurus link here once available
- This documentation will have some example usages

## Integrations

- [Badger SDK Implementation](https://github.com/Badger-Finance/badger-sdk/blob/main/src/registry.v2/registry.v2.service.ts)

## Key Items

The Badger Registry exposes a few select methods of interest to developers, the multisig, or members of the strategist guild.
These functions assist in the maintenance of the vault registries.

```solidity
function add(
  address vault,
  string memory version,
  string memory metadata
)
```

### add

Add allows the addition of vaults to the registry.
It is a permissionless operation - anyone can add to the registry in this way.
Practically, this will not impact the source of truth as only `governance`, `developer`, or the `strategistGuild` would be a non production trusted address.

```solidity
function promote(
  address vault,
  string memory version,
  string memory metadata,
  VaultStatus status
)
```

### promote

Promote allows vaults to be moved to a productionized vault in a given state.
Only specific roles may perform promotions.
A promoted vault is registered as production, and is integrated immediately with the subgraph and the API.
