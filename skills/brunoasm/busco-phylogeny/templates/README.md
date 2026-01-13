# Phylogenomics Workflow Templates

This directory contains template scripts for running the phylogenomics pipeline across different computing environments.

## Directory Structure

```
templates/
├── slurm/      # SLURM job scheduler templates
├── pbs/        # PBS/Torque job scheduler templates
└── local/      # Local machine templates (with GNU parallel support)
```

## Template Naming Convention

Templates follow a consistent naming pattern: `NN_step_name[_variant].ext`

- `NN`: Step number (e.g., `02` for compleasm, `08a` for partition search)
- `step_name`: Descriptive name of the pipeline step
- `_variant`: Optional variant (e.g., `_first`, `_parallel`, `_serial`)
- `.ext`: File extension (`.job` for schedulers, `.sh` for local scripts)

## Available Templates

### Step 2: Ortholog Identification (compleasm)

**SLURM:**
- `02_compleasm_first.job` - Process first genome to download lineage database
- `02_compleasm_parallel.job` - Array job for remaining genomes

**PBS:**
- `02_compleasm_first.job` - Process first genome to download lineage database
- `02_compleasm_parallel.job` - Array job for remaining genomes

**Local:**
- `02_compleasm_first.sh` - Process first genome to download lineage database
- `02_compleasm_parallel.sh` - GNU parallel for remaining genomes

### Step 8A: Partition Model Selection

**SLURM:**
- `08a_partition_search.job` - IQ-TREE partition model search with TESTMERGEONLY

**PBS:**
- `08a_partition_search.job` - IQ-TREE partition model search with TESTMERGEONLY

**Local:**
- `08a_partition_search.sh` - IQ-TREE partition model search with TESTMERGEONLY

### Step 8C: Individual Gene Trees

**SLURM:**
- `08c_gene_trees_array.job` - Array job for parallel gene tree estimation

**PBS:**
- `08c_gene_trees_array.job` - Array job for parallel gene tree estimation

**Local:**
- `08c_gene_trees_parallel.sh` - GNU parallel for gene tree estimation
- `08c_gene_trees_serial.sh` - Serial processing (for debugging/limited resources)

## Placeholders

Templates contain placeholders that must be replaced with user-specific values:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `TOTAL_THREADS` | Total CPU cores available | `64` |
| `THREADS_PER_JOB` | Threads per concurrent job | `16` |
| `NUM_GENOMES` | Number of genomes in analysis | `20` |
| `NUM_LOCI` | Number of loci/alignments | `2795` |
| `LINEAGE` | BUSCO lineage dataset | `insecta_odb10` |
| `MODEL_SET` | Comma-separated substitution models | `LG,WAG,JTT,Q.pfam` |

## Usage

### For Claude (LLM)

When a user requests scripts for a specific computing environment:

1. **Read the appropriate template** using the Read tool
2. **Replace placeholders** with user-specified values
3. **Present the customized script** to the user
4. **Provide setup instructions** (e.g., how many genomes, how to calculate thread allocation)

Example:
```python
# Read template
template = Read("templates/slurm/02_compleasm_first.job")

# Replace placeholders
script = template.replace("TOTAL_THREADS", "64")
script = script.replace("LINEAGE", "insecta_odb10")

# Present to user
print(script)
```

### For Users

Templates are not meant to be used directly. Instead:

1. Follow the workflow in `SKILL.md`
2. Answer Claude's questions about your setup
3. Claude will fetch the appropriate template and customize it for you
4. Copy the customized script Claude provides

## Benefits of This Structure

1. **Reduced token usage**: Claude only reads templates when needed
2. **Easier maintenance**: Update one template file instead of multiple locations in SKILL.md
3. **Consistency**: All users get the same base template structure
4. **Clarity**: Separate files are easier to review than inline code
5. **Extensibility**: Easy to add new templates for additional tools or variants

## Adding New Templates

When adding new templates:

1. **Follow naming convention**: `NN_descriptive_name[_variant].ext`
2. **Include clear comments**: Explain what the script does
3. **Use consistent placeholders**: Match existing placeholder names
4. **Test thoroughly**: Ensure placeholders are complete and correct
5. **Update this README**: Add the new template to the "Available Templates" section
6. **Update SKILL.md**: Reference the new template in the appropriate workflow step
