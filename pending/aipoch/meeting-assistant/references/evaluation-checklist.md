# Meeting Assistant Evaluation Checklist

## Functional Testing

### 1. Timeline Organization
- [ ] Can summarize discussion points chronologically
- [ ] Can identify timestamp information
- [ ] Can mark conclusions and points of disagreement

### 2. Decision Extraction
- [ ] Can identify decision-making statements
- [ ] Can distinguish between decided items and items to be confirmed
- [ ] Can list decision items

### 3. Action Item Extraction
- [ ] Can extract task descriptions
- [ ] Can identify assignees
- [ ] Can identify deadlines
- [ ] Can distinguish between In Progress/To Start/Completed statuses

### 4. Template Usage
- [ ] Can use meeting_minutes_template.md
- [ ] Output format complies with template specifications
- [ ] Includes all required fields

## Quality Testing

### 1. Output Completeness
- [ ] Includes basic meeting information (Subject, Time, Participants, Recorder)
- [ ] Includes agenda list
- [ ] Includes timeline table
- [ ] Includes action items table

### 2. Information Accuracy
- [ ] Action items include assignees
- [ ] Action items include deadlines
- [ ] Clear distinction between decisions and items to be confirmed

### 3. Formatting Standards
- [ ] Markdown formatting is correct
- [ ] Table formatting is standardized
- [ ] Heading hierarchy is correct

## Security Testing

### 1. Path Access
- [ ] Does not access local files
- [ ] Does not access arbitrary URLs
- [ ] Does not write to local files

### 2. Data Processing
- [ ] Automatic masking of sensitive information
- [ ] Does not leak conversation content
- [ ] Releases memory upon completion of processing

## Use Case Testing

### Scenario 1: Meeting Minutes Organization
**Input**: Meeting records with timestamps
**Expectation**: Generate structured meeting minutes

### Scenario 2: Action Item Extraction
**Input**: Discussion text without timestamps
**Expectation**: Extract all action items and assignees

### Scenario 3: Decision Tracking
**Input**: Meeting records containing discussions and decisions
**Expectation**: List all decision items

## Acceptance Criteria

- [ ] All functional tests passed
- [ ] Template format is correct
- [ ] Security scan passed
- [ ] Consistent code style
- [ ] Complete documentation

## Known Limitations

1. Depends on the quality of the input text
2. May not be able to sort accurately without timestamps
3. Dialects or colloquial expressions may be identified inaccurately

## Improvement Suggestions

1. Can add speech-to-text integration
2. Can add multi-language support
3. Can add integration with task management tools (e.g., Todoist, Trello)