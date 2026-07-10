# Alkahest Contract Reference

## Escrow Obligation Types

Each escrow locks assets in a contract until an arbiter validates fulfillment.

| Type | Contract | ObligationData fields |
|------|----------|----------------------|
| ERC20 | `ERC20EscrowObligation` | `token: address`, `amount: uint256`, `arbiter: address`, `demand: bytes` |
| ERC721 | `ERC721EscrowObligation` | `token: address`, `tokenId: uint256`, `arbiter: address`, `demand: bytes` |
| ERC1155 | `ERC1155EscrowObligation` | `token: address`, `tokenId: uint256`, `amount: uint256`, `arbiter: address`, `demand: bytes` |
| Native Token | `NativeTokenEscrowObligation` | `amount: uint256`, `arbiter: address`, `demand: bytes` |
| Token Bundle | `TokenBundleEscrowObligation` | `nativeAmount: uint256`, `erc20Tokens: address[]`, `erc20Amounts: uint256[]`, `erc721Tokens: address[]`, `erc721TokenIds: uint256[]`, `erc1155Tokens: address[]`, `erc1155TokenIds: uint256[]`, `erc1155Amounts: uint256[]`, `arbiter: address`, `demand: bytes` |
| Attestation | `AttestationEscrowObligation` | `attestation: AttestationRequest`, `arbiter: address`, `demand: bytes` |
| Attestation Reference | `AttestationReferenceEscrowObligation` | `referencedAttestationUid: bytes32`, `arbiter: address`, `demand: bytes`, `expirationTime: uint64` |

### Escrow lifecycle

1. `doObligation(data, expirationTime)` — lock assets, create EAS attestation
2. Fulfiller creates fulfillment attestation with `refUID` pointing to escrow
3. `collect(escrowUid, fulfillmentUid)` — arbiter validates, releases assets
4. `reclaim(uid)` — reclaim assets after expiration (buyer only)

## Payment Obligation Types

Payments transfer assets immediately upon attestation creation (no escrow hold).

| Type | Contract | ObligationData fields |
|------|----------|----------------------|
| ERC20 | `ERC20PaymentObligation` | `token: address`, `amount: uint256`, `payee: address` |
| ERC721 | `ERC721PaymentObligation` | `token: address`, `tokenId: uint256`, `payee: address` |
| ERC1155 | `ERC1155PaymentObligation` | `token: address`, `tokenId: uint256`, `amount: uint256`, `payee: address` |
| Native Token | `NativeTokenPaymentObligation` | `amount: uint256`, `payee: address` |
| Token Bundle | `TokenBundlePaymentObligation` | `nativeAmount: uint256`, `erc20Tokens: address[]`, `erc20Amounts: uint256[]`, `erc721Tokens: address[]`, `erc721TokenIds: uint256[]`, `erc1155Tokens: address[]`, `erc1155TokenIds: uint256[]`, `erc1155Amounts: uint256[]`, `payee: address` |

## Fulfillment Obligation Types

| Type | Contract | ObligationData fields |
|------|----------|----------------------|
| String | `StringObligation` | `item: string`, `schema: bytes32` |
| Commit-Reveal | `CommitRevealObligation` | `payload: bytes`, `salt: bytes32`, `schema: bytes32` |

### CommitRevealObligation details

- `commit(commitment, commitDeadline)` — submit hash commitment with ETH bond
- `doObligation(data, refUID)` — reveal fulfillment data and reclaim the matching bond
- `computeCommitment(refUID, claimer, data)` — compute expected commitment hash
- `slashBond(commitment)` — slash bond if reveal deadline passes
- Commitment hash: `keccak256(abi.encode(refUID, claimer, keccak256(abi.encode(obligationData))))`
- Built-in `IArbiter` implementation verifies commitment exists in an earlier block and matches the encoded demand's `bondAmount` and `commitDeadline`

## Atomic Utilities

Atomic utilities combine payment + escrow collection into single-transaction settlements.

| Contract | Supported swaps |
|----------|----------------|
| `AtomicPaymentUtils` | Atomic pay-and-collect helpers for ERC20, ERC721, ERC1155, native token, and token bundle payment obligations (with ERC20 permit support) |

## Contract Addresses

