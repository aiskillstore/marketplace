import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { isDeepStrictEqual } from 'node:util'

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex')

// Consume the exact evidence from the one comparison. A replaced file, changed
// input, or unrelated report must not become the explanation of this summary.
export function verifyDiffEvidence(summary, source, candidate) {
  const evidence = summary?.fullEvidence
  if (!summary?.fullEvidenceAvailable || !evidence?.path || !evidence.sha256) {
    throw new Error(
      'Semantic diff did not retain its complete evidence; the runtime must support diff --output',
    )
  }
  const bytes = readFileSync(evidence.path)
  if (sha256(bytes) !== evidence.sha256) throw new Error('Semantic diff evidence SHA-256 mismatch')
  const full = JSON.parse(bytes)
  const expected = {
    algorithm: 'sha256',
    baseline: sha256(readFileSync(source)),
    target: sha256(readFileSync(candidate)),
  }
  if (
    full.schemaVersion !== 'pptx-diff/v1' ||
    full.status !== 'success' ||
    full.detail !== 'full' ||
    !isDeepStrictEqual(full.inputBinding, expected) ||
    !isDeepStrictEqual(summary.inputBinding, expected) ||
    !isDeepStrictEqual(full.summary, summary.summary)
  ) {
    throw new Error('Semantic diff evidence is not bound to this comparison and its current inputs')
  }
  return full
}
