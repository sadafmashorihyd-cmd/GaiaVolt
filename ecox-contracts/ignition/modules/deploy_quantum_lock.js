const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

const ECOX = "0xc26A215ada91C7A51001a2c11B5348D532B28c93";
const WALLET = "0xcaFB99c260635184a6336E4B48982976cdFB960E";
const DAO = "0xcaFB99c260635184a6336E4B48982976cdFB960E"; // DAO = wallet for now

module.exports = buildModule("QuantumLock2050V2Module", (m) => {
    const quantumLock = m.contract("QuantumLock2050V2", [
        ECOX, DAO, [WALLET]
    ]);
    return { quantumLock };
});