### Base Sepolia

| Contract | Address |
|----------|---------|
| **Core** | |
| EAS | `0x4200000000000000000000000000000000000021` |
| EAS Schema Registry | `0x4200000000000000000000000000000000000020` |
| **ERC20** | |
| ERC20EscrowObligation | `0x5c55EFa334A7FceF530a081D19Be98E871EdbB83` |
| UnconditionalERC20EscrowObligation | `0x56AcF1b3A736C5524b8836534D15445322a50a2B` |
| ERC20PaymentObligation | `0x0f953267E8d835b9f33b361C963F126775316dcA` |
| ERC20AtomicPaymentUtils | `0x4c597Ee412A4414e80Ddb79Fde1Fb704bc1358c0` |
| **ERC721** | |
| ERC721EscrowObligation | `0x0850d8F7015Ba183227925cd100968e82aCb266A` |
| UnconditionalERC721EscrowObligation | `0x63A26965Ea23A61219128a57392f8a2A4E7be140` |
| ERC721PaymentObligation | `0x2e8aa787750853ce422E487dacad385296F81169` |
| ERC721AtomicPaymentUtils | `0x4c597Ee412A4414e80Ddb79Fde1Fb704bc1358c0` |
| **ERC1155** | |
| ERC1155EscrowObligation | `0x267C98D752C6B9F9B354471A08F72aaCb9eC8567` |
| UnconditionalERC1155EscrowObligation | `0x62c1351503Ef1308FfF550cD594c95F3112F61aB` |
| ERC1155PaymentObligation | `0x1F559CE3f65374593ff39EC5a74ea36db0b817d1` |
| ERC1155AtomicPaymentUtils | `0x4c597Ee412A4414e80Ddb79Fde1Fb704bc1358c0` |
| **Native Token** | |
| NativeTokenEscrowObligation | `0x5d83C1Cb608e891F7B2Bcc12294d1e64aBB8eC7F` |
| UnconditionalNativeTokenEscrowObligation | `0x58368eE14F75FA38366E7da12707Ec501e3F042a` |
| NativeTokenPaymentObligation | `0xd53357af507f4c865A6345a05dC9849BB3eFD7c7` |
| NativeTokenAtomicPaymentUtils | `0x4c597Ee412A4414e80Ddb79Fde1Fb704bc1358c0` |
| **Token Bundle** | |
| TokenBundleEscrowObligation | `0xC52c611c0C9A11fF625B93f9D1fb9E74C45d9859` |
| UnconditionalTokenBundleEscrowObligation | `0xa5ba8B7382093525F5F6739cCff910376D63c1ba` |
| TokenBundlePaymentObligation | `0x7F445E83779Df77cAB8E71eC3C5E2Bffe4EB1314` |
| TokenBundleAtomicPaymentUtils | `0x4c597Ee412A4414e80Ddb79Fde1Fb704bc1358c0` |
| **Attestation** | |
| AttestationEscrowObligation | `0xFa299C13D7F17B6a3E63b1bE985F93020Db1169C` |
| UnconditionalAttestationEscrowObligation | `0x61504DB9850e54fEb9f0681631BE8906a75B3bB9` |
| AttestationReferenceEscrowObligation | `0x18a38eE1e1609e21b29F9bec07Ea6633BB5E8368` |
| UnconditionalAttestationReferenceEscrowObligation | `0x7833cD2ADD07CD7bD0DA20020663D6857fDa1E6C` |
| AtomicAttestationUtils | `0x886f7cE4bF11dBDbA163bEE866533965177ae680` |
| **Fulfillment** | |
| StringObligation | `0x22d3203992CCC7Dfb2Ec12D87E15b0d8698De35b` |
| CommitRevealObligation | `0x14d0B7D4ed6915CE0b1a0d54F9D5912584dB550E` |
| **Arbiters** | |
| TrivialArbiter | `0xa42Df9aDF17f26Ff1eD5206cf83E5dab88bD3523` |
| TrustedOracleArbiter | `0x504f496F696c41558070a933c90a98604c3f4475` |
| AllArbiter | `0x9F78AAca04A2c005618c3B214e609B13Bbe66356` |
| AnyArbiter | `0xaF67e09D889e0df9d404059283A1FA7BA7Ac7d88` |
| IntrinsicsArbiter | `0xd78d4404E2E1a9033eEf1ac69BF488f6a4Ea9aC0` |
| ERC8004Arbiter | `0x65dE059a0B2A060E842B8106B1BE365bf5f2F80f` |
| ReferencesEscrowArbiter | `0x335441cc9813558067e5b3a4c39AF8a9cFb6fAF8` |
| ExclusiveRevocableConfirmationArbiter | `0xf6388A7b78c4A130249160CbcC609530D267B59B` |
| ExclusiveUnrevocableConfirmationArbiter | `0x21F1402b4006B4A799502F948cfED187E66e9bb9` |
| NonexclusiveRevocableConfirmationArbiter | `0xC4876Bf97a5C24E26e8286fF7a3391c20A8a0A6e` |
| NonexclusiveUnrevocableConfirmationArbiter | `0x9F8AF67d89B674513eFAdf29ed936c4704A64fEb` |
| RecipientArbiter | `0x507CFD91DD2d2b8E7F93812414d8Ce9dC5404F62` |
| AttesterArbiter | `0xa50365B53232f54cf6C60f0f432ad64169A6e76e` |
| SchemaArbiter | `0xA8f8e66d12b97EbE93C79b36D015666DEC2Dd151` |
| UidArbiter | `0x9F06F7E040d57e21964cCa4D91CBC57b25C55D67` |
| RefUidArbiter | `0xafA3c1593ca451DA36dB7fD36077BcFFf7B4c717` |
| RevocableArbiter | `0x6a9e076cf1Df39D029A7B6d48A1Ab36B3cC28639` |
| TimeAfterArbiter | `0x24D729f6f8Fc3DF5EB42939276cF2Efe9fF963d6` |
| TimeBeforeArbiter | `0xCE156DEAB9B4A525640a0BC2Ad9966d13f9a134a` |
| TimeEqualArbiter | `0x5dc2d28f06DDB3e60b76fab033F672126572c976` |
| ExpirationTimeAfterArbiter | `0xd8C0Ab60B431061a079C8b4e0BaCf7CbF6aEA29d` |
| ExpirationTimeBeforeArbiter | `0xcae48f46d89cd2d78118a84d8CA589Ee7d29C98c` |
| ExpirationTimeEqualArbiter | `0x9354ca2BdB314BB41C78CBff4C4443718a8813DF` |
| **Hook-Based** | |
| HookEscrowObligation | `0x5aD1B5f0eE7A520311B4b8d8f758d48934851981` |
| HooksEscrowObligation | `0xa21a3A6db8b00303D7e919Ea8983CFd2DC6Ed1d3` |
| ERC20EscrowHook | `0xEF0473fE3777b45C68455f90d4edCC1A8673c518` |
| ERC721EscrowHook | `0x80016D907E87989457C0253D42e0a4348476DBb3` |
| ERC1155EscrowHook | `0xC2045eF34C8789dE4744272706a8800A03cE1f11` |
| NativeTokenEscrowHook | `0xFeE4003D97e77251091D9C686ba4da4E46D98c05` |
| AttestationEscrowHook | `0x2fd54cC36e441B2a3c0202B621208db046C18ea3` |
| AttestationReferenceEscrowHook | `0x335cE1C9DFA441C2db31914502E5CeD9b38DCBFD` |
| **Splitters** | |
| ERC20Splitter | `0xd6816aC123844edb88f0AF146Cc565C6663DE97B` |
| ERC1155Splitter | `0xB386B657F66c8eAb3A3335d590Eef4a0871e63a3` |
| NativeTokenSplitter | `0xa32161d10B31f3eB5BfC0EEfDE64784e01CBD9E1` |
| TokenBundleSplitter | `0xceC0D468b29cA55FEA224e2b66AC5694036aA24d` |
| TokenBundleSplitterUnvalidated | `0x6c1c55E13E5Ec8668dad15dbe1B461E7814643a1` |

