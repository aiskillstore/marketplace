# LabArchives Third-Party Integrations

## Overview

LabArchives integrates with numerous scientific software platforms to streamline research workflows. This document covers programmatic integration methods, automation strategies, and best practices for each supported platform.

## Integration Categories

### 1. Protocol Management

#### Protocols.io Integration

Export protocols directly from Protocols.io to LabArchives notebooks.

**Use Cases:**
- Standardize experimental procedures in lab notebooks
- Maintain version control for protocols
- Associate protocols with experimental results

**Setup:**
1. Enable Protocols.io integration in LabArchives settings
2. Authenticate with your Protocols.io account
3. Browse and select protocols to export

**Programmatic Approach:**
```python
# Export Protocols.io protocol as HTML/PDF
# Then upload to LabArchives via API

def import_protocol_to_labarchives(client, uid, nbid, protocol_id):
    """Import Protocols.io protocol to LabArchives entry"""
    # 1. Fetch protocol from Protocols.io API
    protocol_data = fetch_protocol_from_protocolsio(protocol_id)

    # 2. Create new entry in LabArchives
    entry_params = {
        'uid': uid,
        'nbid': nbid,
        'title': f"Protocol: {protocol_data['title']}",
        'content': protocol_data['html_content']
    }
    response = client.make_call('entries', 'create_entry', params=entry_params)

    # 3. Add protocol metadata as comment
    entry_id = extract_entry_id(response)
    comment_params = {
        'uid': uid,
        'nbid': nbid,
        'entry_id': entry_id,
        'comment': f"Protocols.io ID: {protocol_id}<br>Version: {protocol_data['version']}"
    }
    client.make_call('entries', 'create_comment', params=comment_params)

    return entry_id
```

**Last Updated:** September 22, 2025

### 2. Data Analysis Tools

#### GraphPad Prism Integration (Version 8+)

Export analyses, graphs, and illustrations directly from Prism to LabArchives.

**Use Cases:**
- Archive statistical analyses alongside raw data
- Document graph generation processes for publication
- Maintain analysis audit trails for compliance

**Setup:**
1. Install GraphPad Prism 8 or higher
2. Configure LabArchives connection in Prism preferences
3. Use "Export to LabArchives" option from "File" menu

**Programmatic Approach:**
```python
# Upload Prism files to LabArchives via API

def upload_prism_analysis(client, uid, nbid, entry_id, prism_file_path):
    """Upload GraphPad Prism file to LabArchives entry"""
    import requests

    url = f'{client.api_url}/entries/upload_attachment'
    files = {'file': open(prism_file_path, 'rb')}
    params = {
        'uid': uid,
        'nbid': nbid,
        'entry_id': entry_id,
        'filename': os.path.basename(prism_file_path),
        'access_key_id': client.access_key_id,
        'access_password': client.access_password
    }

    response = requests.post(url, files=files, data=params)
    return response
```

**Supported File Types:**
- .pzfx (Prism project files)
- .png, .jpg, .pdf (exported graphs)
- .xlsx (exported data tables)

**Last Updated:** September 8, 2025

### 3. Molecular Biology and Bioinformatics

#### SnapGene Integration

Direct integration for molecular biology workflows, plasmid maps, and sequence analysis.

**Use Cases:**
- Document cloning strategies
- Archive plasmid maps with experimental records
- Associate sequences with experimental results

**Setup:**
1. Install SnapGene software
2. Enable LabArchives export in SnapGene preferences
3. Use "Send to LabArchives" feature

**File Format Support:**
- .dna (SnapGene files)
- .gb, .gbk (GenBank format)
- .fasta (sequence files)
- .png, .pdf (plasmid map exports)

**Programmatic Workflow:**
```python
def upload_snapgene_file(client, uid, nbid, entry_id, snapgene_file):
    """Upload SnapGene file with preview image"""
    # Upload main SnapGene file
    upload_attachment(client, uid, nbid, entry_id, snapgene_file)

    # Generate and upload preview (requires SnapGene CLI)
    preview_png = generate_snapgene_preview(snapgene_file)
    upload_attachment(client, uid, nbid, entry_id, preview_png)
```

