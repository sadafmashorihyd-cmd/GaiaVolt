const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

module.exports = buildModule("EcoXModule", (m) => {
    // ✅ Owner = Oracle address
    const deployer = m.getAccount(0);

    const ecoCoin = m.contract("EcoCoin", [deployer]);
a
    return { ecoCoin };
});