### Sepolia

| Contract | Address |
|----------|---------|
| **Core** | |
| EAS | `0xC2679fBD37d54388Ce493F1DB75320D236e1815e` |
| EAS Schema Registry | `0x0a7E2Ff54e76B8E6659aedc9103FB21c038050D0` |
| **ERC20** | |
| ERC20EscrowObligation | `0x6bcec91a89A63D50368BCe54Cb9eD0399992C18b` |
| UnconditionalERC20EscrowObligation | `0x33F6f558c1FCac597F2b635bc50554055FF98165` |
| ERC20PaymentObligation | `0x99F5335B95e1C0bE4C218a59aae26Efc50d5673f` |
| ERC20AtomicPaymentUtils | `0xD59c6c6Cb025E76a0a1E706c62A9dF38b04694E2` |
| **ERC721** | |
| ERC721EscrowObligation | `0x5B6Bff4DC108C58b97721330666f56c8028C097c` |
| UnconditionalERC721EscrowObligation | `0xF9Dbc74553FaeCAC775201113198085c4D572805` |
| ERC721PaymentObligation | `0x4CB076aF47F0F3909Ebafd88cBc0c4CC8Dee17DD` |
| ERC721AtomicPaymentUtils | `0xD59c6c6Cb025E76a0a1E706c62A9dF38b04694E2` |
| **ERC1155** | |
| ERC1155EscrowObligation | `0x902ac1997bd29A037263E0d80952C80d69D9aFd4` |
| UnconditionalERC1155EscrowObligation | `0xc1b02eFEc19a171ECBB7C8ad54B9617E80fdF40F` |
| ERC1155PaymentObligation | `0xfca2C2DF4023A0A418BF354B5Bfff1EbFe0520A9` |
| ERC1155AtomicPaymentUtils | `0xD59c6c6Cb025E76a0a1E706c62A9dF38b04694E2` |
| **Native Token** | |
| NativeTokenEscrowObligation | `0x797a737deFB8cAE0a30324ecFa52eaab9c0A5fD6` |
| UnconditionalNativeTokenEscrowObligation | `0x850D8Df3fF0149Bd5a9191A958B287B25564716B` |
| NativeTokenPaymentObligation | `0x3c07027874650794EaE300C603f066af182EA86A` |
| NativeTokenAtomicPaymentUtils | `0xD59c6c6Cb025E76a0a1E706c62A9dF38b04694E2` |
| **Token Bundle** | |
| TokenBundleEscrowObligation | `0x7490102a8B821C70679508426823F26C9bab4714` |
| UnconditionalTokenBundleEscrowObligation | `0xD511278D5b9e5F8F9B99d01Ea326B8232C133be5` |
| TokenBundlePaymentObligation | `0xb5800e34602154cE92C5eb0e7Cb455306d7d590E` |
| TokenBundleAtomicPaymentUtils | `0xD59c6c6Cb025E76a0a1E706c62A9dF38b04694E2` |
| **Attestation** | |
| AttestationEscrowObligation | `0xa22b4D9Fe7a746D44BE1e724BB1a26593BCa2C1B` |
| UnconditionalAttestationEscrowObligation | `0xcda1e1EA425E31a789fefFC8e3d90f839fF49C9F` |
| AttestationReferenceEscrowObligation | `0xD57f20673091fB43D55eABf48b4F421DAe70A7C2` |
| UnconditionalAttestationReferenceEscrowObligation | `0xb47c24E94E852521b21D384981F4CEfD1AB9680C` |
| AtomicAttestationUtils | `0xE800A6E43615C5ba54c2851633f4F92548052cd2` |
| **Fulfillment** | |
| StringObligation | `0x66c3f78258823B9B899aB14B11e1DCf978c060D7` |
| CommitRevealObligation | `0x931b35F81e7A585317f8cF8B45795F403EEfe468` |
| **Arbiters** | |
| TrivialArbiter | `0xD56bD862e7BEbD0BD7356603e9E52B32c241E2AE` |
| TrustedOracleArbiter | `0x61dC9c2D757A1C9D0d38A281288d9ef918e77Baa` |
| AllArbiter | `0xb6890A8Cb8CDeFcE11Edc0314125b750F48BFF1B` |
| AnyArbiter | `0x81dC8f2C5677b02aFcAFef34Fa7E75D55dfAEF20` |
| IntrinsicsArbiter | `0x7B20A4b25af2a2637C240622d6C3875DeA609A64` |
| ERC8004Arbiter | `0x194C3Da79a1De5f9141b1DbCdF98eC5d511B4E5a` |
| ReferencesEscrowArbiter | `0x49026902790A8ECb427f335cA0d097c7C5795d13` |
| ExclusiveRevocableConfirmationArbiter | `0xa740634E718c8727853D1E69963303D5cB8Ea44C` |
| ExclusiveUnrevocableConfirmationArbiter | `0xB3D71c6f96cdD41e56dd9870b232225C379f2890` |
| NonexclusiveRevocableConfirmationArbiter | `0x831B40aE79D391C7d56209802b9745Fe0743DBF5` |
| NonexclusiveUnrevocableConfirmationArbiter | `0xFeaA2fa295d1453BA382b7eE0e3F66c489A6d9Bb` |
| RecipientArbiter | `0xE0d55949E6e1590F26eF37a1D01df52Fbb1b2FcE` |
| AttesterArbiter | `0xE571D48D05962C57c95e48b8A7375466D1d02487` |
| SchemaArbiter | `0x9D5817Ff5519f45bf8ed6C3ADa638b874DBCb540` |
| UidArbiter | `0xaA9aEf96068f2BE679ae8781A4fC33FF4798758F` |
| RefUidArbiter | `0x546526311E6639399FdC583dF84eEe8b123D79d5` |
| RevocableArbiter | `0xe8d45cf2471882730a7e0ac142966DF07ae148d4` |
| TimeAfterArbiter | `0x2725A6869b42eDfD155889098408CcB3b1ed060e` |
| TimeBeforeArbiter | `0x014aA3DC53004B50bC13aa1D85A83bccA5c0671a` |
| TimeEqualArbiter | `0x1c21A8fB4F69ADb0ccDd22D8C125F8689bf227AF` |
| ExpirationTimeAfterArbiter | `0xbD90aF50Fb667724338EB8DA541f923F1822ac3C` |
| ExpirationTimeBeforeArbiter | `0xbCCE130337F2D8029982a14471d8686AFceF20fF` |
| ExpirationTimeEqualArbiter | `0x98D5bC7593143E55e9949da97603126CAe0BfD7F` |
| **Hook-Based** | |
| HookEscrowObligation | `0xaFfE00b43dD7843E8F6E8A2B4df0a62949Bf8352` |
| HooksEscrowObligation | `0xc79668ec88dA1fa6efd645Eca2dF338f39E4Dcb6` |
| ERC20EscrowHook | `0x13034d319e72e77e69EDD2ef09ed084d8Fc7cbAE` |
| ERC721EscrowHook | `0x3c1E21911C609714dBc0Ab90800c7aD8817B8e83` |
| ERC1155EscrowHook | `0x32889Ee549d61Ed5D14f2D499fCc809a4feC0dD8` |
| NativeTokenEscrowHook | `0xb0A6DDB4eBA2B11371b605eCFdDFE7491eE28bc0` |
| AttestationEscrowHook | `0x4De7D702A4edC5fe136B6899E10D770633F337aD` |
| AttestationReferenceEscrowHook | `0xCFa0756162eE176106185A42ed14f340aAA76F8a` |
| **Splitters** | |
| ERC20Splitter | `0x5313f28c9e32f45Bd639701e2E7e080b61c0f39e` |
| ERC1155Splitter | `0x11f6b04b2a8FB648fcD20bd4124c448a16ca37D1` |
| NativeTokenSplitter | `0xdA1fD1aC28C1d09E723e5a23Cd16554C87D0D09C` |
| TokenBundleSplitter | `0x0F235Bf6e5725791e118A25b4903856030525EF0` |
| TokenBundleSplitterUnvalidated | `0x4621C947D713cC7f63a377EE4D05eea789ab0956` |

