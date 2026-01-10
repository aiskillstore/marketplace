# Bitbucket Pipeline Artifacts Research

**Date:** 2025-11-03
**Researcher:** Claude (Sonnet 4.5)
**Test Case:** apra-licensing-core build #51

## Problem Statement

Bitbucket Pipelines allow steps to produce artifacts (defined in `bitbucket-pipelines.yml` with the `artifacts:` section), but there is **no documented API** to download these artifacts programmatically.

## Research Findings

### 1. Pipeline Artifacts API Status

**Result:** ❌ **NO DIRECT API EXISTS**

- Confirmed via web search (March 2024 community discussions)
- Confirmed via testing with build #51
- Step details endpoint (`/repositories/{workspace}/{repo}/pipelines/{uuid}/steps/{step_uuid}`) returns step info but NO artifact links
- Teardown commands show `UPLOAD_ARTIFACTS` action but provide no download mechanism

### 2. Test Case: apra-licensing-core Build #51

**Pipeline UUID:** `{1acf2818-e3e1-4f07-992c-e8139e9929e7}`

**Steps with artifacts:**
1. Step UUID: `{6b187d78-0bbd-4fff-899e-ebe92701352d}`
   - Name: "Build Licensing Libraries (Ubuntu 20.04 x64 - GCC 9)"
   - Status: SUCCESSFUL
   - Has `UPLOAD_ARTIFACTS` in teardown_commands

2. Step UUID: `{73851dd6-b68f-401f-937b-b43e6ee5778d}`
   - Name: "Build Licensing Libraries (Ubuntu 20.04 ARM64 - GCC 9)"
   - Status: SUCCESSFUL
   - Has `UPLOAD_ARTIFACTS` in teardown_commands

3. Step UUID: (third step - Create Release Package)
   - Creates: `apra-licensing-libs-{date}-{sha}.zip`
   - Should have this as artifact

**API Response Analysis:**
```json
{
  "uuid": "{6b187d78-0bbd-4fff-899e-ebe92701352d}",
  "name": "Build Licensing Libraries (Ubuntu 20.04 x64 - GCC 9)",
  "links": null  // ❌ No artifacts link!
}
```

### 3. Artifacts Lifecycle

- **Storage Duration:** 14 days after step execution
- **Access Method:** Only within subsequent pipeline steps (can be downloaded in manual steps)
- **External Access:** ❌ Not possible via API

### 4. Workaround: Bitbucket Downloads API

**Status:** ✅ **AVAILABLE** (needs testing)

The Downloads API provides an alternative storage mechanism:

**Endpoints:**
- `GET /repositories/{workspace}/{repo}/downloads` - List downloads
- `POST /repositories/{workspace}/{repo}/downloads` - Upload file
- `GET /repositories/{workspace}/{repo}/downloads/{filename}` - Download file
- `DELETE /repositories/{workspace}/{repo}/downloads/{filename}` - Delete file

**How to use:**
1. In `bitbucket-pipelines.yml`, add a step that uploads artifacts to Downloads:
   ```yaml
   - step:
       name: Upload Artifacts
       script:
         - pipe: atlassian/bitbucket-upload-file:0.3.5
           variables:
             FILENAME: "my-artifact.zip"
   ```

2. Or use curl in pipeline:
   ```bash
   curl -X POST -u "${BB_AUTH_STRING}" \
     https://api.bitbucket.org/2.0/repositories/${BITBUCKET_WORKSPACE}/${BITBUCKET_REPO_SLUG}/downloads \
     -F files=@"artifact.zip"
   ```

3. Then download via API:
   ```bash
   curl -u user:pass \
     https://api.bitbucket.org/2.0/repositories/workspace/repo/downloads/artifact.zip
   ```

## Recommendations

### Option 1: Use Downloads API (Recommended)

**Pros:**
- Full API support
- Persistent storage (not limited to 14 days)
- Can be accessed anytime
- Easy to integrate

**Cons:**
- Requires modifying `bitbucket-pipelines.yml`
- Extra step in pipeline
- Uses repository storage quota

**Implementation:**
1. Add `list-downloads` command to CLI
2. Add `get-download` command to CLI
3. Add `download-artifact` helper function
4. Update SKILL.md with artifact download patterns

### Option 2: Wait for Bitbucket API Update

**Status:** ❌ Not recommended
- No indication Atlassian will add this
- Community requests since 2020+ with no response

### Option 3: Alternative Storage

**Examples:**
- AWS S3
- Azure Blob Storage
- GitHub Releases
- Artifactory

**Pros:** Full control, better for CI/CD
**Cons:** More complex, requires external service

## Proposed Solution

**Add Downloads API support to bitbucket-devops skill:**

### CLI Commands to Add:
```bash
# List all downloads
node index-cli.js list-downloads <workspace> <repo>

# Get download URL
node index-cli.js get-download <workspace> <repo> <filename>

# Download file
node index-cli.js download-file <workspace> <repo> <filename> [output-path]
```

### Helper Function:
```bash
# Find and download latest artifact matching pattern
node helpers.js download-latest-artifact <workspace> <repo> <pattern>
```

### Usage Pattern:
```bash
# User: "Download the latest licensing libraries build"
# Claude:
node helpers.js download-latest-artifact "kumaakh" "apra-licensing-core" "apra-licensing-libs-*.zip"
```

## Next Steps

1. ✅ Complete research (DONE)
2. ⏳ Test Downloads API with apra-licensing-core
3. ⏳ Add downloads commands to CLI
4. ⏳ Create helper functions
5. ⏳ Update SKILL.md
6. ⏳ Document in README

## Conclusion

**Direct pipeline artifacts download via API: ❌ NOT POSSIBLE**

**Recommended workaround: ✅ Use Downloads API**

This requires pipeline changes but provides reliable, programmatic artifact access. The skill can provide seamless download functionality once artifacts are uploaded to Downloads during the pipeline.
