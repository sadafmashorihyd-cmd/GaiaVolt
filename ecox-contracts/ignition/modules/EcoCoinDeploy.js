const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

module.exports = buildModule("EcoCoinModule", (m) => {
    // Yahan "EcoCoin" wo naam hai jo aapke contract ke andar likha hai
    const ecoCoin = m.contract("EcoCoin", ["0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"]);
    return { ecoCoin };
});