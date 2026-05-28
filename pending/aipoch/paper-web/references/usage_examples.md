# Usage Examples and Workflows

## Complete Workflow Example

### Example 1: Full Set of Conference Presentation Materials

**Scenario**: Prepare a complete set of websites, posters, and videos for an important conference presentation.

**User Request**: "I need to create a complete set of presentation materials for my NeurIPS paper submission, including a website, poster, and video demonstration."

**Workflow**:

```bash
# Step 1: Organize paper files
mkdir -p input/neurips2025_paper
cp main.tex input/neurips2025_paper/
cp -r figures/ input/neurips2025_paper/
cp -r tables/ input/neurips2025_paper/
cp bibliography.bib input/neurips2025_paper/

# Step 2: Generate all components
python pipeline_all.py \
  --input-dir input/neurips2025_paper \
  --output-dir output/ \
  --model-choice 1 \
  --generate-website \
  --generate-poster \
  --generate-video \
  --poster-width-inches 48 \
  --poster-height-inches 36 \
  --enable-logo-search

# Step 3: Check output results
ls -R output/neurips2025_paper/
# - website/index.html
# - poster/poster_final.pdf
# - video/final_video.mp4
```

**Output**:
- Interactive website showcasing the research
- 4'×3' conference poster (print-ready)
- 12-minute demonstration video
- Processing time: approximately 45 minutes (without talking-head)

---

### Example 2: Quick Webpage for Preprint

**Scenario**: Create an explorable homepage for a bioRxiv preprint.

**User Request**: "Convert my genomics preprint into an interactive website to accompany my bioRxiv submission."

**Workflow**:

```bash
# Use PDF input (when LaTeX source is not available)
python pipeline_all.py \
  --input-dir papers/genomics_preprint/ \
  --output-dir output/genomics_web/ \
  --model-choice 1 \
  --generate-website

# Deploy to GitHub Pages or personal server
cd output/genomics_web/website/
# Add links to bioRxiv paper, data repository, and code
# Upload to hosting service
```

**Tips**:
- Include links to bioRxiv DOI
- Add GitHub repository link
- Include data availability section
- Embed interactive visualizations if possible

---

### Example 3: Video Abstract for Journal Submission

**Scenario**: Create a video abstract for journals that encourage multimedia submissions.

**User Request**: "Generate a 5-minute video abstract for my Nature Communications submission."

**Workflow**:

```bash
# Generate concise video focusing on core findings
python pipeline_light.py \
  --model_name_t gpt-4.1 \
  --model_name_v gpt-4.1 \
  --result_dir output/video_abstract/ \
  --paper_latex_root papers/nature_comms/ \
  --video-duration 300 \
  --slides-per-minute 3

# Optional: Add custom intro/outro slides
# Optional: Add talking-head narration in introduction
```

**Output**:
- 5-minute video abstract
- Focus on visual results
- Clear, easy-to-understand narration
- Journal-ready format

---

### Example 4: Batch Generation for Multiple Paper Websites

**Scenario**: Create websites for multiple papers from a research group.

**User Request**: "Generate websites for all 5 papers published by our lab this year."

**Workflow**:

```bash
# Organize paper files
mkdir -p batch_input/
# Create subdirectories: paper1/, paper2/, paper3/, paper4/, paper5/
# Each directory contains its own LaTeX source

# Batch processing
python pipeline_all.py \
  --input-dir batch_input/ \
  --output-dir batch_output/ \
  --model-choice 1 \
  --generate-website \
  --enable-logo-search

# Generated content:
# batch_output/paper1/website/
# batch_output/paper2/website/
# batch_output/paper3/website/
# batch_output/paper4/website/
# batch_output/paper5/website/
```

**Best Practices**:
- Use consistent naming conventions
- Overnight processing for large batches
- Verify accuracy of each website
- Deploy to unified lab website

---

### Example 5: Virtual Conference Poster

**Scenario**: Create digital posters with interactive elements for virtual conferences.

**User Request**: "Create a poster for the virtual ISMB conference with clickable links to code and data."

**Workflow**:

```bash
# Generate poster with QR codes and links
python pipeline_all.py \
  --input-dir papers/ismb_submission/ \
  --output-dir output/ismb_poster/ \
  --model-choice 1 \
  --generate-poster \
  --poster-width-inches 48 \
  --poster-height-inches 36 \
  --enable-qr-codes

# Manually point QR codes to:
# - GitHub repository
# - Interactive results dashboard
# - Supplementary data
# - Video demonstration
```

**Digital Enhancements**:
- PDF with embedded hyperlinks
- High-resolution PNG for virtual platforms
- Standalone PDF with video download links

---

### Example 6: Promotional Video Clips

**Scenario**: Create short promotional videos for social media.

**User Request**: "Generate a 2-minute highlight video for our Cell paper posted on Twitter."

**Workflow**:

```bash
# Generate short and engaging video
python pipeline_light.py \
  --model_name_t gpt-4.1 \
  --model_name_v gpt-4.1 \
  --result_dir output/promo_video/ \
  --paper_latex_root papers/cell_paper/ \
  --video-duration 120 \
  --presentation-style public

# Post-processing:
# - Extract 30-second core clip for Twitter
# - Add subtitles for silent playback
# - Optimize file size for social media
```

**Social Media Optimization**:
- Instagram: square format (1:1)
- Twitter/LinkedIn: landscape format (16:9)
- TikTok/Stories: portrait format (9:16)
- Add text overlay for key findings

