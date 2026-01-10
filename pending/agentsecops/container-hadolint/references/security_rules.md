# Hadolint Security Rules Reference

Complete reference of Hadolint security rules with CIS Docker Benchmark mappings and remediation guidance.

## Table of Contents

- [Critical Security Rules](#critical-security-rules)
- [CIS Docker Benchmark Mappings](#cis-docker-benchmark-mappings)
- [Rule Categories](#rule-categories)

## Critical Security Rules

### DL3000: Use absolute WORKDIR

**Severity**: Error
**CIS Mapping**: 4.10 - Ensure secrets are not stored in Dockerfiles

**Issue**: Relative WORKDIR can lead to path confusion and security vulnerabilities.

**Bad**:
```dockerfile
WORKDIR app
```

**Good**:
```dockerfile
WORKDIR /app
```

---

### DL3001: Version pinning for package managers

**Severity**: Warning
**CIS Mapping**: 4.3 - Do not install unnecessary packages

**Issue**: Unpinned versions lead to non-reproducible builds and potential security vulnerabilities from package updates.

**Bad**:
```dockerfile
RUN yum install httpd
```

**Good**:
```dockerfile
RUN yum install -y httpd-2.4.51
```

---

### DL3002: Never switch back to root

**Severity**: Error
**CIS Mapping**: 4.1 - Create a user for the container

**Issue**: Switching back to root defeats container isolation and violates least privilege principle.

**Bad**:
```dockerfile
USER node
RUN npm install
USER root  # ❌ Don't switch back to root
```

**Good**:
```dockerfile
USER node
RUN npm install
# Stay as non-root user
```

---

### DL3003: Use WORKDIR instead of cd

**Severity**: Warning
**CIS Mapping**: Best practices

**Issue**: Using `cd` in RUN commands doesn't persist across instructions and can cause confusion.

**Bad**:
```dockerfile
RUN cd /app && npm install
```

**Good**:
```dockerfile
WORKDIR /app
RUN npm install
```

---

### DL3006: Always tag image versions

**Severity**: Warning
**CIS Mapping**: 4.3 - Ensure base images are verified

**Issue**: Using `:latest` or no tag creates non-reproducible builds and security risks.

**Bad**:
```dockerfile
FROM node
FROM ubuntu:latest
```

**Good**:
```dockerfile
FROM node:18.19.0-alpine3.19
FROM ubuntu:22.04
```

---

### DL3007: Pin Docker image versions to specific digest

**Severity**: Info
**CIS Mapping**: 4.3 - Ensure base images are verified

**Issue**: Tags can be overwritten; digests are immutable.

**Good**:
```dockerfile
FROM node:18.19.0-alpine3.19
```

**Better**:
```dockerfile
FROM node:18.19.0-alpine3.19@sha256:abc123...
```

---

### DL3008: Pin apt-get package versions

**Severity**: Warning
**CIS Mapping**: 4.3 - Do not install unnecessary packages

**Issue**: Unpinned apt packages lead to non-reproducible builds.

**Bad**:
```dockerfile
RUN apt-get update && apt-get install -y curl
```

**Good**:
```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl=7.68.0-1ubuntu2.14 && \
    rm -rf /var/lib/apt/lists/*
```

---

### DL3009: Delete apt cache after installation

**Severity**: Info
**CIS Mapping**: 4.6 - Reduce image size

**Issue**: Unnecessary cache increases image size and attack surface.

**Bad**:
```dockerfile
RUN apt-get update && apt-get install -y curl
```

**Good**:
```dockerfile
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*
```

---

### DL3013: Pin pip package versions

**Severity**: Warning
**CIS Mapping**: 4.3 - Do not install unnecessary packages

**Issue**: Unpinned pip packages compromise build reproducibility.

**Bad**:
```dockerfile
RUN pip install flask
```

**Good**:
```dockerfile
RUN pip install --no-cache-dir flask==2.3.2
```

---

### DL3020: Use COPY instead of ADD

**Severity**: Error
**CIS Mapping**: 4.9 - Use COPY instead of ADD

**Issue**: ADD has implicit behavior (auto-extraction, URL support) that can be exploited.

**Bad**:
```dockerfile
ADD app.tar.gz /app/
ADD https://example.com/file.txt /tmp/
```

**Good**:
```dockerfile
COPY app.tar.gz /app/
# For URLs, use RUN wget/curl instead
RUN curl -O https://example.com/file.txt
```

**Exception**: ADD is acceptable only when you explicitly need tar auto-extraction.

---

### DL3025: Use JSON notation for CMD and ENTRYPOINT

**Severity**: Warning
**CIS Mapping**: 4.6 - Add HEALTHCHECK instruction

**Issue**: Shell form enables shell injection attacks and doesn't properly handle signals.

**Bad**:
```dockerfile
CMD node server.js
ENTRYPOINT /app/start.sh
```

**Good**:
```dockerfile
CMD ["node", "server.js"]
ENTRYPOINT ["/app/start.sh"]
```

---

### DL3028: Use credentials via build secrets

**Severity**: Warning
**CIS Mapping**: 4.10 - Do not store secrets in Dockerfiles

**Issue**: Credentials in ENV or ARG end up in image layers.

**Bad**:
```dockerfile
ARG API_KEY=secret123
RUN curl -H "Authorization: $API_KEY" https://api.example.com
```

**Good** (BuildKit secrets):
```dockerfile
# syntax=docker/dockerfile:1.4
RUN --mount=type=secret,id=api_key \
    curl -H "Authorization: $(cat /run/secrets/api_key)" https://api.example.com
```

---

### DL3059: Multiple RUN instructions

**Severity**: Info
**CIS Mapping**: 4.6 - Optimize layers

**Issue**: Multiple RUN instructions create unnecessary layers, increasing image size.

**Less Optimal**:
```dockerfile
RUN apt-get update
RUN apt-get install -y curl
RUN curl -O https://example.com/file
```

**Better**:
```dockerfile
RUN apt-get update && \
    apt-get install -y curl && \
    curl -O https://example.com/file && \
    rm -rf /var/lib/apt/lists/*
```

**Note**: Balance between layer caching and image size. For development, separate RUN instructions may aid caching.

---

## CIS Docker Benchmark Mappings

### CIS 4.1: Create a user for the container

**Hadolint Rules**: DL3002

**Requirement**: Don't run containers as root.

**Implementation**:
```dockerfile
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser
# Don't switch back to root
```

---

### CIS 4.3: Do not install unnecessary packages

**Hadolint Rules**: DL3001, DL3008, DL3013, DL3015

**Requirement**: Minimize attack surface by installing only required packages with pinned versions.

**Implementation**:
```dockerfile
# Use --no-install-recommends
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    package1=version1 \
    package2=version2 && \
    rm -rf /var/lib/apt/lists/*
```

---

### CIS 4.6: Add HEALTHCHECK instruction

**Hadolint Rules**: DL3025 (related to proper CMD/ENTRYPOINT)

**Requirement**: Include HEALTHCHECK to enable container health monitoring.

**Implementation**:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

---

### CIS 4.7: Do not use update instructions alone

**Hadolint Rules**: DL3009, DL3014, DL3015

**Requirement**: Update and install should be in same RUN instruction to prevent cache issues.

**Implementation**:
```dockerfile
# Bad
RUN apt-get update
RUN apt-get install -y package

# Good
RUN apt-get update && \
    apt-get install -y package && \
    rm -rf /var/lib/apt/lists/*
```

---

### CIS 4.9: Use COPY instead of ADD

**Hadolint Rules**: DL3020

**Requirement**: Use COPY for file operations; ADD only for tar extraction.

**Implementation**: See DL3020 above.

---

### CIS 4.10: Do not store secrets in Dockerfiles

**Hadolint Rules**: DL3028, DL3000 (indirectly)

**Requirement**: Use build secrets or external secret management.

**Implementation**: See DL3028 above.

---

## Rule Categories

### Base Image Security
- DL3006: Always tag image versions
- DL3007: Use specific image digests
- DL3026: Use trusted registries only

### Package Management
- DL3001: Version pinning (yum/dnf/zypper)
- DL3008: Version pinning (apt-get)
- DL3013: Version pinning (pip)
- DL3016: Version pinning (npm)
- DL3018: Version pinning (apk)
- DL3028: Use build secrets for credentials

### Instruction Best Practices
- DL3000: Use absolute WORKDIR
- DL3003: Use WORKDIR instead of cd
- DL3020: Use COPY instead of ADD
- DL3025: Use JSON notation for CMD/ENTRYPOINT

### User and Permissions
- DL3002: Never switch back to root
- DL4001: Use SHELL to switch shells securely

### Image Optimization
- DL3009: Delete apt cache
- DL3014: Use -y for apt-get
- DL3015: Avoid additional packages
- DL3059: Minimize RUN instructions

### ShellCheck Integration
- DL4000-DL4006: Shell script best practices in RUN

---

## Quick Reference Table

| Rule | Severity | CIS | Description |
|------|----------|-----|-------------|
| DL3000 | Error | 4.10 | Use absolute WORKDIR |
| DL3001 | Warning | 4.3 | Pin yum versions |
| DL3002 | Error | 4.1 | Don't switch to root |
| DL3003 | Warning | - | Use WORKDIR not cd |
| DL3006 | Warning | 4.3 | Tag image versions |
| DL3007 | Info | 4.3 | Use image digests |
| DL3008 | Warning | 4.3 | Pin apt versions |
| DL3009 | Info | 4.7 | Delete apt cache |
| DL3013 | Warning | 4.3 | Pin pip versions |
| DL3020 | Error | 4.9 | Use COPY not ADD |
| DL3025 | Warning | 4.6 | JSON notation CMD |
| DL3028 | Warning | 4.10 | Use build secrets |
| DL3059 | Info | - | Multiple RUN instructions |

---

## Additional Resources

- [Hadolint Rules Wiki](https://github.com/hadolint/hadolint/wiki)
- [CIS Docker Benchmark v1.6](https://www.cisecurity.org/benchmark/docker)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [NIST SP 800-190](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)
