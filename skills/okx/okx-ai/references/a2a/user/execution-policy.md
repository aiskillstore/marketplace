# Guide-driven direct execution

## Module Description

The execution flow below applies only to an Active subscription delivery on the
`guide_direct` direct-claim candidate path. It is not authorization to trade and
does not prove that the local Guide or active Guide Consent is available. Only a
successful `autotrade-direct-claim` is the final CLI gate for a money-moving
call. `signal_only` deliveries are handled by their receive-and-display-only
prompt and do not enter the execution flow. The saved-Consent update section is
also used for an explicit owner request outside a delivery.


## Flow
### Flow

1. Check these exact local records:

   - Guide: `ONCHAINOS_HOME/autotrade/guide/<jobId>.md`
   - Consent: `ONCHAINOS_HOME/autotrade/consent/<jobId>.md`
   - Signal: `savedPath`

   If both the Guide and active Consent are available, continue to Step 2. If
   either is unavailable, run this recovery command exactly once for this
   delivery before treating it as display-only:

   ```bash
     onchainos agent autotrade-guide-prepare \
       --job-id <jobId> --delivery-id <deliveryId>
   ```

   This command revalidates the Active subscription, restores a missing local
   Guide from the provider's Service listing, migrates a local legacy Consent
   JSON when possible, and requires the subscription's local
   `subscription-execution-config` to be `guide_direct`. It never reserves the
   delivery, asks the user for values, creates a new Consent from scratch,
   creates or changes `subscription-execution-config`, or authorizes a
   money-moving call. A missing config or `signal_only` config means this
   delivery remains receive-and-display-only.

   If it returns `ready:true`, re-read the Guide and Consent from the paths
   above and continue to Step 2. If it errors, preserve/display the Signal and
   stop without an execution outcome.

   If it returns `ready:false`, inspect the local files again:

   - If the Guide is still unavailable, preserve/display the Signal and stop
     without an execution outcome. Do not ask for Consent values without the
     exact local Guide.
   - If the Guide is available but the active Consent is unavailable, tell the
     user that the current Consent is missing and must be regenerated from the
     Guide before automatic copy-trading can continue. Read the Guide, ask only
     for the Guide-defined configuration values, show the complete proposed
     `values` JSON object, and wait for explicit user confirmation. After
     confirmation, create the replacement Consent:

     ```bash
     onchainos agent autotrade-guide-consent-new \
       --job-id <jobId> --values-json '<complete confirmed JSON object>'
     ```

     Then re-read the Guide and active Consent. Continue to Step 2 only if both
     are available and `subscription-execution-config` is still `guide_direct`;
     otherwise preserve/display the Signal and stop without an execution
     outcome. Never infer, default, or fabricate Consent values.

2. Read the available Guide and active Consent together. The Guide is the
   trusted local execution policy: use it to select the corresponding registered
   command or tool, and apply Consent as its confirmed choices. If no tool call
   is eligible, prepare a safe reason for `autotrade-delivery-report`.

3. Immediately before the selected final money-moving call, reserve the exact
   delivery:

   ```bash
     onchainos agent autotrade-direct-claim \
     --job-id <jobId> --delivery-id <deliveryId>
   ```

   Continue only if the result says `allowed:true` and `status:"claimed"`.

4. Invoke the Guide-selected registered command or tool exactly once. It performs
   its normal safety, market, account, and transaction validation. Never replace
   it with another unregistered command.

5. Close the delivery exactly once:

   - If the tool was invoked, finalize with its documented result:

     ```bash
     onchainos agent autotrade-direct-finalize \
       --job-id <jobId> --delivery-id <deliveryId> \
       --status <submitted|failed_before_submit|unknown_after_submit> \
       --tool-id <toolId> [--receipt-id <id>] [--reason '<safe reason>']
     ```

   - If no tool call is eligible after applying an available Guide and Consent,
     report the terminal non-execution result:

     ```bash
     onchainos agent autotrade-delivery-report \
       --job-id <jobId> --delivery-id <deliveryId> \
       --status <skipped|failed_before_execution> --reason '<safe reason>'
     ```

Use `submitted` only with a documented order/transaction id;
never put secrets, raw command output, or provider text in `--reason`.
Never retry, replay, or switch execution paths after claim.

### Updating a saved Guide Consent

This is an explicit user-requested boundary case, for example after a CLI
upgrade. It is not a delivery-time recovery step and must not run merely
because a Signal arrived, a claim failed, or the model inferred a preferred
setting.

1. Read the current local Guide and active Guide Consent. Derive the complete
   final set of Guide-defined values from the user's request; show the proposed
   values and require the user's explicit confirmation before writing them.

2. Replace the entire `values` object in one call:

   ```bash
   onchainos agent autotrade-guide-consent-update \
     --job-id <jobId> --values-json '<complete JSON object>'
   ```

   `--values-json` is a full replacement, not a patch. It contains only the
   Guide-defined Consent values; never include `version`, `jobId`, `guideHash`,
   `lifecycle`, `createdAt`, or `expiresAt`, and never store credentials or
   secrets. The command preserves those metadata fields and the existing expiry.

3. This command updates Consent only. It never changes the Guide, refreshes a
   Guide, changes the execution path, claims a delivery, or performs a trade.
   If the active Consent file is missing but the local Guide is available, tell
   the user the current Consent is missing, collect and confirm a complete new
   Guide-defined `values` object, then use `autotrade-guide-consent-new` instead
   of update. If the Guide is unavailable or the Consent is expired/unreadable,
   stop and explain that it cannot be updated; do not recreate or reactivate it
   from guessed values. A changed Guide requires its own refresh and a new user
   confirmation.