---

## Common Use Case Patterns

### Pattern 1: LaTeX Paper → Full Set of Materials

**Input**: LaTeX source with all assets
**Output**: Website + Poster + Video
**Time**: 45-90 minutes
**Use Case**: Major publications, conference presentations

```bash
python pipeline_all.py \
  --input-dir [latex_dir] \
  --output-dir [output_dir] \
  --model-choice 1 \
  --generate-website \
  --generate-poster \
  --generate-video
```

---

### Pattern 2: PDF → Interactive Website

**Input**: Published PDF paper
**Output**: Explorable website
**Time**: 15-30 minutes
**Use Case**: Post-publication promotion, preprint enhancement

```bash
python pipeline_all.py \
  --input-dir [pdf_dir] \
  --output-dir [output_dir] \
  --model-choice 1 \
  --generate-website
```

---

### Pattern 3: LaTeX → Conference Poster

**Input**: LaTeX paper
**Output**: Print-ready poster (customizable size)
**Time**: 10-20 minutes
**Use Case**: Conference poster sessions

```bash
python pipeline_all.py \
  --input-dir [latex_dir] \
  --output-dir [output_dir] \
  --model-choice 1 \
  --generate-poster \
  --poster-width-inches [width] \
  --poster-height-inches [height]
```

---

### Pattern 4: LaTeX → Presentation Video

**Input**: LaTeX paper
**Output**: Presentation video with narration
**Time**: 20-60 minutes (without talking-head)
**Use Case**: Video abstracts, online presentations, course materials

```bash
python pipeline_light.py \
  --model_name_t gpt-4.1 \
  --model_name_v gpt-4.1 \
  --result_dir [output_dir] \
  --paper_latex_root [latex_dir]
```

---

## Platform-Specific Output

### Twitter/X Promotional Content

The system automatically detects numerically named folders for Twitter optimization:

```bash
# Create Twitter-optimized content
mkdir -p input/001_twitter_post/
# System generates English promotional content
```

**Generated Output**:
- Short and engaging summaries
- Key figure highlights
- Hashtag recommendations
- Thread-ready format

---

### Xiaohongshu Content

For Chinese social media, use alphanumeric folder names:

```bash
# Create Xiaohongshu-optimized content
mkdir -p input/xhs_genomics/
# System generates Chinese promotional content
```

**Generated Output**:
- Chinese language content
- Platform-appropriate format
- Visual-first presentation
- Engagement optimization tips

---

## Troubleshooting Common Scenarios

### Scenario: Long Papers (>50 pages)

**Challenge**: Processing time and content selection
**Solutions**:
```bash
# Option 1: Focus on key sections
# Modify LaTeX, comment out non-core sections

# Option 2: Process in parts
# Generate website for overview
# Generate separate detailed videos for methods/results

# Option 3: Use faster model for first pass
# Check and regenerate key components with better model
```

---

### Scenario: Complex Mathematical Content

**Challenge**: Formulas may not render perfectly
**Solutions**:
- Use LaTeX input (not PDF) for optimal formula handling
- Verify formula accuracy in generated content
- Manually adjust complex formulas if needed
- Consider using screenshots for key formulas

---

### Scenario: Non-Standard Paper Structure

**Challenge**: Paper does not follow standard IMRAD format
**Solutions**:
- Provide custom section guidance in paper metadata
- Check generated structure and make adjustments
- Use more powerful model (GPT-4.1) for better adaptability
- Consider manual section labeling in LaTeX comments

---

### Scenario: API Budget Constraints

**Challenge**: Reduce costs while maintaining quality
**Solutions**:
```bash
# Use GPT-3.5-turbo for simpler papers
python pipeline_all.py \
  --input-dir [paper_dir] \
  --output-dir [output_dir] \
  --model-choice 3

# Only generate needed components
# Website only (cheapest)
# Poster only (moderate)
# Video without talking-head (moderate)
```

---

### Scenario: Urgent Deadline

**Challenge**: Need output quickly
**Solutions**:
```bash
# Parallel processing if multiple papers
# Use faster model (GPT-3.5-turbo)
# Generate only core components first
# Skip optional features (logo search, talking-head)

python pipeline_light.py \
  --model_name_t gpt-3.5-turbo \
  --model_name_v gpt-3.5-turbo \
  --result_dir [output_dir] \
  --paper_latex_root [latex_dir]
```

**Priority Order**:
1. Website (fastest, most versatile)
2. Poster (moderate speed, limited by print deadline)
3. Video (slowest, can be generated later)

---

## Quality Optimization Tips

### Website Best Practices
1. Use LaTeX input with all assets
2. Include high-resolution figures
3. Ensure paper has clear section structure
4. Enable logo search for professional appearance
5. Check and test all interactive elements

### Poster Best Practices
1. Provide high-resolution figures (300+ DPI)
2. Specify exact poster dimensions needed
3. Include institutional branding
4. Use professional color schemes
5. Test print thumbnail before full print

### Video Best Practices
1. Use LaTeX for clearest content extraction
2. Specify appropriate target duration
3. Review script before generating video
4. Choose appropriate presentation style
5. Test audio quality and pacing

### General Best Practices
1. Start with clean, well-organized LaTeX source
2. Use GPT-4 or GPT-4.1 for highest quality
3. Review all output before finalizing
4. Iterate on any components needing adjustments
5. Integrate components for unified presentation package
