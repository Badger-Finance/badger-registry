// SPDX-License-Identifier: GPL-3.0
pragma solidity =0.8.11;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

contract BadgerRegistry {
  using EnumerableSet for EnumerableSet.AddressSet;

  /// @dev is the vault at the experimental, guarded, open or deprecated stage? Only for Prod Vaults
  enum VaultStatus {
    deprecated,
    experimental,
    guarded,
    open
  }

  uint256 public constant VAULT_STATUS_LENGTH = 4;

  struct VaultInfo {
    address vault;
    string version;
    VaultStatus status;
    string metadata;
  }

  struct VaultMetadata {
    address vault;
    string metadata;
  }

  struct VaultData {
    string version;
    VaultStatus status;
    VaultMetadata[] list;
  }

  /// @dev Multisig. Vaults from here are considered Production ready
  address public governance;
  address public devGovernance; //@notice an address with some powers to make things easier in development
  address public strategistGuild;

  /// @dev Given an Author Address, and Version, Return the Vault
  mapping(address => mapping(string => EnumerableSet.AddressSet)) private vaults;

  /// @dev Given an Author Address, and Vault Address, Return the VaultInfo
  mapping(address => mapping(address => VaultInfo)) public vaultInfoByAuthorAndVault;

  mapping(string => address) public addresses;
  mapping(address => string) public keyByAddress;

  /// @dev Given Version and VaultStatus, returns the list of Vaults in production
  mapping(string => mapping(VaultStatus => EnumerableSet.AddressSet)) private productionVaults;

  /// @dev Given Vault Address, returns the VaultInfo in production
  mapping(address => VaultInfo) public productionVaultInfoByVault;

  // Known constants you can use
  string[] public keys; //@notice, you don't have a guarantee of the key being there, it's just a utility
  string[] public versions; //@notice, you don't have a guarantee of the key being there, it's just a utility

  event NewVault(address author, string version, string metadata, address vault);
  event RemoveVault(address author, string version, string metadata, address vault);
  event PromoteVault(address author, string version, string metadata, address vault, VaultStatus status);
  event DemoteVault(address author, string version, string metadata, address vault, VaultStatus status);
  event PurgeVault(address author, string version, string metadata, address vault, VaultStatus status);

  event Set(string key, address at);
  event AddKey(string key);
  event DeleteKey(string key);
  event AddVersion(string version);

  function initialize(address newGovernance, address newStrategistGuild) public {
    require(governance == address(0));
    governance = newGovernance;
    strategistGuild = newStrategistGuild;
    devGovernance = address(0);

    versions.push("v1"); //For v1
    versions.push("v1.5"); //For v1.5
    versions.push("v2"); //For v2
  }

  function setGovernance(address _newGov) public {
    require(msg.sender == governance, "!gov");
    governance = _newGov;
  }

  function setDev(address newDev) public {
    require(msg.sender == governance || msg.sender == devGovernance, "!gov");
    devGovernance = newDev;
  }

  function setStrategistGuild(address newStrategistGuild) public {
    require(msg.sender == governance, "!gov");
    strategistGuild = newStrategistGuild;
  }

  /// @dev Utility function to add Versions for Vaults,
  //@notice No guarantee that it will be properly used
  function addVersions(string memory version) public {
    require(msg.sender == governance, "!gov");
    versions.push(version);

    emit AddVersion(version);
  }

  /// @dev Anyone can add a vault to here, it will be indexed by their address
  function add(
    address vault,
    string memory version,
    string memory metadata
  ) public {
    VaultInfo memory existedVaultInfo = vaultInfoByAuthorAndVault[msg.sender][vault];
    if (existedVaultInfo.vault != address(0)) {
      require(
        // Compare strings via their hash because solidity
        vault == existedVaultInfo.vault &&
          keccak256(bytes(version)) == keccak256(bytes(existedVaultInfo.version)) &&
          keccak256(bytes(metadata)) == keccak256(bytes(existedVaultInfo.metadata)),
        "BadgerRegistry: vault info changed. Please remove before add changed vault info"
      );
      // Same vault cannot be added twice (nothing happens)
      return;
    }

    // Vault status start as experimental, this aids in promotion / demotion invariants
    vaultInfoByAuthorAndVault[msg.sender][vault] = VaultInfo({
      vault: vault,
      version: version,
      status: VaultStatus(1),
      metadata: metadata
    });

    vaults[msg.sender][version].add(vault);
    emit NewVault(msg.sender, version, metadata, vault);
  }

  /// @dev Remove the vault from your index
  function remove(address vault) public {
    VaultInfo memory existedVaultInfo = vaultInfoByAuthorAndVault[msg.sender][vault];
    if (existedVaultInfo.vault == address(0)) {
      return;
    }
    delete vaultInfoByAuthorAndVault[msg.sender][vault];
    bool removedFromVersionSet = vaults[msg.sender][existedVaultInfo.version].remove(vault);
    if (removedFromVersionSet) {
      emit RemoveVault(msg.sender, existedVaultInfo.version, existedVaultInfo.metadata, vault);
    }
  }

  /// @dev Promote a vault to Production
  /// @dev Promote just means indexed by the Governance Address
  function promote(address vault, VaultStatus status) public {
    require(msg.sender == governance || msg.sender == strategistGuild || msg.sender == devGovernance, "!auth");

    VaultStatus actualStatus = status;
    if (msg.sender == devGovernance) {
      actualStatus = VaultStatus.experimental;
    }

    VaultInfo memory existedVaultInfo = productionVaultInfoByVault[vault];
    require(existedVaultInfo.vault != address(0), "BadgerRegistry: Vault does not exist");
    // Value should be allowed to be equal to allow for promotion of vaults to experimental status as prod vaults
    require(uint256(actualStatus) >= uint256(existedVaultInfo.status), "BadgerRegistry: Vault is not being promoted");

    bool addedToVersionStatusSet = productionVaults[existedVaultInfo.version][actualStatus].add(vault);
    // If addedToVersionStatusSet remove from old and emit event
    if (addedToVersionStatusSet) {
      // also remove from old prod
      if (uint256(actualStatus) > 0) {
        for (uint256 status_ = uint256(actualStatus); status_ > 0; --status_) {
          productionVaults[existedVaultInfo.version][VaultStatus(status_ - 1)].remove(vault);
        }
      }

      emit PromoteVault(msg.sender, existedVaultInfo.version, existedVaultInfo.metadata, vault, actualStatus);
    }
  }

  function demote(address vault, VaultStatus status) public {
    require(msg.sender == governance || msg.sender == strategistGuild || msg.sender == devGovernance, "!auth");

    VaultStatus actualStatus = status;
    if (msg.sender == devGovernance) {
      actualStatus = VaultStatus.experimental;
    }

    VaultInfo memory existedVaultInfo = productionVaultInfoByVault[vault];
    require(existedVaultInfo.vault != address(0), "BadgerRegistry: Vault does not exist");
    // Value should be allowed to be equal to allow for promotion of vaults to experimental status as prod vaults
    require(uint256(actualStatus) < uint256(existedVaultInfo.status), "BadgerRegistry: Vault is not being demoted");

    bool removedFromVersionStatusSet = productionVaults[existedVaultInfo.version][actualStatus].remove(vault);
    if (removedFromVersionStatusSet) {
      if (uint256(actualStatus) < VAULT_STATUS_LENGTH - 1) {
        for (uint256 status_ = uint256(actualStatus); status_ <= VAULT_STATUS_LENGTH - 1; status_++) {
          productionVaults[existedVaultInfo.version][VaultStatus(status_)].remove(vault);
        }
      }
      emit DemoteVault(msg.sender, existedVaultInfo.version, existedVaultInfo.metadata, vault, status);
    }
  }

  function purge(address vault) public {
    require(msg.sender == governance || msg.sender == strategistGuild, "!auth");

    VaultInfo memory existedVaultInfo = productionVaultInfoByVault[vault];
    require(existedVaultInfo.vault != address(0), "BadgerRegistry: Vault does not exist");

    bool removedFromVersionStatusSet = productionVaults[existedVaultInfo.version][existedVaultInfo.status].remove(
      vault
    );
    bool deletedFromVaultInfoByVault = productionVaultInfoByVault[vault].vault != address(0);
    if (removedFromVersionStatusSet || deletedFromVaultInfoByVault) {
      delete productionVaultInfoByVault[vault];
      emit PurgeVault(msg.sender, existedVaultInfo.version, existedVaultInfo.metadata, vault, existedVaultInfo.status);
    }
  }

  /** KEY Management */

  /// @dev Set the value of a key to a specific address
  //@notice e.g. controller = 0x123123
  function set(string memory key, address at) public {
    require(msg.sender == governance, "!gov");
    _addKey(key);
    addresses[key] = at;
    keyByAddress[at] = key;
    emit Set(key, at);
  }

  /// @dev Delete a key
  function deleteKey(string memory key) external {
    require(msg.sender == governance, "!gov");
    _deleteKey(key);
  }

  function _deleteKey(string memory key) private {
    address at = addresses[key];
    delete keyByAddress[at];

    for (uint256 x = 0; x < keys.length; x++) {
      // Compare strings via their hash because solidity
      if (keccak256(bytes(key)) == keccak256(bytes(keys[x]))) {
        delete addresses[key];
        keys[x] = keys[keys.length - 1];
        keys.pop();
        emit DeleteKey(key);
        return;
      }
    }
  }

  /// @dev Delete keys
  function deleteKeys(string[] memory _keys) external {
    require(msg.sender == governance, "!gov");

    uint256 length = _keys.length;
    for (uint256 x = 0; x < length; ++x) {
      _deleteKey(_keys[x]);
    }
  }

  /// @dev Retrieve the value of a key
  function get(string memory key) public view returns (address) {
    return addresses[key];
  }

  /// @dev Get keys count
  function keysCount() public view returns (uint256) {
    return keys.length;
  }

  /// @dev Add a key to the list of keys
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

  /// @dev Retrieve a list of all Vaults from the given author and version
  function getVaults(string memory version, address author) public view returns (VaultInfo[] memory) {
    uint256 length = vaults[author][version].length();

    VaultInfo[] memory list = new VaultInfo[](length);
    for (uint256 i = 0; i < length; i++) {
      list[i] = vaultInfoByAuthorAndVault[author][vaults[author][version].at(i)];
    }
    return list;
  }

  /// @dev Retrieve a list of all Vaults that are in production, based on Version and Status
  function getFilteredProductionVaults(string memory version, VaultStatus status)
    public
    view
    returns (VaultInfo[] memory)
  {
    uint256 length = productionVaults[version][status].length();

    VaultInfo[] memory list = new VaultInfo[](length);
    for (uint256 i = 0; i < length; i++) {
      list[i] = productionVaultInfoByVault[productionVaults[version][status].at(i)];
    }
    return list;
  }

  function getProductionVaults() public view returns (VaultData[] memory) {
    uint256 versionsCount = versions.length;

    VaultData[] memory data = new VaultData[](versionsCount * VAULT_STATUS_LENGTH);

    for (uint256 x = 0; x < versionsCount; x++) {
      for (uint256 y = 0; y < VAULT_STATUS_LENGTH; y++) {
        uint256 length = productionVaults[versions[x]][VaultStatus(y)].length();
        VaultMetadata[] memory list = new VaultMetadata[](length);
        for (uint256 z = 0; z < length; z++) {
          VaultInfo storage vaultInfo = productionVaultInfoByVault[productionVaults[versions[x]][VaultStatus(y)].at(z)];
          list[z] = VaultMetadata({vault: vaultInfo.vault, metadata: vaultInfo.metadata});
        }
        data[x * VAULT_STATUS_LENGTH + y] = VaultData({version: versions[x], status: VaultStatus(y), list: list});
      }
    }

    return data;
  }

  /// @notice Metadata is used for offchain naming and information display of vaults
  /// @dev Metadata expected format: name=MyVault,protocol=Badger,
  function verifyMetadata(string memory metadata) internal returns (bool) {}
}
