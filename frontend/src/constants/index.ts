// Contract addresses
export const CONTRACTS = {
    ECOX: "0xc26A215ada91C7A51001a2c11B5348D532B28c93",
    QUANTUM_LOCK: "0xc0d5a8E04706674b5aA2e366122Ae8d54C56c7c1",
    PAYMASTER: "0xBC8dc092c43D6795A27Cc4DbF1Abb6C55BFE5477",
}

// Recent carbon actions for globe
export const CARBON_ACTIONS = [
    { id: 1, city: "Hyderabad", lat: 17.385, lon: 78.487, type: "solar_panels", co2: 2.5, conf: 99.95 },
    { id: 2, city: "Karachi", lat: 24.860, lon: 67.001, type: "cycling", co2: 0.8, conf: 97.2 },
    { id: 3, city: "Lahore", lat: 31.549, lon: 74.343, type: "solar_panels", co2: 2.5, conf: 98.1 },
    { id: 4, city: "Mumbai", lat: 19.076, lon: 72.877, type: "cycling", co2: 0.8, conf: 96.4 },
    { id: 5, city: "Delhi", lat: 28.613, lon: 77.209, type: "utility_bills", co2: 1.2, conf: 94.8 },
    { id: 6, city: "Islamabad", lat: 33.720, lon: 73.060, type: "plantation", co2: 5.0, conf: 99.1 },
]

// Chain config
export const CHAIN = {
    ID: 80002,
    NAME: "Polygon Amoy",
    RPC: "https://rpc-amoy.polygon.technology",
}