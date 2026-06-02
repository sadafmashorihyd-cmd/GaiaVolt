const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

const ENTRY_POINT = "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789";
const ECOX_CONTRACT = "0xc26A215ada91C7A51001a2c11B5348D532B28c93";

module.exports = buildModule("EcoXPaymasterModule", (m) => {
    const paymaster = m.contract("EcoXPaymaster", [ENTRY_POINT, ECOX_CONTRACT]);
    return { paymaster };
});