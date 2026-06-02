require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config({ path: "../.env" });

const ORACLE_PRIVATE_KEY = process.env.ORACLE_PRIVATE_KEY || "0x" + "0".repeat(64);
const RPC_URL = process.env.RPC_URL || "https://rpc-amoy.polygon.technology";
const POLYGONSCAN_KEY = process.env.POLYGONSCAN_KEY || "";

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
    solidity: {
        version: "0.8.20",
        settings: {
            // ✅ Optimizer — gas fees kam!
            optimizer: {
                enabled: true,
                runs: 200
            }
        }
    },

    networks: {
        // ✅ Local Hardhat
        hardhat: {
            chainId: 31337
        },

        // ✅ Polygon Amoy Testnet
        amoy: {
            url: RPC_URL,
            accounts: [ORACLE_PRIVATE_KEY],
            chainId: 80002,
            gasPrice: "auto"
        },

        // ✅ Polygon Mainnet (Day 34)
        polygon: {
            url: "https://polygon-rpc.com",
            accounts: [ORACLE_PRIVATE_KEY],
            chainId: 137,
            gasPrice: "auto"
        }
    },

    // ✅ Polygonscan verify
    etherscan: {
        apiKey: {
            polygonAmoy: POLYGONSCAN_KEY,
            polygon: POLYGONSCAN_KEY
        },
        customChains: [
            {
                network: "polygonAmoy",
                chainId: 80002,
                urls: {
                    apiURL: "https://api-amoy.polygonscan.com/api",
                    browserURL: "https://amoy.polygonscan.com"
                }
            }
        ]
    },

    // ✅ Gas reporter
    gasReporter: {
        enabled: true,
        currency: "USD"
    }
};