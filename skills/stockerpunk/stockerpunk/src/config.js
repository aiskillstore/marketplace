// StockerPunk CLI config. Fill CONTRACTS at launch; everything else is live now.
module.exports = {
  CHAIN_ID: 56,
  CHAIN_NAME: "BNB Chain",
  RPCS: [
    "https://bsc-rpc.publicnode.com",
    "https://binance.llamarpc.com",
    "https://bsc-dataseed.binance.org",
  ],

  // Filled on deploy. While null, read/mint commands report NOT_LIVE.
  CONTRACTS: {
    nft: "0xfD81e3e5853553D43e4BD3D0bCDE98c69E86c98c",     // StockerPunk ERC721 (mint, tokensOfOwner, rarityOf, miningWeight, accountOf)
    vault: "0x50F03C2034942f1C032a466F5dBb3a1fc9477504",   // MiningVault (pendingStock, harvest, lock/boost)
    spunk: "0x5d392B52868077b9Ba5391eeF734820865CD0de6", // $SPUNK token (boost + reward sink)
  },

  TOKENS: {
    agentId: "0x60b9262456de011f7d15a54cdd8c48baaa8b022f", // SPACE ID Agent ID (.ai), BSC
    nvda:    "0x02fca66c1d1afb4e2a7884261eb00f63598a7436", // bStock NVDAB, reward asset
  },

  SUPPLY: 5000,
  PRICE_USD: 1,
  MAX_PER_WALLET: 5,

  RARITY: [ // index = on-chain rarity id
    { id: 0, name: "Retail",     weight: 1.0 },
    { id: 1, name: "Day Trader", weight: 1.6 },
    { id: 2, name: "Broker",     weight: 2.5 },
    { id: 3, name: "Quant",      weight: 4.0 },
    { id: 4, name: "Whale",      weight: 8.0 },
  ],

  // precomputed 4-byte selectors (keccak of the signature)
  SEL: {
    mint:          "0xa0712d68", // mint(uint256)
    harvest:       "0xddc63262", // harvest(uint256)
    totalMinted:   "0xa2309ff8", // totalMinted()
    maxSupply:     "0xd5abeb01", // maxSupply()
    mintPriceWei:  "0xcb2c9722", // mintPriceWei()
    tokensOfOwner: "0x8462151c", // tokensOfOwner(address)
    rarityOf:      "0xdd3b5f9a", // rarityOf(uint256)
    pendingStock:  "0x5d9fd0ea", // pendingStock(uint256)
    miningWeight:  "0xfff0d2a3", // miningWeight(uint256)
    accountOf:     "0x8f4e4321", // accountOf(uint256)
    balanceOf:     "0x70a08231", // balanceOf(address)
    minted:        "0x1e7269c5", // minted(address)
  },
};
