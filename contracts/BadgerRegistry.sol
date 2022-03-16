// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.6.0 <0.7.0;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/utils/EnumerableSet.sol";
import "./utils/StringsUtils.sol";

contract BadgerRegistry {
    using EnumerableSet for EnumerableSet.Bytes32Set;
    using EnumerableSet for EnumerableSet.AddressSet;
    using StringsUtils for string;
    using StringsUtils for bytes32;

    //@dev is the vault at the experimental, guarded or open stage? Only for Prod Vaults
    enum VaultStatus {
        experimental,
        guarded,
        open,
        deprecated
    }

    struct VaultData {
        string version;
        VaultStatus status;
        address[] list;
        string metadata;
    }

    //@dev Multisig. Vaults from here are considered Production ready
    address public governance;
    address public devGovernance; //@notice an address with some powers to make things easier in development

    //@dev Given an Author Address, and Token, Return the Vault
    mapping(address => mapping(string => EnumerableSet.AddressSet))
        private vaults;
    //@dev Given a Key, Return the Address
    mapping(string => address) public addresses;

    //@dev Given Version and VaultStatus, returns the list of Vaults in production
    mapping(string => mapping(VaultStatus => EnumerableSet.AddressSet))
        private productionVaults;

    // Known constants you can use
    string[] public keys; //@notice, you don't have a guarantee of the key being there, it's just a utility
    string[] public versions; //@notice, you don't have a guarantee of the key being there, it's just a utility

    uint256 internal statusCount;
    address[] public strategistGuild;
    uint256 public multiSigThreshold;
    string[] public productionMetadatas;
    //@dev Given an address, return its membership in strategistGuild
    mapping(address => bool) public isStrategist;
    mapping(bytes32 => uint256) public promoteConfirmations;
    //@dev Given an Author Address, Version and Metadata, Return the list of Vaults
    mapping(address => mapping(string => mapping(string => EnumerableSet.AddressSet)))
        internal vaultsWithMetadata;
    //@dev Given Version, Metadata and VaultStatus, returns the list of Vaults in production
    mapping(string => mapping(string => mapping(VaultStatus => EnumerableSet.AddressSet)))
        internal productionVaultsWithMetadata;
    //@dev Given an Address, Return the Keys
    mapping(address => EnumerableSet.Bytes32Set) internal address2Keys;

    event NewVault(
        address author,
        string version,
        string metadata,
        address vault
    );
    event RemoveVault(
        address author,
        string version,
        string metadata,
        address vault
    );
    event PromoteVault(
        address author,
        string version,
        string metadata,
        address vault,
        VaultStatus status
    );
    event DemoteVault(
        address author,
        string version,
        string metadata,
        address vault,
        VaultStatus status
    );

    event SetKey(string key, address at);
    event AddKey(string key);
    event DeleteKey(string key);
    event AddVersion(string version);
    event AddMetadata(string metadata);

    modifier onlyGov() {
        require(msg.sender == governance, "!gov");
        _;
    }

    modifier onlyGovOrDev() {
        require(
            msg.sender == governance || msg.sender == devGovernance,
            "!gov,!dev"
        );
        _;
    }

    function initialize(
        address newGovernance,
        address[] memory _strategistGuild,
        uint256 _multiSigThreshold,
        bool address2KeysInitialization
    ) public {
        if (address2KeysInitialization) {
            initializeAddress2Keys();
            return;
        }

        require(
            governance == address(0) &&
                strategistGuild.length == 0 &&
                _multiSigThreshold > 0
        );
        governance = newGovernance;
        devGovernance = address(0);
        for (uint256 i = 0; i < _strategistGuild.length; i++) {
            address owner = _strategistGuild[i];
            require(owner != address(0));
            isStrategist[owner] = true;
        }
        strategistGuild = _strategistGuild;
        multiSigThreshold = _multiSigThreshold;

        versions.push("v1"); //For v1
        versions.push("v2"); //For v2

        productionMetadatas.push("");

        statusCount = 4;
    }

    //@dev Just for migrating current keys from the old version to the new contract when upgrading the proxy
    function initializeAddress2Keys() internal onlyGovOrDev {
        for (uint256 i = 0; i < keys.length; i++) {
            string storage key = keys[i];
            address target = addresses[key];
            address2Keys[target].add(key.toBytes32());
        }
    }

    function setGovernance(address _newGov) public onlyGov {
        governance = _newGov;
    }

    function setDev(address newDev) public onlyGovOrDev {
        devGovernance = newDev;
    }

    function setStrategistGuild(
        address[] memory _strategistGuild,
        uint256 _multiSigThreshold
    ) public onlyGov {
        require(_multiSigThreshold > 0);
        for (uint256 i = 0; i < strategistGuild.length; i++) {
            isStrategist[strategistGuild[i]] = false;
        }
        for (uint256 i = 0; i < _strategistGuild.length; i++) {
            address owner = _strategistGuild[i];
            require(owner != address(0));
            isStrategist[owner] = true;
        }
        strategistGuild = _strategistGuild;
        multiSigThreshold = _multiSigThreshold;
    }

    //@dev Utility function to add Versions for Vaults,
    //@notice No guarantee that it will be properly used
    function addVersion(string memory version) public onlyGov {
        versions.push(version);

        emit AddVersion(version);
    }

    //@dev Utility function to add Metadata for Vaults,
    //@notice No guarantee that it will be properly used
    function addMetadata(string memory metadata) public onlyGov {
        productionMetadatas.push(metadata);

        emit AddMetadata(metadata);
    }

    //@dev Anyone can add a vault to here, it will be indexed by their address
    function add(
        string memory version,
        string memory metadata,
        address vault
    ) public {
        bool added = _getVaultSet(msg.sender, version, metadata).add(vault);
        if (added) {
            emit NewVault(msg.sender, version, metadata, vault);
        }
    }

    //@dev Remove the vault from your index
    function remove(
        string memory version,
        string memory metadata,
        address vault
    ) public {
        bool removed = _getVaultSet(msg.sender, version, metadata).remove(
            vault
        );
        if (removed) {
            emit RemoveVault(msg.sender, version, metadata, vault);
        }
    }

    //@dev Promote a vault to Production
    //@dev Promote just means indexed by the Governance Address
    function promote(
        string memory version,
        string memory metadata,
        address vault,
        VaultStatus status
    ) public {
        require(
            msg.sender == governance ||
                msg.sender == devGovernance ||
                isStrategist[msg.sender],
            "!gov"
        );

        if (isStrategist[msg.sender]) {
            bytes32 parameters = keccak256(
                abi.encode(version, metadata, vault, status)
            );
            promoteConfirmations[parameters] += 1;
            if (promoteConfirmations[parameters] < multiSigThreshold) {
                return;
            }
            promoteConfirmations[parameters] = 0;
        }

        _promote(version, metadata, vault, status);
    }

    function _promote(
        string memory version,
        string memory metadata,
        address vault,
        VaultStatus status
    ) internal {
        VaultStatus actualStatus = status;
        if (msg.sender == devGovernance) {
            actualStatus = VaultStatus.experimental;
        }

        bool added = _getProductionVaultSet(version, actualStatus, metadata)
            .add(vault);

        // If added remove from old and emit event
        if (added) {
            // also remove from old prod
            for (uint256 i = 0; i < uint256(actualStatus); i++) {
                _getProductionVaultSet(version, VaultStatus(i), metadata)
                    .remove(vault);
            }

            emit PromoteVault(
                msg.sender,
                version,
                metadata,
                vault,
                actualStatus
            );
        }
    }

    function demote(
        string memory version,
        string memory metadata,
        address vault,
        VaultStatus status
    ) public onlyGovOrDev {
        VaultStatus actualStatus = status;
        if (msg.sender == devGovernance) {
            actualStatus = VaultStatus.experimental;
        }

        bool removed = _getProductionVaultSet(version, actualStatus, metadata)
            .remove(vault);

        if (removed) {
            emit DemoteVault(msg.sender, version, metadata, vault, status);
        }
    }

    /* KEY Management */

    //@dev Set the value of a key to a specific address
    //@notice e.g. controller = 0x123123
    function setKey(string memory key, address at) public onlyGov {
        require(bytes(key).length <= 32);
        _addKey(key);
        address oldAt = addresses[key];
        if (oldAt != at) {
            // Set new address
            addresses[key] = at;
            // Remove key from oldAt's keys
            address2Keys[oldAt].remove(key.toBytes32());
            // Add key to at's keys
            address2Keys[at].add(key.toBytes32());
            emit SetKey(key, at);
        }
    }

    //@dev Delete a key
    function deleteKey(string memory key) public onlyGov {
        for (uint256 x = 0; x < keys.length; x++) {
            // Compare strings via their hash because solidity
            if (keccak256(bytes(key)) == keccak256(bytes(keys[x]))) {
                address target = addresses[key];
                delete addresses[key];
                address2Keys[target].remove(key.toBytes32());
                keys[x] = keys[keys.length - 1];
                keys.pop();
                emit DeleteKey(key);
                return;
            }
        }
    }

    //@dev Retrieve the value of a key
    function getTargetOfKey(string memory key) public view returns (address) {
        return addresses[key];
    }

    //@dev Retrieve the keys of an address
    function getKeysOfTarget(address target)
        public
        view
        returns (string[] memory)
    {
        EnumerableSet.Bytes32Set storage keySet = address2Keys[target];
        uint256 length = keySet.length();
        string[] memory list = new string[](length);
        for (uint256 i = 0; i < length; i++) {
            list[i] = keySet.at(i).toString();
        }
        return list;
    }

    //@dev Get keys count
    function keysCount() public view returns (uint256) {
        return keys.length;
    }

    //@dev Add a key to the list of keys
    //@notice This is used to make it easier to discover keys,
    //@notice however you have no guarantee that all keys will be in the list
    function _addKey(string memory key) internal {
        //If we find the key, skip
        for (uint256 x = 0; x < keys.length; x++) {
            // Compare strings via their hash because solidity
            if (keccak256(bytes(key)) == keccak256(bytes(keys[x]))) {
                return;
            }
        }

        // Else let's add it and emit the event
        keys.push(key);

        emit AddKey(key);
    }

    function _getVaultSet(
        address author,
        string memory version,
        string memory metadata
    ) internal view returns (EnumerableSet.AddressSet storage) {
        if (bytes(metadata).length == 0) {
            return vaults[author][version];
        } else {
            return vaultsWithMetadata[author][version][metadata];
        }
    }

    function _getProductionVaultSet(
        string memory version,
        VaultStatus status,
        string memory metadata
    ) internal view returns (EnumerableSet.AddressSet storage) {
        if (bytes(metadata).length == 0) {
            return productionVaults[version][status];
        } else {
            return productionVaultsWithMetadata[version][metadata][status];
        }
    }

    //@dev Retrieve a list of all Vault Addresses from the given author
    function getVaults(
        string memory version,
        string memory metadata,
        address author
    ) public view returns (address[] memory) {
        EnumerableSet.AddressSet storage vaultSet = _getVaultSet(
            author,
            version,
            metadata
        );
        uint256 length = vaultSet.length();

        address[] memory list = new address[](length);
        for (uint256 i = 0; i < length; i++) {
            list[i] = vaultSet.at(i);
        }
        return list;
    }

    //@dev Retrieve a list of all Vaults that are in production, based on Version and Status
    function getFilteredProductionVaults(
        string memory version,
        string memory metadata,
        VaultStatus status
    ) public view returns (address[] memory) {
        EnumerableSet.AddressSet storage vaultSet = _getProductionVaultSet(
            version,
            status,
            metadata
        );
        uint256 length = vaultSet.length();

        address[] memory list = new address[](length);
        for (uint256 i = 0; i < length; i++) {
            list[i] = vaultSet.at(i);
        }
        return list;
    }

    function getProductionVaults() public view returns (VaultData[] memory) {
        uint256 versionsCount = versions.length;
        uint256 metadataCount = productionMetadatas.length;
        uint256 countsMultiply = versionsCount * metadataCount;

        VaultData[] memory data = new VaultData[](
            versionsCount * metadataCount * statusCount
        );

        for (uint256 x = 0; x < versionsCount; x++) {
            for (uint256 y = 0; y < metadataCount; y++) {
                for (uint256 z = 0; z < statusCount; z++) {
                    EnumerableSet.AddressSet
                        storage vaultSet = _getProductionVaultSet(
                            versions[x],
                            VaultStatus(z),
                            productionMetadatas[y]
                        );
                    uint256 length = vaultSet.length();
                    address[] memory list = new address[](length);
                    for (uint256 i = 0; i < length; i++) {
                        list[i] = vaultSet.at(i);
                    }
                    data[
                        x + y * versionsCount + z * countsMultiply
                    ] = VaultData({
                        version: versions[x],
                        status: VaultStatus(z),
                        list: list,
                        metadata: productionMetadatas[y]
                    });
                }
            }
        }

        return data;
    }
}
