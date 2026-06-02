const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

module.exports = buildModule("EcoCoinModule", (m) => {
    const ecoCoin = m.contract("EcoCoin", ["0xcaFB99c260635184a6336E4B48982976cdFB960E"]);
    return { ecoCoin };
});