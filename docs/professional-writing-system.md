# Professional Writing System for Marketing Content

**Version:** 1.0.0

**Branch:** task/02-marketing-content
**Purpose:** Generate high-quality, job-specific seed sentences for Marketing Automation Manager and related positions

---

## Overview

This system creates professional-quality resume and cover letter sentences tailored to specific job titles. It combines:

1. **User personal content** (achievements, experience, skills)
2. **Target job analysis** (industry standards, required competencies)
3. **Professional writing expertise** (tone, style, Canadian standards)
4. **AI-powered variation generation** (Gemini API for scaling)
5. **Quality evaluation pipeline** (5-stage approval process)

### Design Philosophy: Wide Funnel → Strict Filtering

**Seed Generation Strategy:**
The seed sentences are intentionally experimental and varied. The goal at this stage is NOT to maintain a consistent brand voice - it's to create diverse, high-quality content that maximizes creative range. This allows the variation generation phase to experiment more widely.

**Filtering Pipeline:**
Consistency and context-appropriateness emerge through rigorous downstream filtering:
- **Variation Phase:** Gemini generates 7 variations per seed (widens the pool)
- **Truthfulness Phase:** Validates factual accuracy against source materials
- **Keyword Phase:** Filters for job-specific relevance
- **Tone Analysis Phase:** Matches tone to specific contexts

This architecture ensures the right sentence is available at the right time, rather than constraining creative generation upfront.

---

## Architecture

### Core Components

#### 1. **Professional Writing Agent**
- **Location:** `.claude/agents/professional-writer.md`
- **Model:** Claude Opus 4 (claude-opus-4-20250514)
- **Specialization:** Elite wordsmith for Canadian job applications
- **Disabled Tools:** All coding, linting, system architecture tools
- **Enabled Tools:** Text formatting, semantic analysis, language quality

**Key Capabilities:**
- Lexical prosody for Canadian English
- Narrative tension in sentence construction
- Marketing psychology and persuasion
- Professional appropriateness by industry

#### 2. **Slash Command: `/copywriter`**
- **Location:** `.claude/commands/copywriter.md`
- **Usage:** `/copywriter [task description]`
- **Invokes:** Professional Writing Agent (Opus model)
- **Input:** Task description + user source materials
- **Output:** Varies by task (seed sentences, reviews, rewrites, etc.)

#### 3. **Sentence Variation Generator**
- **Location:** `modules/content/sentence_variation_generator.py`
- **Model:** Gemini 2.0 Flash Experimental (free tier)
- **Purpose:** Generate 7 variations per seed sentence
- **API:** Flask blueprint at `/api/sentence-variations/`

#### 4. **User Content System**
- **Source Materials:** `user_content/source_materials/`
- **Target Jobs:** `user_content/target_jobs/`
- **Privacy:** All personal content in .gitignore

---

## Folder Structure

```
user_content/
├── source_materials/              # Your personal background files
│   ├── README.md                  # Instructions for what to include
│   ├── resume_current.pdf         # Your files (gitignored)
│   ├── work_history.md
│   └── achievements.txt
│
└── target_jobs/                   # Auto-generated job folders
    ├── marketing-automation-manager/
    │   ├── README.md              # Job-specific documentation
    │   ├── job_config.json        # Salary, location, preferences
    │   ├── seed_sentences/        # Original seeds (gitignored)
    │   ├── generated_variations/  # Gemini variations (gitignored)
    │   └── reframed_context/      # Job-specific framing (gitignored)
    │
    ├── marketing-manager/
    └── digital-marketing-manager/
```

---

## Workflow

### Phase 1: Setup (One-time)

1. **Add your materials:**
   ```bash
   # Drop your files into:
   user_content/source_materials/
   ```

   Include:
   - Current resume/CV
   - Work history details
   - Achievement lists with metrics
   - Certifications
   - Personal career statement

