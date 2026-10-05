# CI/CD and Container Delivery

Build once, verify the exact artifact, and promote it by immutable identity. A pipeline is a release control system, not a collection of copied YAML steps.

## Establish the delivery baseline

Inspect the package manager and lockfile, supported Node.js version, build output, Dockerfile and ignore rules, CI workflows, registry, deployment environments, secret/authentication mechanism, migration step, artifact identity, approval policy, and rollback process. Trace one commit from checkout to the running revision.

Record separately:

- source revision;
- dependency lockfile identity;
- build run and builder identity;
- image or artifact digest;
- deployment environment and release record;
- database/configuration changes coupled to the release.

A tag is a useful human label but not an immutable identity. Verify and deploy the digest when the platform supports it.

## Design the pipeline as gates

### 1. Source and trust

- Give workflow tokens and service identities the minimum permissions required by each job.
- Prefer short-lived workload identity or OIDC federation over stored cloud credentials.
- Pin third-party workflow dependencies according to the platform's security model; review update provenance.
- Treat pull-request titles, branch names, issue text, artifacts, caches, and forked code as untrusted input.
- Never expose production secrets to untrusted pull-request code or interpolate untrusted values into a shell command.

### 2. Reproducible install and build

- Pin the Node.js major/minor policy and package-manager version used by local development, CI, and the runtime image.
- Install from the committed lockfile, such as with `npm ci`, and fail on drift.
- Run type/build, lint, unit, integration, contract, migration, and security checks in proportion to the release risk.
- Isolate tests from production services and credentials.
- Fail the pipeline when required generated contracts or migrations are stale.

### 3. Artifact and supply chain

- Produce one immutable artifact and promote it; do not rebuild different bytes per environment.
- Attach source revision and safe build metadata.
- Generate an SBOM and provenance/attestation when the repository or compliance model uses them.
- Scan dependencies, source, images, and IaC, then triage exploitability and ownership. A scanner count is not a release decision by itself.
- Sign or attest artifacts only with protected identities and verify policy at a meaningful boundary.
- Rebuild supported base images regularly so patched operating-system and runtime packages enter the artifact.

### 4. Promotion and deployment

- Use protected environments, scoped credentials, concurrency controls, and an auditable deployment record.
- Promote the tested digest through environments with environment-specific configuration supplied at runtime.
- Run migrations through one controlled actor with compatibility and recovery checks.
- Gate production on required evidence, not on a manual click with no defined review criteria.
- Observe the rollout against success and rollback signals, then record the outcome.

## Build a production container

- Use multi-stage builds to separate dependency/build tooling from the runtime filesystem.
- Keep the build context small with `.dockerignore`; do not copy Git history, local secrets, test output, or unrelated files.
- Install only runtime dependencies in the final stage when the application does not need development tooling.
- Choose a maintained base image deliberately. Pin versions or digests according to the repository's update process rather than using an unreviewed floating tag.
- Run as a non-root user and use a read-only root filesystem or dropped Linux capabilities when the application and platform support them.
- Write mutable data only to declared temporary or persistent locations; do not rely on the container filesystem for durable state.
- Start the real Node process with signal behavior verified. Avoid wrapper chains that prevent `SIGTERM` from reaching the application.
- Add no credentials to `ARG`, image layers, copied files, or build logs. Use BuildKit secret/SSH mounts for build-time access when required.
- Do not put a process supervisor in every application container by habit; use one only when the runtime contract genuinely needs multiple managed processes.

Image size is not the only objective. Patchability, predictable native dependencies, startup behavior, diagnostics, and compatibility matter more than winning a size comparison.

## Release and rollback rules

Define before deployment:

- rollout strategy and maximum unavailable/surge capacity;
- health and business success signals;
- observation window and automated/manual abort criteria;
- schema, event, cache, and configuration compatibility;
- rollback artifact and command/procedure;
- owner and communication path.

Rollback is not safe when the old application cannot read the new schema or messages. Use expand-and-contract changes or a forward repair when data evolution is irreversible.

## Verify the delivered artifact

1. Reproduce the build from the lockfile in a clean environment.
2. Run the final container as its configured user with production-like signals, filesystem, and configuration.
3. Inspect the image for unexpected files, credentials, packages, and architecture mismatches.
4. Verify the deployed digest matches the promoted digest.
5. Exercise startup, readiness, a representative request/job, `SIGTERM`, drain, and resource closure.
6. Prove rollback or forward recovery in a non-production environment for consequential releases.

See Docker's official [build best practices](https://docs.docker.com/build/building/best-practices/), [multi-stage builds](https://docs.docker.com/build/building/multi-stage/), and [build secrets](https://docs.docker.com/build/building/secrets/), plus GitHub's [secure use of Actions](https://docs.github.com/en/actions/reference/security/secure-use), [deployment environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments), and [artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations).
