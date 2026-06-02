const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

const ECOX_CONTRACT = "0x9B85faC077fE830ee9A513ca32835b9901638166";

module.exports = buildModule("QuantumLock2050Module", (m) => {
    const quantumLock = m.contract("QuantumLock2050", [ECOX_CONTRACT]);
    return { quantumLock };
});