2. **Create target job folders:**
   ```bash
   python tools/setup_target_jobs.py
   ```

   This reads your job preferences from the database and creates organized folders for each target position.

### Phase 2: Seed Generation (Per Job)

3. **Invoke the copywriter:**
   ```
   /copywriter Write seed sentences for Marketing Automation Manager
   ```

   The Professional Copywriter will:
   - Read ALL your source materials
   - Analyze the target job requirements
   - Reframe your experiences for that role
   - Create 15-20 high-quality seed sentences
   - Output structured JSON with metadata

### Phase 3: Variation Generation

4. **Generate variations via API:**

   **Option A: Using Python directly**
   ```python
   from modules.content.sentence_variation_generator import SentenceVariationGenerator

   generator = SentenceVariationGenerator()
   result = generator.generate_variations(
       seed_sentences=seeds,
       variations_per_seed=7,
       target_position="Marketing Automation Manager"
   )
   ```

   **Option B: Using Flask API**
   ```bash
   curl -X POST http://localhost:5000/api/sentence-variations/generate \
     -H "Content-Type: application/json" \
     -d @seeds.json
   ```

5. **Download CSV:**
   ```bash
   # Add output_format: "csv" to get downloadable CSV
   curl -X POST http://localhost:5000/api/sentence-variations/generate \
     -H "Content-Type: application/json" \
     -d '{"seed_sentences": [...], "output_format": "csv"}' \
     -o variations.csv
   ```

### Phase 4: Evaluation

6. **Upload to pipeline:**
   - Import CSV via existing `csv_processor.py`
   - Automatic processing through 5 stages:
     1. Keyword Filter
     2. Truthfulness (Gemini)
     3. Canadian Spelling
     4. Tone Analysis (Gemini)
     5. Skill Analysis (Gemini)

7. **Approved sentences** ready for document generation

---

## Target Jobs

### Current Configuration

Based on user preferences, the system supports:

| Job Title | Salary Range | Location | Work Arrangement |
|-----------|--------------|----------|------------------|
| Marketing Automation Manager | $85K - $120K | Alberta | Hybrid |
| Marketing Manager | $75K - $110K | Edmonton | Hybrid |
| Digital Marketing Manager | $75K - $110K | Remote | Remote |

### Adding New Target Jobs

Update in database:
```sql
INSERT INTO user_job_search_preferences (
    user_id, job_title_target, salary_minimum, salary_maximum,
    work_arrangement_preference, location_preference, package_name
) VALUES (...);
```

Then re-run:
```bash
python tools/setup_target_jobs.py
```

---

## Writing Standards

### Tone Categories

- **Confident** (40%): Shows ownership without arrogance
- **Warm** (20%): Friendly, approachable
- **Bold** (15%): Direct, impact-focused
- **Curious** (10%): Emphasizes learning
- **Insightful** (10%): Offers new perspectives
- **Storytelling** (5%): Narrative elements

### Sentence Categories

**Resume:**
- Leadership/Achievement (3-4 sentences)
- Technical/Skills (3-4 sentences)
- Collaboration/Team (2-3 sentences)
- Results/Impact (1-2 sentences)

**Cover Letter:**
- Opening/Hook (2 sentences)
- Alignment/Fit (2-3 sentences)
- Achievement/Story (2 sentences)
- Closing/CTA (1 sentence)

### Quality Standards

Every sentence must:
- ✓ Based on actual user experiences
- ✓ Active voice, crisp syntax
- ✓ Free of clichés ("results-oriented", "team player")
- ✓ Canadian spelling
- ✓ Specific with metrics when appropriate
- ✓ Professional yet conversational
- ✓ Scannable and punchy

---

## API Reference

### Sentence Variation Endpoints

**Base URL:** `http://localhost:5000/api/sentence-variations`

#### `POST /generate`
Generate variations for seed sentences