#### Geneious Integration

Bioinformatics analysis export from Geneious to LabArchives.

**Use Cases:**
- Archive sequence alignments and phylogenetic trees
- Document NGS analysis pipelines
- Associate bioinformatics workflows with wet lab experiments

**Supported Export Content:**
- Sequence alignments
- Phylogenetic trees
- Assembly reports
- Variant calling results

**File Formats:**
- .geneious (Geneious documents)
- .fasta, .fastq (sequence data)
- .bam, .sam (alignment files)
- .vcf (variant files)

### 4. Computational Notebooks

#### Jupyter Integration

Embed Jupyter notebooks as LabArchives entries for reproducible computational research.

**Use Cases:**
- Document data analysis workflows
- Archive computational experiments
- Associate code, results, and narrative explanations

**Workflow:**

```python
def export_jupyter_to_labarchives(notebook_path, client, uid, nbid):
    """Export Jupyter notebook to LabArchives"""
    import nbformat
    from nbconvert import HTMLExporter

    # Load notebook
    with open(notebook_path, 'r') as f:
        nb = nbformat.read(f, as_version=4)

    # Convert to HTML
    html_exporter = HTMLExporter()
    html_exporter.template_name = 'classic'
    (body, resources) = html_exporter.from_notebook_node(nb)

    # Create entry in LabArchives
    entry_params = {
        'uid': uid,
        'nbid': nbid,
        'title': f"Jupyter Notebook: {os.path.basename(notebook_path)}",
        'content': body
    }
    response = client.make_call('entries', 'create_entry', params=entry_params)

    # Upload original .ipynb file as attachment
    entry_id = extract_entry_id(response)
    upload_attachment(client, uid, nbid, entry_id, notebook_path)

    return entry_id
```

**Best Practices:**
- Include outputs when exporting (run all cells before exporting)
- Include environment.yml or requirements.txt as attachments
- Add execution timestamps and system info in comments

### 5. Clinical Research

#### REDCap Integration

Clinical data capture integration with LabArchives for research compliance and audit trails.

**Use Cases:**
- Associate clinical data collection with research notebooks
- Maintain audit trails required for regulatory compliance
- Document clinical trial protocols and amendments

**Integration Methods:**
- Export data to LabArchives entries via REDCap API
- Implement automated data synchronization for longitudinal studies
- HIPAA-compliant data handling

**Workflow Example:**
```python
def sync_redcap_to_labarchives(redcap_api_token, client, uid, nbid):
    """Sync REDCap data to LabArchives"""
    # Fetch REDCap data
    redcap_data = fetch_redcap_data(redcap_api_token)

    # Create LabArchives entry
    entry_params = {
        'uid': uid,
        'nbid': nbid,
        'title': f"REDCap Data Export {datetime.now().strftime('%Y-%m-%d')}",
        'content': format_redcap_data_html(redcap_data)
    }
    response = client.make_call('entries', 'create_entry', params=entry_params)

    return response
```

**Compliance Features:**
- 21 CFR Part 11 compliant
- Audit trail maintenance
- Data integrity validation

### 6. Research Publishing

#### Qeios Integration

Research publishing platform integration for preprints and peer review.

**Use Cases:**
- Export research findings to preprint servers
- Document publishing workflows
- Link published articles to lab notebooks

**Workflow:**
- Export formatted entries from LabArchives
- Submit to Qeios platform
- Maintain bidirectional links between notebooks and publications

#### SciSpace Integration

Literature management and citation integration.

**Use Cases:**
- Associate references with experimental steps
- Maintain literature reviews in notebooks
- Generate reference lists for reports

**Features:**
- Import citations from SciSpace to LabArchives
- PDF annotation sync
- Reference management

