---
title: Text Formatting Decision Documentation
created: '2025-10-06'
updated: '2025-10-06'
author: Steve-Merlin-Projecct
type: archived
status: archived
tags:
- text
- formatting
- decision
- '2025'
---

# Text Formatting Decision Documentation
**Date:** September 5, 2025  
**Context:** Copywriting Evaluator System PRD Development

## Decision Made: Plain Text Storage with Application-Time Formatting

### Final Decision
Store all sentence text as **plain text** in the database (status quo). Apply italics formatting during document assembly process in the document generation modules.

### Background Discussion

#### Initial Problem
Need to italicize specific publication names in sentences during the Copywriting Evaluator System processing:
- "Edify"
- "Together We Thrive" 
- "Legacy in Action"
- "Edify Unfiltered"
- "CroneCast"
- "The Well Endowed Podcast"

#### Options Considered

##### Option 1: JSON Metadata Storage
**Structure:**
```json
{
  "text": "I contributed to Edify and Together We Thrive publications",
  "formatting": [
    {"start": 16, "end": 21, "type": "italic", "content": "Edify"},
    {"start": 26, "end": 45, "type": "italic", "content": "Together We Thrive"}
  ]
}
```

**Advantages:**
- ✅ Native PostgreSQL JSONB support with indexing
- ✅ Flexible for future formatting types (bold, colors, etc.)
- ✅ No parsing conflicts with variable content `{target_job_title}`
- ✅ Works with multiple output formats (.docx, email, web)
- ✅ Professional, scalable approach

**Disadvantages:**
- ❌ More complex to read raw database content
- ❌ Requires JSON parsing in application code
- ❌ Less human-readable in database queries

##### Option 2: Custom Markers
**Examples:**
- `[[italic:Edify]]` (double brackets)
- `{{style:italic:Edify}}` (prefixed to distinguish from variables)
- `<italic>Edify</italic>` (XML-style tags)

**Advantages:**
- ✅ Human-readable in database
- ✅ Simple regex parsing
- ✅ Clear distinction from variable content `{target_job_title}`

**Disadvantages:**
- ❌ Limited flexibility for complex formatting
- ❌ String manipulation required for changes
- ❌ Potential parsing complexity as formatting grows

##### Option 3: HTML Tags (Rejected)
`<i>Edify</i>` format - rejected because HTML tags don't work directly in .docx files.

### Decision Rationale

**Chosen: Plain text storage + application-time formatting**

Reasons:
1. **Simplicity:** Keep database text clean and readable
2. **Separation of concerns:** Formatting logic belongs in presentation layer
3. **Maintainability:** Easy to modify formatting rules without database changes
4. **Flexibility:** Can apply different formatting for different output channels
5. **Performance:** No additional database complexity or parsing overhead

### Implementation Details

#### Database Storage
- Continue storing sentences as plain text in existing format
- No additional formatting columns needed

#### Implementation Location
**Target file:** `modules/content/document_generation/document_generator.py` or `modules/content/document_generation/template_engine.py`

Based on code analysis:
- `document_generator.py` - Main orchestration for document creation
- `template_engine.py` - Handles text processing and variable substitution

**Recommended approach:** Add italics processing to `template_engine.py` during the text substitution phase, since it already processes paragraph text.

#### Formatting Logic
Create a function to detect publication names and apply italics formatting:
```python
def apply_publication_formatting(text):
    publications = [
        "Edify", "Together We Thrive", "Legacy in Action", 
        "Edify Unfiltered", "CroneCast", "The Well Endowed Podcast"
    ]
    # Apply italics during .docx generation
```

### Future Considerations

This decision can be revisited if:
1. Formatting requirements become significantly more complex
2. Multiple formatting types need to be stored persistently
3. Performance becomes an issue with application-time processing
4. Cross-platform formatting consistency becomes critical

### Related PRD Updates

This decision affects the Style Guide stage in the Copywriting Evaluator System:
- Stage 3: Style guide processing (Canadian Press spelling + publication italics)
- Implementation will be in document generation layer, not database storage
- Simplified tracking: only `style_guide_status` and `style_guide_date` columns needed