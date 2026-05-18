// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable2Step.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title Real ZK-Verifier Interface
 * @notice Yeh interface hamare main contract ko real ZK-SNARK verifier contract se jorta hai.
 */
interface IZkVerifier {
    function verifyProof(
        uint256[2] calldata a,
        uint256[2][2] calldata b,
        uint256[2] calldata c,
        uint256[1] calldata input // ZK public inputs ke liye
    ) external view returns (bool);
}

/**
 * @title EcoCoin (ECOX) - Production Ready
 * @author Sadaf (Scientist-Founder) & Gemini AI
 * @notice Enterprise-grade deflationary ERC20 token with real ZK-Proof validation and hard supply caps.
 */
contract EcoCoin is ERC20, ERC20Burnable, Ownable2Step, ReentrancyGuard {

    // --- STRUCTS ---
    struct ZkProof {
        uint256[2] a;
        uint256[2][2] b;
        uint256[2] c;
    }

    // --- CUSTOM ERRORS (Gas Optimized) ---
    error ZeroAddressForbidden();
    error UnauthorizedOracle();
    error DuplicateActionHash();
    error InvalidZeroKnowledgeProof();
    error ExceedsMaxSupplyCeiling();
    error ExceedsMaxPerMintLimit();

    // --- CONSTANTS (Real-World Safety Controls) ---
    uint256 public constant BURN_TAX_BPS = 100; // 1%
    uint256 public constant BPS_DENOMINATOR = 10000;
    
    // Safety Caps (Token economics safety)
    uint256 public constant MAX_SUPPLY = 500_000_000 * 10**18; // 500 Million Max Supply
    uint256 public constant MAX_PER_MINT = 50_000 * 10**18;    // Max 50k tokens per validation

    // --- STATE VARIABLES ---
    address public aiOracleNode;
    address public zkVerifierAddress; // Real ZK Verifier Contract Address
    
    mapping(address => bool) private _isExemptFromTax;
    mapping(bytes32 => bool) private _processedImageHashes;

    // --- EVENTS ---
    event TaxExemptionStatusUpdated(address indexed account, bool isExempt);
    event DeflationaryBurnExecuted(address indexed sender, address indexed recipient, uint256 burnAmount);
    event OracleNodeUpdated(address indexed oldOracle, address indexed newOracle);
    event ZkVerifierUpdated(address indexed oldVerifier, address indexed newVerifier);
    event EcoRewardMinted(address indexed recipient, uint256 amount, bytes32 indexed imageHash);
    event ZkProofVerified(bytes32 indexed actionHash, bool success);

    // --- MODIFIERS ---
    modifier onlyOracle() {
        if (msg.sender != aiOracleNode) revert UnauthorizedOracle();
        _;
    }

    constructor(address initialOwner) 
        ERC20("EcoCoin", "ECOX") 
        Ownable(initialOwner) 
    {}

    // --- EXTERNAL/PUBLIC FUNCTIONS ---

    function setTaxExemption(address account, bool isExempt) external onlyOwner {
        if (account == address(0)) revert ZeroAddressForbidden();
        _isExemptFromTax[account] = isExempt;
        emit TaxExemptionStatusUpdated(account, isExempt);
    }

    function isExemptFromTax(address account) external view returns (bool) {
        return _isExemptFromTax[account];
    }

    /**
     * @notice Updates the trusted AI Oracle Node interface address.
     */
    function updateOracleNode(address newOracle) external onlyOwner {
        if (newOracle == address(0)) revert ZeroAddressForbidden();
        address oldOracle = aiOracleNode;
        aiOracleNode = newOracle;
        _isExemptFromTax[newOracle] = true; // Auto-exempt Oracle
        emit OracleNodeUpdated(oldOracle, newOracle);
    }

    /**
     * @notice Sets or updates the real cryptographic ZK Verifier contract address.
     */
    function updateZkVerifier(address newVerifier) external onlyOwner {
        if (newVerifier == address(0)) revert ZeroAddressForbidden();
        address oldVerifier = zkVerifierAddress;
        zkVerifierAddress = newVerifier;
        emit ZkVerifierUpdated(oldVerifier, newVerifier);
    }

    /**
     * @notice Standard AI Minting with basic security controls.
     */
    function mintEcoReward(
        address recipient, 
        uint256 amount, 
        bytes32 imageHash
    ) external onlyOracle nonReentrant {
        if (recipient == address(0)) revert ZeroAddressForbidden();
        if (amount > MAX_PER_MINT) revert ExceedsMaxPerMintLimit();
        if (totalSupply() + amount > MAX_SUPPLY) revert ExceedsMaxSupplyCeiling();
        if (_processedImageHashes[imageHash]) revert DuplicateActionHash();

        _processedImageHashes[imageHash] = true;
        _mint(recipient, amount);

        emit EcoRewardMinted(recipient, amount, imageHash);
    }

    /**
     * @notice Real-World Enterprise Upgrade: Mints rewards using REAL ZK-SNARK verification contract.
     */
    function mintEcoRewardWithZkProof(
        address recipient,
        uint256 amount,
        bytes32 imageHash,
        ZkProof calldata proof
    ) external onlyOracle nonReentrant {
        if (recipient == address(0)) revert ZeroAddressForbidden();
        if (amount > MAX_PER_MINT) revert ExceedsMaxPerMintLimit();
        if (totalSupply() + amount > MAX_SUPPLY) revert ExceedsMaxSupplyCeiling();
        if (_processedImageHashes[imageHash]) revert DuplicateActionHash();
        if (zkVerifierAddress == address(0)) revert InvalidZeroKnowledgeProof(); // Verifier set hona zaroori hai

        // --- REAL CRYPTOGRAPHIC ZK-SNARK BRIDGE ---
        // ImageHash ko ba-taur public input convert kar ke verifier ko bhejte hain
        uint256[1] memory publicInput = [uint256(imageHash)];
        
        bool isProofValid = IZkVerifier(zkVerifierAddress).verifyProof(
            proof.a, 
            proof.b, 
            proof.c, 
            publicInput
        );
        
        if (!isProofValid) revert InvalidZeroKnowledgeProof();

        emit ZkProofVerified(imageHash, true);

        // State changes & Execution
        _processedImageHashes[imageHash] = true;
        _mint(recipient, amount);

        emit EcoRewardMinted(recipient, amount, imageHash);
    }

    function isImageHashProcessed(bytes32 imageHash) external view returns (bool) {
        return _processedImageHashes[imageHash];
    }

    // --- INTERNAL OVERRIDES (Fixed Tax Logic) ---

    function _update(
        address from,
        address to,
        uint256 value
    ) internal override(ERC20) {
        // Minting aur Burning par koi tax nahi hoga
        if (from == address(0) || to == address(0)) {
            super._update(from, to, value);
            return;
        }

        // Agar koi ek party bhi whitelist (exempt) hai toh tax skip hoga
        bool isExempt = _isExemptFromTax[from] || _isExemptFromTax[to];

        if (isExempt) {
            super._update(from, to, value);
        } else {
            uint256 burnAmount = (value * BURN_TAX_BPS) / BPS_DENOMINATOR;
            uint256 tokensToTransfer = value - burnAmount;

            if (burnAmount > 0) {
                super._update(from, address(0), burnAmount);
                emit DeflationaryBurnExecuted(from, to, burnAmount);
            }

            super._update(from, to, tokensToTransfer);
        }
    }
}