// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract QuantumLock2050V2 {

    error StillLocked(uint256 unlockTime, uint256 currentTime);
    error NotTopHolder();
    error NotEcoCoinContract();
    error AlreadyClaimed();
    error ZeroAddress();
    error TransferFailed();
    error EmergencyPaused();
    error NotOwner();
    error NotMultisig();
    error AlreadyApproved();
    error RotationOverdue();
    error FallbackNotReady();

    uint256 public constant UNLOCK_TIMESTAMP   = 2524608000;
    uint256 public constant ENDOWMENT_RATE_BPS = 100;
    uint256 public constant BPS_DENOMINATOR    = 10000;
    uint256 public constant MULTISIG_THRESHOLD = 2;
    uint256 public constant ROTATION_PERIOD    = 5 * 365 days;
    uint256 public constant FALLBACK_DELAY     = 365 days;

    address public ecoCoinContract;
    address public daoTreasury;
    bool    public emergencyPaused;
    bool    public claimed;

    uint256 public lastSignerRotation;

    mapping(address => bool)    public multisigSigners;
    uint256 public signerCount;

    bytes32 public merkleRoot;
    mapping(bytes32 => uint256) public merkleScores;

    struct PendingAction {
        bytes32  actionType;
        address  newAddress;
        bool     boolValue;
        uint256  approvals;
        bool     executed;
        mapping(address => bool) hasApproved;
    }
    mapping(bytes32 => PendingAction) private _pendingActions;

    mapping(address => uint256) public proofOfPlanetScore;
    address public currentTopHolder;
    uint256 public currentTopScore;
    uint256 public totalAccumulated;

    // Testament — IPFS encrypted notes
    mapping(address => string) public testament;
    event TestamentStored(address indexed user, string ipfsHash);

    event ContributionReceived(address indexed user, uint256 amount, uint256 co2);
    event ProofUpdated(address indexed user, uint256 score, bool isTop);
    event FundUnlocked(address indexed winner, uint256 amount);
    event FallbackTriggered(address indexed dao, uint256 amount);
    event EmergencyPauseSet(bool paused);
    event EcoCoinUpdated(address indexed oldAddr, address indexed newAddr);
    event SignerRotated(address indexed oldSigner, address indexed newSigner);
    event MerkleRootUpdated(bytes32 indexed newRoot);
    event MultisigActionProposed(bytes32 indexed actionId);
    event MultisigActionExecuted(bytes32 indexed actionId);
    event TimeCapsuleMessage(string message);

    modifier onlyEcoCoin() {
        if (msg.sender != ecoCoinContract) revert NotEcoCoinContract();
        _;
    }

    modifier notPaused() {
        if (emergencyPaused) revert EmergencyPaused();
        _;
    }

    modifier onlySigner() {
        if (!multisigSigners[msg.sender]) revert NotMultisig();
        _;
    }

    modifier rotationCheck() {
        if (block.timestamp > lastSignerRotation + ROTATION_PERIOD)
            revert RotationOverdue();
        _;
    }

    constructor(
        address _ecoCoinContract,
        address _daoTreasury,
        address[] memory _signers
    ) {
        if (_ecoCoinContract == address(0)) revert ZeroAddress();
        if (_daoTreasury == address(0))     revert ZeroAddress();

        ecoCoinContract   = _ecoCoinContract;
        daoTreasury       = _daoTreasury;
        lastSignerRotation = block.timestamp;

        for (uint i = 0; i < _signers.length; i++) {
            multisigSigners[_signers[i]] = true;
            signerCount++;
        }

        emit TimeCapsuleMessage(
            "To whoever reads this in 2050: "
            "This fund was created June 3, 2026, "
            "from Hyderabad, Pakistan, "
            "by people who believed the planet was worth saving. "
            "Use this wisely. - EcoX 2026"
        );
    }

    // ─── Core: recordContribution ───
    function recordContribution(
        address user,
        uint256 mintAmount,
        uint256 co2NanoGrams
    ) external onlyEcoCoin notPaused {
        uint256 contribution  = (mintAmount * ENDOWMENT_RATE_BPS) / BPS_DENOMINATOR;
        totalAccumulated     += contribution;

        proofOfPlanetScore[user] += co2NanoGrams;
        uint256 userScore         = proofOfPlanetScore[user];

        if (userScore > currentTopScore) {
            currentTopScore  = userScore;
            currentTopHolder = user;
            emit ProofUpdated(user, userScore, true);
        } else {
            emit ProofUpdated(user, userScore, false);
        }

        emit ContributionReceived(user, contribution, co2NanoGrams);
    }

    // ─── Fix 3: Merkle batch update (gas optimization) ───
    function submitBatchMerkleUpdate(bytes32 newRoot) external onlySigner {
        merkleRoot = newRoot;
        emit MerkleRootUpdated(newRoot);
    }

    // ─── Unlock 2050 ───
    function unlockEndowment() external notPaused {
        if (block.timestamp < UNLOCK_TIMESTAMP)
            revert StillLocked(UNLOCK_TIMESTAMP, block.timestamp);
        if (claimed) revert AlreadyClaimed();
        if (msg.sender != currentTopHolder) revert NotTopHolder();

        claimed = true;
        uint256 balance = IERC20(ecoCoinContract).balanceOf(address(this));
        bool success    = IERC20(ecoCoinContract).transfer(currentTopHolder, balance);
        if (!success) revert TransferFailed();

        emit FundUnlocked(currentTopHolder, balance);
    }

    // ─── Fix 1: Fallback to DAO after 1 year ───
    function claimFallbackToDAO() external notPaused {
        if (block.timestamp < UNLOCK_TIMESTAMP + FALLBACK_DELAY)
            revert FallbackNotReady();
        if (claimed) revert AlreadyClaimed();

        claimed = true;
        uint256 balance = IERC20(ecoCoinContract).balanceOf(address(this));
        bool success    = IERC20(ecoCoinContract).transfer(daoTreasury, balance);
        if (!success) revert TransferFailed();

        emit FallbackTriggered(daoTreasury, balance);
    }

    // ─── Fix 4: Emergency Pause via Multisig ───
    function proposePause(bool pauseState) external onlySigner {
        bytes32 actionId = keccak256(
            abi.encodePacked("pause", pauseState, block.timestamp / 1 days)
        );
        PendingAction storage action = _pendingActions[actionId];
        if (action.actionType == bytes32(0)) {
            action.actionType = "pause";
            action.boolValue  = pauseState;
            emit MultisigActionProposed(actionId);
        }
        if (action.hasApproved[msg.sender]) revert AlreadyApproved();
        action.hasApproved[msg.sender] = true;
        action.approvals++;

        if (action.approvals >= MULTISIG_THRESHOLD && !action.executed) {
            action.executed    = true;
            emergencyPaused    = pauseState;
            emit EmergencyPauseSet(pauseState);
            emit MultisigActionExecuted(actionId);
        }
    }

    // ─── Fix 2: Signer Rotation (every 5 years) ───
    function proposeSignerRotation(
        address oldSigner,
        address newSigner
    ) external onlySigner {
        if (newSigner == address(0)) revert ZeroAddress();

        bytes32 actionId = keccak256(
            abi.encodePacked("rotateSigner", oldSigner, newSigner)
        );
        PendingAction storage action = _pendingActions[actionId];
        if (action.actionType == bytes32(0)) {
            action.actionType = "rotateSigner";
            action.newAddress = newSigner;
            emit MultisigActionProposed(actionId);
        }
        if (action.hasApproved[msg.sender]) revert AlreadyApproved();
        action.hasApproved[msg.sender] = true;
        action.approvals++;

        if (action.approvals >= MULTISIG_THRESHOLD && !action.executed) {
            action.executed = true;
            multisigSigners[oldSigner] = false;
            multisigSigners[newSigner] = true;
            lastSignerRotation         = block.timestamp;
            emit SignerRotated(oldSigner, newSigner);
            emit MultisigActionExecuted(actionId);
        }
    }

    // ─── EcoCoin Update via Multisig ───
    function proposeEcoCoinUpdate(address newAddr) external onlySigner {
        if (newAddr == address(0)) revert ZeroAddress();
        bytes32 actionId = keccak256(abi.encodePacked("updateEcoCoin", newAddr));
        PendingAction storage action = _pendingActions[actionId];
        if (action.actionType == bytes32(0)) {
            action.actionType = "updateEcoCoin";
            action.newAddress = newAddr;
            emit MultisigActionProposed(actionId);
        }
        if (action.hasApproved[msg.sender]) revert AlreadyApproved();
        action.hasApproved[msg.sender] = true;
        action.approvals++;

        if (action.approvals >= MULTISIG_THRESHOLD && !action.executed) {
            action.executed = true;
            address old     = ecoCoinContract;
            ecoCoinContract = newAddr;
            emit EcoCoinUpdated(old, newAddr);
            emit MultisigActionExecuted(actionId);
        }
    }

    // ─── Testament (IPFS encrypted notes) ───
    function storeTestament(string calldata ipfsHash) external {
        testament[msg.sender] = ipfsHash;
        emit TestamentStored(msg.sender, ipfsHash);
    }

    function getTestament(address user) external view returns (string memory) {
        return testament[user];
    }

    // ─── View Functions ───
    function getFundStatus() external view returns (
        bool locked, uint256 secondsRemaining,
        uint256 accumulated, address topHolder,
        uint256 topScore, bool isClaimed, bool paused
    ) {
        locked           = block.timestamp < UNLOCK_TIMESTAMP;
        secondsRemaining = locked ? UNLOCK_TIMESTAMP - block.timestamp : 0;
        accumulated      = totalAccumulated;
        topHolder        = currentTopHolder;
        topScore         = currentTopScore;
        isClaimed        = claimed;
        paused           = emergencyPaused;
    }

    receive() external payable {}
}