## Integration Authentication (OAuth)

LabArchives now uses OAuth 2.0 for new third-party integrations.

**OAuth Flow for App Developers:**

```python
def labarchives_oauth_flow(client_id, client_secret, redirect_uri):
    """Implement OAuth 2.0 flow for LabArchives integration"""
    import requests

    # Step 1: Get authorization code
    auth_url = "https://mynotebook.labarchives.com/oauth/authorize"
    auth_params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'read write'
    }
    # User visits auth_url and grants permission

    # Step 2: Exchange authorization code for access token
    token_url = "https://mynotebook.labarchives.com/oauth/token"
    token_params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
        'code': authorization_code  # from redirect
    }

    response = requests.post(token_url, data=token_params)
    tokens = response.json()

    return tokens['access_token'], tokens['refresh_token']
```

**Benefits of OAuth:**
- More secure than API keys
- Fine-grained permission control
- Token refresh mechanism for long-running integrations
- Revocable access permissions

## Custom Integration Development

### Generic Workflow

For tools not yet officially supported, custom integrations can be developed:

1. **Export data** from source application (via API or file export)
2. **Transform format** to HTML or supported file types
3. **Authenticate** using LabArchives API
4. **Create entries** or upload attachments
5. **Add metadata** via comments for traceability

### Example: Custom Integration Template

```python
class LabArchivesIntegration:
    """Custom LabArchives integration template"""

    def __init__(self, config_path):
        self.client = self._init_client(config_path)
        self.uid = self._authenticate()

    def _init_client(self, config_path):
        """Initialize LabArchives client"""
        with open(config_path) as f:
            config = yaml.safe_load(f)
        return Client(config['api_url'],
                     config['access_key_id'],
                     config['access_password'])

    def _authenticate(self):
        """Get user ID"""
        # See authentication_guide.md for implementation
        pass

    def export_data(self, source_data, nbid, title):
        """Export data to LabArchives"""
        # Transform data to HTML
        html_content = self._transform_to_html(source_data)

        # Create entry
        params = {
            'uid': self.uid,
            'nbid': nbid,
            'title': title,
            'content': html_content
        }
        response = self.client.make_call('entries', 'create_entry', params=params)

        return extract_entry_id(response)

    def _transform_to_html(self, data):
        """Transform data to HTML format"""
        # Custom transformation logic
        pass
```

## Integration Best Practices

1. **Version Control:** Track software versions that generated data.
2. **Metadata Preservation:** Include timestamps, user info, and processing parameters.
3. **File Format Standards:** Use open formats where possible (CSV, JSON, HTML).
4. **Bulk Operations:** Implement rate limiting for batch uploads.
5. **Error Handling:** Implement retry logic with exponential backoff.
6. **Audit Trails:** Log all API operations for compliance.
7. **Testing:** Validate integrations in test notebooks before production use.

## Integration Troubleshooting

### Common Issues

**Integration not appearing in LabArchives:**
- Verify administrator has enabled the integration
- If using OAuth, check OAuth permissions
- Ensure software version compatibility

**File upload failures:**
- Verify file size limits (typically 2GB per file)
- Check file format compatibility
- Ensure adequate storage quota

**Authentication errors:**
- Verify API credentials are current
- Check if integration-specific tokens have expired
- Confirm user has necessary permissions

### Integration Support

For integration-specific issues:
- Consult software vendor documentation (e.g., GraphPad, Protocols.io)
- Contact LabArchives support: support@labarchives.com
- Visit LabArchives knowledge base: help.labarchives.com

## Future Integration Opportunities

Potential integrations for custom development:
- Electronic Data Capture (EDC) systems
- Laboratory Information Management Systems (LIMS)
- Instrument data systems (chromatography, spectroscopy)
- Cloud storage platforms (Box, Dropbox, Google Drive)
- Project management tools (Asana, Monday.com)
- Grant management systems

Contact LabArchives to discuss custom integration development and API partnership opportunities.
