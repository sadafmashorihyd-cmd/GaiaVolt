const hre = require("hardhat");

async function main() {
    const contractAddress = "0x5FbDB2315678afecb367f032d93F642f64180aa3";
    const trustedOracleAddress = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266";

    const EcoCoin = await hre.ethers.getContractFactory("EcoCoin");
    const contract = EcoCoin.attach(contractAddress);

    console.log("🔗 Binding authorized Oracle Node address on-chain...");
    const tx = await contract.updateOracleNode(trustedOracleAddress);
    await tx.wait();
    console.log("✅ Success! Oracle address locked on-chain.");
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});