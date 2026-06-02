require("dotenv").config();
const hre = require("hardhat");

async function main() {
    // ✅ P131 FIXED: .env se contract address
    const contractAddress = process.env.CONTRACT_ADDRESS;

    // ✅ P132 FIXED: .env se oracle address
    const trustedOracleAddress = process.env.ORACLE_NODE_ADDRESS;

    // Validation
    if (!contractAddress) {
        console.error("❌ CONTRACT_ADDRESS not set in .env!");
        process.exit(1);
    }
    if (!trustedOracleAddress) {
        console.error("❌ ORACLE_NODE_ADDRESS not set in .env!");
        process.exit(1);
    }

    console.log("\n" + "=".repeat(55));
    console.log("🔗 ORACLE INITIALIZATION");
    console.log("=".repeat(55));
    console.log(`   Contract: ${contractAddress}`);
    console.log(`   Oracle:   ${trustedOracleAddress}`);

    const EcoCoin = await hre.ethers.getContractFactory("EcoCoin");
    const contract = EcoCoin.attach(contractAddress);

    console.log("\n   Binding Oracle Node on-chain...");
    const tx = await contract.updateOracleNode(trustedOracleAddress);
    await tx.wait();

    console.log("   ✅ Oracle address locked on-chain!");
    console.log("=".repeat(55) + "\n");
}

main().catch((error) => {
    console.error("❌ Error:", error.message);
    process.exitCode = 1;
});