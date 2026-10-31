---
name: container-publish
description: >
  Dockerfile-less containerization using the .NET 10 SDK container publishing
  feature. Covers MSBuild properties, chiseled images, multi-arch builds, and
  registry publishing — all without writing a Dockerfile.
  Load this skill when the user wants to containerize without a Dockerfile, or
  mentions "dotnet publish container", "PublishContainer", "ContainerRepository",
  "ContainerFamily", "chiseled", "distroless", "container publish", "SDK
  container", "no Dockerfile", or "containerize without Docker".
---

# Container Publishing (No Dockerfile)

## Core Principles

1. **No Dockerfile needed** — The .NET 10 SDK builds OCI-compliant container images directly from `dotnet publish /t:PublishContainer`. No Dockerfile to write or maintain.
2. **Chiseled images for production** — Use `noble-chiseled` base images: no shell, no package manager, 7 Linux components vs 100+. Smallest attack surface.
3. **Non-root by default** — .NET 10 container images run as the `app` user automatically. Never override to root in production.
4. **Configuration in the .csproj** — All container settings are MSBuild properties, versioned with your project. No separate files to drift.

## Patterns

### Minimal Container Publish

No project file changes needed. Just publish:

```bash
dotnet publish /t:PublishContainer --os linux --arch x64
```

This creates a container image in your local Docker daemon using the default `aspnet:10.0` base image.

### Production-Ready .csproj Configuration

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <ContainerRepository>mycompany/myapp-api</ContainerRepository>
    <ContainerFamily>noble-chiseled</ContainerFamily>
  </PropertyGroup>

  <ItemGroup>
    <ContainerPort Include="8080" Type="tcp" />
    <ContainerEnvironmentVariable Include="ASPNETCORE_HTTP_PORTS" Value="8080" />
    <ContainerEnvironmentVariable Include="DOTNET_EnableDiagnostics" Value="0" />
    <ContainerLabel Include="org.opencontainers.image.vendor" Value="MyCompany" />
  </ItemGroup>

</Project>
```

### Publishing to a Registry

Authenticate with `docker login` first, then specify the registry:

```bash
# GitHub Container Registry
docker login ghcr.io
dotnet publish /t:PublishContainer --os linux --arch x64 \
    -p ContainerRegistry=ghcr.io \
    -p ContainerImageTag=1.0.0

# Azure Container Registry
az acr login --name myregistry
dotnet publish /t:PublishContainer --os linux --arch x64 \
    -p ContainerRegistry=myregistry.azurecr.io

# Docker Hub (requires username prefix in repository)
dotnet publish /t:PublishContainer --os linux --arch x64 \
    -p ContainerRegistry=docker.io \
    -p ContainerRepository=myuser/myapp
```

### Multi-Architecture Images

Build images for multiple platforms with a single publish:

```xml
<PropertyGroup>
    <RuntimeIdentifiers>linux-x64;linux-arm64</RuntimeIdentifiers>
    <ContainerRuntimeIdentifiers>linux-x64;linux-arm64</ContainerRuntimeIdentifiers>
</PropertyGroup>
```

```bash
dotnet publish /t:PublishContainer
```

This produces an OCI Image Index — registries serve the correct architecture automatically.

### Multiple Tags

```bash
# Bash — note the quoting for semicolons
dotnet publish /t:PublishContainer --os linux --arch x64 \
    -p ContainerImageTags='"1.0.0;latest"'
```

Or in the project file:

```xml
<ContainerImageTags>1.0.0;latest</ContainerImageTags>
```

### Save as Tarball (No Docker Required)

No container runtime needed on the build machine. Useful for CI scanning:

```bash
dotnet publish /t:PublishContainer --os linux --arch x64 \
    -p ContainerArchiveOutputPath=./images/myapp.tar.gz

# Scan with Trivy before pushing
trivy image --input ./images/myapp.tar.gz
```

### Chiseled Image Variants

| ContainerFamily | Use Case | Shell | Size |
|----------------|----------|-------|------|
| *(default)* | General purpose (Debian) | Yes | ~220 MB |
| `noble-chiseled` | Production (no shell) | No | ~110 MB |
| `noble-chiseled-extra` | Production with localization (ICU) | No | ~120 MB |
| `alpine` | Small size, has shell | Yes | ~112 MB |

```xml
<!-- Standard chiseled (InvariantGlobalization=true) -->
<ContainerFamily>noble-chiseled</ContainerFamily>

<!-- Chiseled with ICU for localization -->
<ContainerFamily>noble-chiseled-extra</ContainerFamily>
```

For Native AOT, the SDK auto-selects `chiseled-aot`:

```xml
<PublishAot>true</PublishAot>
<!-- SDK picks runtime-deps:10.0-noble-chiseled-aot automatically -->
```

### CI/CD with GitHub Actions

```yaml
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      packages: write
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-dotnet@v5
        with:
          dotnet-version: '10.0.x'
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - run: |
          dotnet publish src/MyApp.Api/MyApp.Api.csproj \
            /t:PublishContainer --os linux --arch x64 \
            -p ContainerRegistry=ghcr.io \
            -p ContainerRepository=${{ github.repository_owner }}/myapp \
            -p ContainerImageTag=${{ github.sha }}
```

## Anti-patterns

### Don't Use the Deprecated Property Names

```xml
<!-- BAD — ContainerImageName is deprecated -->
<ContainerImageName>myapp</ContainerImageName>

<!-- GOOD — use ContainerRepository -->
<ContainerRepository>myapp</ContainerRepository>
```

### Don't Use PublishProfile=DefaultContainer

```bash
# BAD — old approach, inconsistent across project types
dotnet publish -p:PublishProfile=DefaultContainer

# GOOD — use the MSBuild target directly
dotnet publish /t:PublishContainer
```

### Don't Forget to Target Linux

```bash
# BAD on Windows — may produce a Windows container
dotnet publish /t:PublishContainer

# GOOD — explicitly target Linux
dotnet publish /t:PublishContainer --os linux --arch x64
```

### Don't Skip Authentication Before Push

```bash
# BAD — fails with CONTAINER1013 error
dotnet publish /t:PublishContainer -p ContainerRegistry=ghcr.io

# GOOD — authenticate first
docker login ghcr.io
dotnet publish /t:PublishContainer -p ContainerRegistry=ghcr.io
```

### Don't Use SDK Publishing When You Need OS Packages

```xml
<!-- BAD — SDK container publish cannot run apt-get or install native packages -->
<!-- There is no RUN equivalent -->

<!-- GOOD — create a custom base image with a Dockerfile first, then reference it -->
<ContainerBaseImage>myregistry/custom-base:1.0</ContainerBaseImage>
```

## Decision Guide

| Scenario | Recommendation |
|----------|---------------|
| Standard ASP.NET Core API | SDK container publishing with `noble-chiseled` |
| Worker service / console app | SDK container publishing (native .NET 10 support) |
| Needs native OS packages | Dockerfile (or custom base image + SDK publishing) |
| Azure Functions | Dockerfile (not supported by SDK publishing) |
| CI without Docker daemon | Tarball output with `ContainerArchiveOutputPath` |
| Multi-arch deployment (x64 + arm64) | `ContainerRuntimeIdentifiers` property |
| Production image size | `noble-chiseled` (~110 MB) or Native AOT (~10 MB) |
| Local development | `dotnet publish /t:PublishContainer --os linux --arch x64` |
| Registry push | `ContainerRegistry` + `docker login` |
