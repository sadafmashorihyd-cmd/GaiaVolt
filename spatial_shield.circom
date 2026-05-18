pragma circom 2.0.6; // Version updated for strict constraints

include "node_modules/circomlib/circuits/poseidon.circom";
include "node_modules/circomlib/circuits/comparators.circom";

template SpatialGuard() {
    // --- 1. INPUT SIGNALS ---
    signal input user_lat;
    signal input user_lon;
    signal input user_trust;

    signal input min_lat;
    signal input max_lat;
    signal input min_lon;
    signal input max_lon;
    
    signal input allowed_region_hash;
    signal input min_trust;

    // --- 2. OUTPUT SIGNAL ---
    signal output is_valid_user;

    // --- 3. CRYPTOGRAPHIC VERIFICATION ---
    component hasher = Poseidon(4);
    hasher.inputs[0] <== min_lat;
    hasher.inputs[1] <== max_lat;
    hasher.inputs[2] <== min_lon;
    hasher.inputs[3] <== max_lon;

    allowed_region_hash === hasher.out;

    // --- 4. OPTIMIZED BOUNDARY CHECKS (252-bit) ---
    component gteLat = GreaterEqThan(252);
    gteLat.in[0] <== user_lat;
    gteLat.in[1] <== min_lat;

    component lteLat = LessEqThan(252);
    lteLat.in[0] <== user_lat;
    lteLat.in[1] <== max_lat;

    component gteLon = GreaterEqThan(252);
    gteLon.in[0] <== user_lon;
    gteLon.in[1] <== min_lon;

    component lteLon = LessEqThan(252);
    lteLon.in[0] <== user_lon;
    lteLon.in[1] <== max_lon;

    component gteTrust = GreaterEqThan(252);
    gteTrust.in[0] <== user_trust;
    gteTrust.in[1] <== min_trust;

    // --- 5. CLEAN CONSTRAINTS ---
    signal lat_ok;
    signal lon_ok;
    signal spatial_ok;
    
    lat_ok <== gteLat.out * lteLat.out;
    lon_ok <== gteLon.out * lteLon.out;
    spatial_ok <== lat_ok * lon_ok;

    is_valid_user <== spatial_ok * gteTrust.out;
    
    // THE ULTIMATE ABSOLUTE SECURITY LOCK:
    is_valid_user === 1; 
}

component main {public [allowed_region_hash, min_trust]} = SpatialGuard();