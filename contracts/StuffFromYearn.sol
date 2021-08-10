// Data from Vault
struct StrategyParams {
  uint256 performanceFee;
  uint256 activation;
  uint256 debtRatio;
  uint256 minDebtPerHarvest;
  uint256 maxDebtPerHarvest;
  uint256 lastReport;
  uint256 totalDebt;
  uint256 totalGain;
  uint256 totalLoss;
}

interface VaultView {
  function name() external view returns (string memory);
  function symbol() external view returns (string memory);

  function token() external view returns (address);

  function strategies(address _strategy) external view returns (StrategyParams memory);


  function pendingGovernance() external view returns (address);
  function governance() external view returns (address);
  function management() external view returns (address);
  function guardian() external view returns (address);

  function rewards() external view returns (address);

  function withdrawalQueue(uint256 index) external view returns (address);
}

interface StratView {
    function name() external view returns (string memory);

    function strategist() external view returns (address);
    function rewards() external view returns (address);
    function keeper() external view returns (address);

}