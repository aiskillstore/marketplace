# Paper2Video: Presentation Video Generation

## Overview

Paper2Video generates presentation videos from LaTeX source, transforming academic papers into dynamic video presentations. The system processes papers through multiple specialized modules to create professional presentations containing slides, narration, and optional talking-head videos.

## Core Components

### 1. Slide Generation Module
- Extracts key content from paper structure
- Creates visually appealing presentation slides
- Organizes content in logical flow
- Includes figures, tables, and equations
- Optimizes text density for readability

### 2. Subtitle Generation Module
- Generates natural speaking scripts
- Synchronizes text with slide transitions
- Creates speaker notes and duration control
- Supports multiple languages
- Optimizes for speech synthesis

### 3. Speech Synthesis Module
- Converts subtitles to natural human voice
- Supports multiple voices and accents
- Controls speech rate and emphasis
- Generates video audio tracks
- Handles technical terminology

### 4. Cursor Movement Module
- Simulates presenter cursor movements
- Highlights key points on slides
- Guides audience attention
- Creates natural speech flow
- Synchronizes with narration

### 5. Talking-Head Video Generation (Optional)
- Uses Hallo2 to generate realistic presenter videos
- Achieves lip sync with generated audio
- Requires reference image or video
- GPU-intensive (minimum NVIDIA A6000 48GB)
- Enhances presentation presence

## Usage

### Basic Video Generation (Without Talking-Head)

```bash
python pipeline_light.py \
  --model_name_t gpt-4.1 \
  --model_name_v gpt-4.1 \
  --result_dir /path/to/output \
  --paper_latex_root /path/to/paper
```

### Full Video Generation (With Talking-Head)

```bash
python pipeline_all.py \
  --input-dir "path/to/papers" \
  --output-dir "path/to/output" \
  --model-choice 1 \
  --enable-talking-head
```

### Parameters

**Model Configuration:**
- `--model_name_t`: Model for text/subtitle generation (default: gpt-4.1)
- `--model_name_v`: Model for visual/slide generation (default: gpt-4.1)
- `--model-choice`: Preset model configuration (1=GPT-4, 2=GPT-4.1)

**Input/Output:**
- `--paper_latex_root`: Root directory of LaTeX paper source
- `--result_dir` or `--output-dir`: Output directory for generated videos
- `--input-dir`: Directory containing multiple papers to process

**Video Options:**
- `--enable-talking-head`: Enable talking-head video generation (requires GPU)
- `--video-duration`: Target video duration in seconds (default: auto-calculated)
- `--slides-per-minute`: Control presentation pace (default: 2-3 slides per minute)
- `--voice`: Voice selection for speech synthesis

**Quality Settings:**
- `--video-resolution`: Output resolution (default: 1920x1080)
- `--video-fps`: Frame rate (default: 30)
- `--audio-quality`: Audio bitrate (default: 192kbps)

## Input Requirements

### LaTeX Source Structure
```
paper_directory/
├── main.tex              # Main paper file
├── sections/             # Section files (if split)
│   ├── introduction.tex
│   ├── methods.tex
│   └── results.tex
├── figures/              # Image files
│   ├── fig1.pdf
│   ├── fig2.png
│   └── ...
├── tables/               # Table files
└── bibliography.bib      # References
```

### Required Elements
- Valid LaTeX source that compiles successfully
- Complete section structure (abstract, introduction, methods, results, conclusions)
- High-quality images (vector formats preferred)
- Complete references

### Optional Elements
- Author photos for talking-head generation
- Custom slide templates
- Background music or sound effects
- Institutional branding assets

## Output Structure

```
output/paper_name/video/
├── final_video.mp4           # Complete presentation video
├── slides/                   # Generated slide images
│   ├── slide_001.png
│   ├── slide_002.png
│   └── ...
├── audio/                    # Audio components
│   ├── narration.mp3         # Speech synthesis output
│   └── background.mp3        # Optional background audio
├── subtitles/                # Subtitle files
│   ├── subtitles.srt         # Standard subtitle format
│   └── subtitles.vtt         # WebVTT format
├── script/                   # Speaking scripts
│   ├── full_script.txt       # Complete narration text
│   └── slide_notes.json      # Per-slide notes
└── metadata/                 # Video metadata
    ├── timings.json          # Slide timing information
    └── video_info.json       # Video properties
```

## Video Generation Process

### Phase 1: Content Analysis
1. Parse LaTeX source structure
2. Extract core concepts and research results
3. Identify important figures and equations
4. Determine logical presentation flow