**Request:**
```json
{
  "seed_sentences": [
    {
      "content_text": "Your sentence here",
      "tone": "Confident",
      "category": "Achievement",
      "intended_document": "resume",
      "position_label": "Marketing Automation Manager"
    }
  ],
  "variations_per_seed": 7,
  "target_position": "Marketing Automation Manager",
  "output_format": "json"
}
```

**Response:**
```json
{
  "success": true,
  "variations": [...],
  "stats": {
    "total_seeds": 15,
    "variations_per_seed": 7,
    "total_generated": 105,
    "successful_seeds": 15,
    "failed_seeds": 0
  }
}
```

#### `GET /health`
Check service status

#### `GET /example-request`
Get example request format

---

## Privacy & Security

### What's Protected

**Gitignored (NEVER committed):**
- `user_content/source_materials/*` (except README)
- `user_content/target_jobs/*/seed_sentences/*`
- `user_content/target_jobs/*/generated_variations/*`
- `user_content/target_jobs/*/reframed_context/*`

**Committed to repo:**
- Folder structure
- README files
- job_config.json files
- System code and agents

### Data Flow

1. **Local Only:** Source materials stay on your machine
2. **API Calls:** Only reframed sentence excerpts sent to Gemini for variation
3. **No Storage:** Gemini doesn't store your data (per their API terms)
4. **Database:** Final approved sentences stored locally in PostgreSQL

---

## Testing

### Test Variation Generator

```bash
python test_sentence_variation.py
```

Runs:
- Health check
- JSON output test
- CSV output test
- Saves results to `variation_results.json` and `variations_output.csv`

### Manual Testing

```bash
# 1. Start Flask server
python app_modular.py

# 2. Test health
curl http://localhost:5000/api/sentence-variations/health

# 3. Get example request
curl http://localhost:5000/api/sentence-variations/example-request

# 4. Generate variations
curl -X POST http://localhost:5000/api/sentence-variations/generate \
  -H "Content-Type: application/json" \
  -d @test_seeds.json
```

---

## Troubleshooting

### Issue: "GEMINI_API_KEY not found"
**Solution:** Add to `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

### Issue: "No source materials found"
**Solution:** Add files to `user_content/source_materials/`

### Issue: "Target job folder doesn't exist"
**Solution:** Run `python tools/setup_target_jobs.py`

### Issue: Database table not found
**Solution:** System uses defaults. Update schema or check `user_job_search_preferences` table exists.

---

## Next Steps

### Immediate
1. ✓ Add your background materials to `user_content/source_materials/`
2. ✓ Run `/copywriter Write seed sentences for Marketing Automation Manager`
3. ✓ Review written seeds
4. ✓ Generate variations
5. ✓ Import CSV to evaluation pipeline

### Future Enhancements
- Async batch processing for large seed lists
- Job tracking system for variation generation
- A/B testing framework for sentence performance
- Automatic reframing when new source materials added
- Integration with document generation templates

---

## File Manifest

### Created Files
```
.claude/agents/professional-writer.md          # Opus agent definition
.claude/commands/copywriter.md                 # Slash command
modules/content/sentence_variation_generator.py # Variation generator
modules/content/sentence_variation_api.py      # Flask API
tools/setup_target_jobs.py                     # Folder automation
test_sentence_variation.py                     # Test suite
user_content/                                  # User content folders
docs/professional-writing-system.md            # This document
```

### Modified Files
```
app_modular.py                                 # Added API blueprint
.gitignore                                     # Protected user content
```

---

## Support

For questions or issues:
1. Check this documentation
2. Review `.claude/agents/professional-writer.md` for writing guidelines
3. Check `/api/sentence-variations/example-request` for API format
4. Run test suite: `python test_sentence_variation.py`

---

**Ready to start!** Add your materials to `user_content/source_materials/` and run `/copywriter [task description]`

**Example tasks:**
- `/copywriter Write seed sentences for Marketing Automation Manager`
- `/copywriter Create compelling cover letter openings for tech startups`
- `/copywriter Review and improve: "Managed marketing campaigns"`
