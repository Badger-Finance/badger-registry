// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.6.0 <0.7.0;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/utils/EnumerableSet.sol";

contract BadgerRegistry {
  using EnumerableSet for EnumerableSet.AddressSet;
  using EnumerableSet for EnumerableSet.Bytes32Set;

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
    string[] metadata;
  }

  /// @dev Multisig. Vaults from here are considered Production ready
  address public governance;
  /// @notice an address with some powers to make things easier in development
  address public devGovernance;
  /// @dev strategistGuild is entitled to do the entire promotion process
  address public strategistGuild;

  /// @dev Given an Author Address, and Token, Return the Vault
  mapping(address => mapping(string => EnumerableSet.AddressSet)) private vaults;
  /// @dev Stores the metadata of a vault
  mapping(address => string) private metadata;

  /// @dev Given an Key return the vault
  mapping(string => address) public addresses;

  /// @dev Given an vault it returns the key
  mapping(address => string) public keys;
  /// @dev counts all keys that are stored in the keys mapping
  uint256 public keysCount;

  /// @dev Given Version and VaultStatus, returns the list of Vaults in production
  mapping(bytes32 => mapping(VaultStatus => EnumerableSet.AddressSet)) private productionVaults;

  // Known constants you can use
  EnumerableSet.Bytes32Set private versions; //@notice, you don't have a guarantee of the key being there, it's just a utility

  ///@dev versionLookup can be used to get a string representation of the stored keccak hash
  mapping(bytes32 => string) versionLookup;

  event NewVault(address author, string version, address vault);
  event RemoveVault(address author, string version, address vault);
  event PromoteVault(address author, string version, address vault, VaultStatus status);
  event DemoteVault(address author, string version, address vault, VaultStatus status);

  event KeyAdded(string key, address at);
  event KeyDeleted(string key, address at);

  event AddVersion(string version);

  constructor(address _newGovernance) public {
    governance = _newGovernance;
    versions.add(keccak256(abi.encode("v1"))); //For v1
    versions.add(keccak256(abi.encode("v2"))); //For v2

    versionLookup[keccak256(abi.encode("v1"))] = "v1";
    versionLookup[keccak256(abi.encode("v2"))] = "v2";
  }

  modifier onlyGovernance() {
    require(msg.sender == governance, "!gov");
    _;
  }

  modifier onlyDev() {
    require(msg.sender == governance || msg.sender == devGovernance, "!gov");
    _;
  }

  modifier onlyPromoter() {
    require(
      msg.sender == governance || msg.sender == strategistGuild || msg.sender == devGovernance,
      "you are not allowed to promote"
    );
    _;
  }

  modifier versionGuard(string memory _version) {
    require(versions.contains(keccak256(abi.encode(_version))), "version is not supported");
    _;
  }

  function setGovernance(address _newGov) public onlyGovernance {
    governance = _newGov;
  }

  function setDev(address _newDev) public onlyDev {
    devGovernance = _newDev;
  }

  function setStrategistGuild(address _newStrategist) public onlyGovernance {
    strategistGuild = _newStrategist;
  }

  //@dev Utility function to add Versions for Vaults,
  //@notice No guarantee that it will be properly used
  function addVersions(string memory _version) public onlyGovernance {
    require(msg.sender == governance, "!gov");
    versions.add(keccak256(abi.encode((_version))));
    versionLookup[keccak256(abi.encode(_version))] = _version;

    emit AddVersion(_version);
  }

  //@dev Anyone can add a vault to here, it will be indexed by their address
  function add(
    string memory _version,
    address _vault,
    string memory _metadata
  ) public versionGuard(_version) {
    bool added = vaults[msg.sender][_version].add(_vault);
    metadata[_vault] = _metadata;
    if (added) {
      emit NewVault(msg.sender, _version, _vault);
    }
  }

  //@dev Remove the vault from your index
  function remove(string memory version, address _vault) public {
    bool removed = vaults[msg.sender][version].remove(_vault);
    if (removed) {
      emit RemoveVault(msg.sender, version, _vault);
    }
  }

  //@dev Promote a vault to Production
  //@dev Promote just means indexed by the Governance Address
  function promote(
    string memory _version,
    address _vault,
    VaultStatus _status
  ) public onlyPromoter versionGuard(_version) {
    require(_status != VaultStatus(3), "can't promote to deprecated");

    VaultStatus actualStatus = _status;
    if (msg.sender == devGovernance) {
      actualStatus = VaultStatus.experimental;
    }

    bytes32 version = keccak256(abi.encode(_version));

    bool added = productionVaults[version][actualStatus].add(_vault);

    // If added remove from old and emit event
    if (added) {
      // also remove from old prod
      if (uint256(actualStatus) == 2) {
        //Cant use promte to lower the status
        bool wasProviouslyDeprecated = productionVaults[version][VaultStatus(3)].contains(_vault);
        require(!wasProviouslyDeprecated, "vault's prevoius status needs to be lower than the new status");
        // Remove from prev2
        productionVaults[version][VaultStatus(0)].remove(_vault);
        productionVaults[version][VaultStatus(1)].remove(_vault);
      }
      if (uint256(actualStatus) == 1) {
        bool wasProviouslyDeprecated = productionVaults[version][VaultStatus(3)].contains(_vault);
        bool wasProviouslyOpen = productionVaults[version][VaultStatus(2)].contains(_vault);
        require(
          !(wasProviouslyDeprecated || wasProviouslyOpen),
          "vault's prevoius status needs to be lower than the new status"
        );
        // Remove from prev1
        productionVaults[version][VaultStatus(0)].remove(_vault);
      }

      emit PromoteVault(msg.sender, _version, _vault, actualStatus);
    }
  }

  function demote(
    string memory _version,
    address _vault,
    VaultStatus _status
  ) public onlyPromoter versionGuard(_version) {
    require(_status != VaultStatus(2), "can't demote to production");

    VaultStatus actualStatus = _status;
    if (msg.sender == devGovernance) {
      actualStatus = VaultStatus.experimental;
    }

    bytes32 version = keccak256(abi.encode(_version));

    bool added = productionVaults[version][actualStatus].add(_vault);
    // Demote vault to depreacted
    if (uint256(actualStatus) == 3) {
      productionVaults[version][VaultStatus(0)].remove(_vault);
      productionVaults[version][VaultStatus(1)].remove(_vault);
      productionVaults[version][VaultStatus(2)].remove(_vault);
    }
    // Demote vault to guarded
    if (uint256(actualStatus) == 1) {
      bool wasPrevioslyExperimental = productionVaults[version][VaultStatus(0)].contains(_vault);
      require(!wasPrevioslyExperimental, "vault's prevoius status needs to be lower than the new status");

      productionVaults[version][VaultStatus(2)].remove(_vault);
    }

    // Demote vault to experimental

    if (uint256(actualStatus) == 0) {
      productionVaults[version][VaultStatus(1)].remove(_vault);
      productionVaults[version][VaultStatus(2)].remove(_vault);
    }

    if (added) {
      emit DemoteVault(msg.sender, _version, _vault, _status);
    }
  }

  /** KEY Management */

  //@dev Set the value of a key to a specific address
  //@notice e.g. controller = 0x123123
  function addKey(string memory _key, address _at) public onlyGovernance {
    keys[_at] = _key;
    addresses[_key] = _at;
    keysCount++;
    emit KeyAdded(_key, _at);
  }

  //@dev Delete a key
  function deleteKey(string memory _key) public onlyGovernance {
    address at = addresses[_key];
    delete keys[at];
    delete addresses[_key];
    keysCount--;
    emit KeyDeleted(_key, at);
  }

  //@dev Retrieve the value of a key
  function getAddressOfKey(string memory _key) public view returns (address) {
    return addresses[_key];
  }

  //@dev Retrieve the key of a value
  function getKeyOfAddress(address _value) public view returns (string memory) {
    return keys[_value];
  }

  //@dev Retrieve a list of all Vault Addresses from the given author
  function getVaults(string memory _version, address _author)
    public
    view
    returns (address[] memory vaultAddresses, string[] memory vaultMetadata)
  {
    uint256 length = vaults[_author][_version].length();

    vaultAddresses = new address[](length);
    vaultMetadata = new string[](length);

    for (uint256 i = 0; i < length; i++) {
      address currentVault = vaults[_author][_version].at(i);
      vaultAddresses[i] = currentVault;
      vaultMetadata[i] = metadata[currentVault];
    }
  }

  //@dev Retrieve a list of all Vaults that are in production, based on Version and Status
  function getFilteredProductionVaults(string memory _version, VaultStatus _status)
    public
    view
    returns (address[] memory vaultAddresses, string[] memory vaultMetadata)
  {
    bytes32 version = keccak256(abi.encode(_version));

    uint256 length = productionVaults[version][_status].length();

    vaultAddresses = new address[](length);
    vaultMetadata = new string[](length);

    address[] memory list = new address[](length);
    for (uint256 i = 0; i < length; i++) {
      address currentVault = productionVaults[version][_status].at(i);
      vaultAddresses[i] = productionVaults[version][_status].at(i);
      vaultMetadata[i] = metadata[currentVault];
    }
  }

  function getProductionVaults() public view returns (VaultData[] memory vaultData) {
    uint256 versionsCount = versions.length();

    vaultData = new VaultData[](versionsCount * 3);

    for (uint256 x = 0; x < versionsCount; x++) {
      for (uint256 y = 0; y < 3; y++) {
        uint256 length = productionVaults[versions.at(x)][VaultStatus(y)].length();
        address[] memory vaultAddresses = new address[](length);
        string[] memory vaultMetadata = new string[](length);

        for (uint256 z = 0; z < length; z++) {
          address currentVault = productionVaults[versions.at(x)][VaultStatus(y)].at(z);

          vaultAddresses[z] = currentVault;
          vaultMetadata[z] = metadata[currentVault];
        }
        vaultData[x * (versionsCount - 1) + y * 2] = VaultData({
          version: versionLookup[versions.at(x)],
          status: VaultStatus(y),
          list: vaultAddresses,
          metadata: vaultMetadata
        });
      }
    }
  }
}
