# DNAnexus App Development

## Overview

Apps and Applets are executable programs that run on the DNAnexus platform. They can be written in Python or Bash and are deployed with all necessary dependencies and configuration.

## Applets vs Apps

- **Applets**: Data objects that exist inside a project. Suitable for development and testing phases.
- **Apps**: Versioned, shareable executable files that don't directly exist inside a project. Can be published for others to use.

Both are created identically until the final build step. An Applet can be converted to an App later.

## Creating an App/Applet

### Using dx-app-wizard

Generate a skeleton app directory structure:

```bash
dx-app-wizard
```

This creates:
- `dxapp.json` - Configuration file
- `src/` - Source code directory
- `resources/` - Bundled dependencies
- `test/` - Test files

### Building and Deployment

Build Applet:
```bash
dx build
```

Build App:
```bash
dx build --app
```

Build process:
1. Validate dxapp.json configuration
2. Bundle source code and resources
3. Deploy to platform
4. Return applet/app ID

## App Directory Structure

```
my-app/
├── dxapp.json          # Metadata and configuration
├── src/
│   └── my-app.py       # Main execution file (Python)
│   └── my-app.sh       # Or Bash script
├── resources/          # Bundled files and dependencies
│   └── tools/
│   └── data/
└── test/               # Test data and scripts
    └── test.json
```

## Python App Structure

### Entry Points

Python apps use the `@dxpy.entry_point()` decorator to define functions:

```python
import dxpy

@dxpy.entry_point('main')
def main(input1, input2):
    # Process input
    # Return output
    return {
        "output1": result1,
        "output2": result2
    }

dxpy.run()
```

### Input/Output Handling

**Input**: DNAnexus data objects are represented as dictionaries containing links:

```python
@dxpy.entry_point('main')
def main(reads_file):
    # Convert link to handle
    reads_dxfile = dxpy.DXFile(reads_file)

    # Download to local filesystem
    dxpy.download_dxfile(reads_dxfile.get_id(), "reads.fastq")

    # Process file...
```

**Output**: Return raw types directly, convert file outputs to links:

```python
    # Upload result file
    output_file = dxpy.upload_local_file("output.fastq")

    return {
        "trimmed_reads": dxpy.dxlink(output_file)
    }
```

## Bash App Structure

Bash apps use a simpler shell script approach:

```bash
#!/bin/bash
set -e -x -o pipefail

main() {
    # Download input
    dx download "$reads_file" -o reads.fastq

    # Process
    process_reads reads.fastq > output.fastq

    # Upload output
    trimmed_reads=$(dx upload output.fastq --brief)

    # Set job output
    dx-jobutil-add-output trimmed_reads "$trimmed_reads" --class=file
}
```

## Common Development Patterns

### 1. Bioinformatics Pipeline

Download → Process → Upload pattern:

```python
# Download input
dxpy.download_dxfile(input_file_id, "input.fastq")

# Run analysis
subprocess.check_call(["tool", "input.fastq", "output.bam"])

# Upload result
output = dxpy.upload_local_file("output.bam")
return {"aligned_reads": dxpy.dxlink(output)}
```

### 2. Multi-File Processing

```python
# Process multiple inputs
for file_link in input_files:
    file_handler = dxpy.DXFile(file_link)
    local_path = f"{file_handler.name}"
    dxpy.download_dxfile(file_handler.get_id(), local_path)
    # Process each file...
```

### 3. Parallel Processing

Apps can spawn subjobs for parallel execution:

```python
# Create subjobs
subjobs = []
for item in input_list:
    subjob = dxpy.new_dxjob(
        fn_input={"input": item},
        fn_name="process_item"
    )
    subjobs.append(subjob)

# Collect results
results = [job.get_output_ref("result") for job in subjobs]
```

## Execution Environment

Apps run in isolated Linux virtual machines (Ubuntu 24.04) with:
- Internet access
- DNAnexus API access
- Temporary staging space in `/home/dnanexus`
- Input files downloaded to job workspace
- Root access for installing dependencies

## Testing Apps

### Local Testing

Test app logic locally before deployment:

```bash
cd my-app
python src/my-app.py
```

### Platform Testing

Run Applet on the platform:

```bash
dx run applet-xxxx -i input1=file-yyyy
```

Monitor job execution:

```bash
dx watch job-zzzz
```

View job logs:

```bash
dx watch job-zzzz --get-streams
```

## Best Practices

1. **Error Handling**: Use try-except blocks with detailed error messages.
2. **Logging**: Print progress and debug info to stdout/stderr.
3. **Validation**: Validate inputs before processing.
4. **Cleanup**: Delete temporary files after completion.
5. **Documentation**: Include clear descriptions in dxapp.json.
6. **Testing**: Test against various input types and edge cases.
7. **Versioning**: Use semantic versioning for apps.

## Common Issues

### File Not Found
Ensure files are properly downloaded before accessing:
```python
dxpy.download_dxfile(file_id, local_path)
# Now you can safely open local_path
```

### Out of Memory
Specify larger instance types in `systemRequirements` in dxapp.json.

### Timeout
Increase timeout in dxapp.json, or split task into smaller subjobs.

### Permission Errors
Ensure the app has necessary permissions granted in dxapp.json.
