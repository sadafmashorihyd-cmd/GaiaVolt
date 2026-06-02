// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract QuantumLock2050 {

    error StillLocked(uint256 unlockTime, uint256 currentTime);
    error NotTopHolder();
    error NotEcoCoinContract();
    error AlreadyClaimed();
    error ZeroAddress();
    error TransferFailed();

    uint256 public constant UNLOCK_TIMESTAMP    = 2524608000;
    uint256 public constant ENDOWMENT_RATE_BPS  = 100;
    uint256 public constant BPS_DENOMINATOR     = 10000;

    address public immutable ecoCoinContract;
    address public owner;
    bool    public claimed;

    mapping(address => uint256) public proofOfPlanetScore;
    address public currentTopHolder;
    uint256 public currentTopScore;
    uint256 public totalAccumulated;

    event EndowmentReceived(address indexed from, uint256 amount, uint256 totalAccumulated);
    event ProofOfPlanetUpdated(address indexed user, uint256 newScore, bool isNewTopHolder);
    event FundUnlocked(address indexed winner, uint256 amount, uint256 unlockedAt);
    event TimeCapsuleMessage(string message);

    constructor(address _ecoCoinContract) {
        if (_ecoCoinContract == address(0)) revert ZeroAddress();
        ecoCoinContract = _ecoCoinContract;
        owner           = msg.sender;
        emit TimeCapsuleMessage(
            "To whoever reads this in 2050: This fund was created on May 31, 2026, "
            "by people who believed the planet was worth saving. "
            "Every fraction of ECOX here represents a real action. "
            "Use this wisely. - EcoX, 2026"
        );
    }

    modifier onlyEcoCoin() {
        if (msg.sender != ecoCoinContract) revert NotEcoCoinContract();
        _;
    }

    function recordContribution(
        address user,
        uint256 mintAmount,
        uint256 co2NanoGrams
    ) external onlyEcoCoin {
        uint256 contribution  = (mintAmount * ENDOWMENT_RATE_BPS) / BPS_DENOMINATOR;
        totalAccumulated     += contribution;

        proofOfPlanetScore[user] += co2NanoGrams;
        uint256 userScore         = proofOfPlanetScore[user];

        bool isNewTop = false;
        if (userScore > currentTopScore) {
            currentTopScore  = userScore;
            currentTopHolder = user;
            isNewTop         = true;
        }

        emit EndowmentReceived(user, contribution, totalAccumulated);
        emit ProofOfPlanetUpdated(user, userScore, isNewTop);
    }

    function unlockEndowment() external {
        if (block.timestamp < UNLOCK_TIMESTAMP)
            revert StillLocked(UNLOCK_TIMESTAMP, block.timestamp);
        if (claimed) revert AlreadyClaimed();
        if (msg.sender != currentTopHolder) revert NotTopHolder();

        claimed = true;
        uint256 balance = IERC20(ecoCoinContract).balanceOf(address(this));
        bool success    = IERC20(ecoCoinContract).transfer(currentTopHolder, balance);
        if (!success) revert TransferFailed();

        emit FundUnlocked(currentTopHolder, balance, block.timestamp);
    }

    function getTimeRemaining() external view returns (uint256) {
        if (block.timestamp >= UNLOCK_TIMESTAMP) return 0;
        return UNLOCK_TIMESTAMP - block.timestamp;
    }

    function getUnlockDate() external pure returns (string memory) {
        return "January 1, 2050 00:00:00 UTC";
    }

    function getTopHolder() external view returns (address, uint256) {
        return (currentTopHolder, currentTopScore);
    }

    function isLocked() external view returns (bool) {
        return block.timestamp < UNLOCK_TIMESTAMP;
    }

    function getFundStatus() external view returns (
        bool locked, uint256 secondsRemaining,
        uint256 accumulated, address topHolder,
        uint256 topScore, bool isClaimed
    ) {
        locked           = block.timestamp < UNLOCK_TIMESTAMP;
        secondsRemaining = locked ? UNLOCK_TIMESTAMP - block.timestamp : 0;
        accumulated      = totalAccumulated;
        topHolder        = currentTopHolder;
        topScore         = currentTopScore;
        isClaimed        = claimed;
    }

    receive() external payable {}
}