### Phase 2: Slide Creation
1. Design slide layouts based on content
2. Distribute content across appropriate number of slides
3. Integrate figures and visual elements
4. Apply unified styling and branding

### Phase 3: Script Generation
1. Write natural presentation narration
2. Match script segments to slide timings
3. Add transitions and emphasis
4. Optimize for speech synthesis

### Phase 4: Audio Production
1. Generate voice from script
2. Add emphasis and rhythm control
3. Reserve pauses for slide transitions
4. Mix with optional background audio

### Phase 5: Video Assembly
1. Combine slides with timing information
2. Synchronize audio tracks
3. Add cursor movements and highlights
4. Generate talking-head video (if enabled)
5. Render final video file

## Customization Options

### Presentation Styles
- **Academic**: Formal, detailed, comprehensive
- **Conference**: Focused on key findings, faster pace
- **Public**: Concise language, engaging narrative
- **Tutorial**: Step-by-step explanations, teaching-focused

### Voice Configuration
Available voice options (via speech synthesis):
- Multiple languages and accents
- Male/female voice selection
- Speech rate adjustment
- Pitch and timbre customization

### Visual Themes
- Institutional brand colors
- Conference template matching
- Custom backgrounds and fonts
- Dark mode presentations

## Quality Assessment

### Content Quality Metrics
- **Completeness**: Coverage of paper content
- **Clarity**: Explanation quality and coherence
- **Fluidity**: Logical progression of ideas
- **Engagement**: Visual appeal and pacing

### Technical Quality Metrics
- **Audio Quality**: Voice clarity and naturalness
- **Video Quality**: Resolution and encoding
- **Synchronization**: Audio-visual alignment
- **Timing**: Appropriate slide dwell time

## Advanced Features

### Multi-language Support
- Generate presentations in multiple languages
- Auto-translate scripts
- Select corresponding language voices
- Cultural adaptation of presentation style

### Talking-Head Generation with Hallo2
Requirements:
- NVIDIA A6000 GPU (minimum 48GB)
- Reference image or short video of presenter
- Additional processing time (2-3x increase)

Benefits:
- More engaging presentations
- Professional presenter image
- Natural gestures and expressions
- High lip-sync accuracy

### Interactive Elements
- Embed clickable links
- Navigation menus
- Section markers
- Supplementary material links

## Best Practices

### Input Preparation
1. **Clean LaTeX source**: Remove unnecessary comments and redundant content
2. **High-quality figures**: Use vector formats whenever possible
3. **Clear structure**: Well-organized sections and subsections
4. **Complete content**: Include all necessary files and references

### Model Selection
- **Text generation (model_name_t)**: Use GPT-4.1 for best script quality
- **Visual generation (model_name_v)**: Use GPT-4.1 for optimal slide design
- For faster processing with acceptable quality: Use GPT-3.5-turbo

### Video Optimization
1. **Target duration**: 10-15 minutes for conference talks, 30-45 minutes for detailed reports
2. **Pacing**: 2-3 slides per minute for technical content
3. **Resolution**: Standard 1920x1080, high quality 3840x2160
4. **Audio**: Minimum 192kbps for clear voice

### Quality Check
Before finalizing:
1. Watch entire video to ensure content accuracy
2. Check audio synchronization with slides
3. Verify image quality and readability
4. Test subtitle accuracy and timing
5. Verify cursor movements are natural

## Performance Considerations

### Processing Time
- **Without talking-head**: 10-30 minutes per paper (depending on length)
- **With talking-head**: 30-120 minutes per paper
- **Factors**: Paper length, number of images, model speed, GPU availability

### Resource Requirements
- **CPU**: Multi-core recommended for parallel processing
- **RAM**: Minimum 16GB, 32GB recommended for large papers
- **GPU**: Optional for standard version, required for talking-head version (A6000 48GB)
- **Storage**: 1-5GB per video depending on length and quality

## Troubleshooting

### Common Issues

**1. LaTeX Parsing Errors**
- Ensure LaTeX source compiles successfully
- Check for special packages or custom commands
- Verify all referenced files exist

**2. Speech Synthesis Issues**
- Check audio quality settings
- Verify text format is correct
- Try different voice options

**3. Video Rendering Failures**
- Check available disk space
- Verify all dependencies are installed
- Check error logs for specific issues

**4. Talking-Head Generation Errors**
- Confirm GPU memory (requires 48GB)
- Check CUDA drivers are up to date
- Verify reference image quality and format

## Integration with Other Components

Combine Paper2Video with:
- **Paper2Web**: Embed videos in generated websites
- **Paper2Poster**: Use matching visual styles
- **AutoPR**: Create promotional clips from full videos