### Ethereum Mainnet

| Contract | Address |
|----------|---------|
| EAS | `0xA1207F3BBa224E2c9c3c6D5aF63D0eb1582Ce587` |
| EAS Schema Registry | `0xA7b39296258348C78294F95B872b282326A97BDF` |
| ERC20EscrowObligation | `0xB2c808911E84E80156101983897Da7c80e13cB47` |
| ERC20PaymentObligation | `0xb822aA07F55a8B75Ee133ede1f21C4E49DE7952f` |
| ERC721EscrowObligation | `0x2A7df117e45D93d34a7893CC3aE8B105Ae0B561C` |
| ERC721PaymentObligation | `0x59A9c929778Ad2cC4D5DB6151bDEf0F9Fa7A068C` |
| ERC1155EscrowObligation | `0xf04d9CA943f57353A3A735494E503280C1cD5e77` |
| ERC1155PaymentObligation | `0x52748DD0E39eD6eA9f626179b5eb512302adA7D9` |
| NativeTokenEscrowObligation | `0x9bA50DB048d1E5db034377abf97F92496D027C71` |
| NativeTokenPaymentObligation | `0xf60db64506E366a0A6c1f4cF9D849Adc7bB886D6` |
| TokenBundleEscrowObligation | `0x677Aa9e1CD9D05f57FbCa2327155EA7479ec7Ac3` |
| TokenBundlePaymentObligation | `0x36Fcf1Ddee838a94B1358285A11e8bbbb90eD9A1` |
| AttestationEscrowObligation | `0x6eb7792D821f32914Be75901F1b4269B13Efad2e` |
| AttestationReferenceEscrowObligation | `0x1A7c6F951e0a33F4910dbe56a200Eb413AEca17b` |
| AtomicAttestationUtils | `0x0000000000000000000000000000000000000000` |
| StringObligation | `0xC51C938f5497be8157DAf8CCc3Eb11Afb8b752C0` |
| CommitRevealObligation | `0x0000000000000000000000000000000000000000` |
| TrivialArbiter | `0x594E79466b6ac01C6416C929e428264a4bdF0C92` |
| TrustedOracleArbiter | `0x3B2a812E3eb3B729D40d866Da16c2BB2b6cDd2f2` |
| AllArbiter | `0x847F69d27E4F1A8a115aCa3F4358B079706dc9CE` |
| AnyArbiter | `0xe968dFA581B8aBb94eC5F24d0b56163DE69511fD` |
| IntrinsicsArbiter | `0xaabdDAa76651d20922d1F561f924a40F6fE7710c` |
| ERC8004Arbiter | `0xBE7fE4d7CEb2140eeBdf01e12D198AEBAdC1F54D` |
| ExclusiveRevocableConfirmationArbiter | `0x941044D43F9d75dfA8Ad24880B9B9cAD6e116a66` |
| ExclusiveUnrevocableConfirmationArbiter | `0x16aeE626D398B547eDD5fa4BdAA638524C92921d` |
| NonexclusiveRevocableConfirmationArbiter | `0xe483EDA58b5f9Eba06A1ad0151dA5e4a5fFC8300` |
| NonexclusiveUnrevocableConfirmationArbiter | `0x01666d869918aDDDED1B30eF2d36f3C990F09BDE` |
| RecipientArbiter | `0xF1C9E20078A13816ACdDF3153e2eAaDd93Fd6E57` |
| AttesterArbiter | `0x6CC4068d471E96A1669097918e18017f5764f72a` |
| SchemaArbiter | `0x913eAdD13dcCdeD9CD5518075083b6C7A9574A8c` |
| UidArbiter | `0xae4fa2D5d7EDD6Aaf697dC0c98EDb921F0fEc058` |
| RefUidArbiter | `0xE9ee2c57B18283b66d342D33d63C55f1427f9e9B` |
| RevocableArbiter | `0xeda25079f76ef93c54cC042116Be8D88E49D3439` |
| TimeAfterArbiter | `0x0ea9e144FfDc6456E5cE8d1f75c686112e8f29c5` |
| TimeBeforeArbiter | `0x68A6e6022ab9984Ee1A9A6cee384FF2aE8be5264` |
| TimeEqualArbiter | `0x208385Fb349c01af2CfA8C6b86F633F6642718e2` |
| ExpirationTimeAfterArbiter | `0x309509db364526C7aE202eA9ED94a398a0819d38` |
| ExpirationTimeBeforeArbiter | `0xFAf8a07709dB9f90d0A0415876CfE00D904cd40B` |
| ExpirationTimeEqualArbiter | `0x7c782ac7741BB78DB7491Ee222af0a04f7f2bc0b` |
