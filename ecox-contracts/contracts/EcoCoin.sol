// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable2Step.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title EcoCoin (ECOX) - Day 17 Automated AI Minting
 * @notice Enterprise-grade token with automated AI-to-Blockchain minting pipeline.
 */
interface IZkVerifier {
    function verifyProof(uint256[2] calldata a, uint256[2][2] calldata b, uint256[2] calldata c, uint256[1] calldata input) external view returns (bool);
}

contract EcoCoin is ERC20, ERC20Burnable, Ownable2Step, ReentrancyGuard {

    struct ZkProof {
        uint256[2] a;
        uint256[2][2] b;
        uint256[2] c;
    }

    error ZeroAddressForbidden();
    error UnauthorizedOracle();
    error DuplicateActionHash();
    error InvalidZeroKnowledgeProof();
    error ExceedsMaxSupplyCeiling();
    error ExceedsMaxPerMintLimit();

    uint256 public constant BURN_TAX_BPS = 100;
    uint256 public constant BPS_DENOMINATOR = 10000;
    uint256 public constant MAX_SUPPLY = 500_000_000 * 10**18;
    uint256 public constant MAX_PER_MINT = 50_000 * 10**18;

    address public aiOracleNode;
    address public zkVerifierAddress;
    
    mapping(address => bool) private _isExemptFromTax;
    mapping(bytes32 => bool) private _processedImageHashes;

    event EcoRewardMinted(address indexed recipient, uint256 amount, bytes32 indexed imageHash);
    event OracleNodeUpdated(address indexed oldOracle, address indexed newOracle);

    constructor(address initialOwner) ERC20("EcoCoin", "ECOX") Ownable(initialOwner) {}

    // --- DAY 17: AUTOMATED AI MINTING ---
    function mintFromAI(address recipient, uint256 amount, bytes32 actionId) external nonReentrant {
        if (msg.sender != aiOracleNode) revert UnauthorizedOracle();
        
        if (recipient == address(0)) revert ZeroAddressForbidden();
        if (amount > MAX_PER_MINT) revert ExceedsMaxPerMintLimit();
        if (totalSupply() + amount > MAX_SUPPLY) revert ExceedsMaxSupplyCeiling();
        if (_processedImageHashes[actionId]) revert DuplicateActionHash();

        _processedImageHashes[actionId] = true;
        _mint(recipient, amount);

        emit EcoRewardMinted(recipient, amount, actionId);
    }

    // --- ZK PROOF MINTING ---
    function mintEcoRewardWithZkProof(
        address recipient, uint256 amount, bytes32 imageHash, ZkProof calldata proof
    ) external nonReentrant {
        if (msg.sender != aiOracleNode) revert UnauthorizedOracle();
        if (recipient == address(0)) revert ZeroAddressForbidden();
        if (amount > MAX_PER_MINT) revert ExceedsMaxPerMintLimit();
        if (totalSupply() + amount > MAX_SUPPLY) revert ExceedsMaxSupplyCeiling();
        if (_processedImageHashes[imageHash]) revert DuplicateActionHash();

        uint256[1] memory publicInput = [uint256(imageHash)];
        bool isProofValid = IZkVerifier(zkVerifierAddress).verifyProof(proof.a, proof.b, proof.c, publicInput);
        if (!isProofValid) revert InvalidZeroKnowledgeProof();

        _processedImageHashes[imageHash] = true;
        _mint(recipient, amount);
        emit EcoRewardMinted(recipient, amount, imageHash);
    }

    // --- ADMIN & UTILS ---
    function updateOracleNode(address newOracle) external onlyOwner {
        if (newOracle == address(0)) revert ZeroAddressForbidden();
        address oldOracle = aiOracleNode;
        aiOracleNode = newOracle;
        _isExemptFromTax[newOracle] = true;
        emit OracleNodeUpdated(oldOracle, newOracle);
    }

    function _update(address from, address to, uint256 value) internal override(ERC20) {
        if (from == address(0) || to == address(0) || _isExemptFromTax[from] || _isExemptFromTax[to]) {
            super._update(from, to, value);
            return;
        }
        uint256 burnAmount = (value * BURN_TAX_BPS) / BPS_DENOMINATOR;
        super._update(from, address(0), burnAmount);
        super._update(from, to, value - burnAmount);
    }
}