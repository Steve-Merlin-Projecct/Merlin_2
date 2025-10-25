---
title: "Agent Template Conversion Guide"
type: guide
component: general
status: draft
tags: []
---

# Agent Template Conversion Guide

## Purpose

This guide provides detailed instructions for AI agents converting example resume templates into production-ready variable-based templates. These instructions are based on real issues discovered during testing.

---

## Core Principle: Replace EVERYTHING

**Critical Rule:** Every piece of content that could vary between users MUST be a variable.

### ❌ WRONG Approach
```
<<position_1>> | Contoso Bar and Grill | September 20XX – <<end_date_1>>
```
**Problem:** Company name and start date are hardcoded

### ✅ CORRECT Approach
```
<<position_1>> | <<company_1>> | <<start_date_1>> – <<end_date_1>>
```
**Result:** All content is replaceable

---

## Critical Checks: The "Would Any User Want This Different?" Test

Before finalizing a template, ask these questions for EVERY piece of text:

1. **Is this a specific person's name?** → Make it a variable
2. **Is this a specific company name?** → Make it a variable
3. **Is this a specific date?** → Make it a variable
4. **Is this a specific degree/certification?** → Make it a variable
5. **Is this a specific skill or achievement?** → Make it a variable
6. **Is this a specific location?** → Make it a variable
7. **Would different users want different text here?** → Make it a variable

### Examples of What MUST Be Variables

```
❌ "Contoso Bar and Grill" → ✅ <<company_1>>
❌ "September 20XX" → ✅ <<start_date_1>>
❌ "B.S. in Business Administration" → ✅ <<degree_1>>
❌ "June 20XX" → ✅ <<graduation_date_1>>
❌ "Grew customer base by 19%" → ✅ <<job_1_experience_2>>
❌ "Cornell University" → ✅ <<institution_1>>
❌ "New York" → ✅ <<city>>
```

---

## Variable Naming Standards

### 1. Use Consistent Numbering

**❌ WRONG:** Using the same number for different items
```
Job 1: <<position_1>> | <<company_1>>
Job 2: <<position_1>> | <<company_2>>  ← WRONG! Should be position_2
```

**✅ CORRECT:** Each item gets its own unique number
```
Job 1: <<position_1>> | <<company_1>>
Job 2: <<position_2>> | <<company_2>>  ← CORRECT!
```

### 2. Match Variable Sets Across Sections

If you have Job 1 with these variables:
```
<<position_1>>
<<company_1>>
<<start_date_1>>
<<end_date_1>>
<<job_1_experience_1>>
<<job_1_experience_2>>
<<job_1_experience_3>>
```

Then Job 2 MUST have the complete matching set:
```
<<position_2>>
<<company_2>>
<<start_date_2>>
<<end_date_2>>
<<job_2_experience_1>>
<<job_2_experience_2>>
<<job_2_experience_3>>
```

### 3. Use Semantic Names

**Good variable names:**
- `<<position_1>>` - Clear it's a job title
- `<<company_1>>` - Clear it's a company name
- `<<start_date_1>>` - Clear it's a start date
- `<<degree_1>>` - Clear it's a degree name
- `<<graduation_date_1>>` - Clear it's when they graduated

**Bad variable names:**
- `<<text_1>>` - Not clear what this is
- `<<data_1>>` - Too generic
- `<<thing_1>>` - Meaningless

---

## Common Mistakes to Avoid

### Mistake 1: Incomplete Variable Sets

**❌ WRONG:**
```
Education Entry 1:
<<degree_1>> | <<graduation_date_1>> | <<institution_1>>, <<institution_city_1>>

Education Entry 2:
<<degree_2>> | <<graduation_date_2>> | <<institution_1>>, <<institution_city_1>>
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                      WRONG! Should use institution_2 variables
```

**✅ CORRECT:**
```
Education Entry 1:
<<degree_1>> | <<graduation_date_1>> | <<institution_1>>, <<institution_city_1>>, <<institution_state_1>>

Education Entry 2:
<<degree_2>> | <<graduation_date_2>> | <<institution_2>>, <<institution_city_2>>, <<institution_state_2>>
```

### Mistake 2: Leaving Hardcoded Examples

**❌ WRONG:**
```
<<position_1>> | ABC Corporation | <<start_date_1>> – <<end_date_1>>
               ^^^^^^^^^^^^^^^^
               Hardcoded example company
```

**✅ CORRECT:**
```
<<position_1>> | <<company_1>> | <<start_date_1>> – <<end_date_1>>
```

### Mistake 3: Mixing Hardcoded and Variable Content

**❌ WRONG:**
```
<<job_1_experience_1>>
Increased sales by 15% through strategic initiatives
<<job_1_experience_3>>
```
**Problem:** Middle bullet is hardcoded (missing job_1_experience_2)

**✅ CORRECT:**
```
<<job_1_experience_1>>
<<job_1_experience_2>>
<<job_1_experience_3>>
```

### Mistake 4: Variable Duplication

**❌ WRONG:**
```
Restaurant Manager | ABC Restaurant | 2020 – 2023

Restaurant Supervisor | <<company_2>> | 2018 – 2020
^^^^^^^^^^^^^^^^^^^^^^
This should be <<position_2>>, not hardcoded!
```

**✅ CORRECT:**
```
<<position_1>> | <<company_1>> | <<start_date_1>> – <<end_date_1>>

<<position_2>> | <<company_2>> | <<start_date_2>> – <<end_date_2>>
```

---

## Section-by-Section Conversion Checklist

### Contact Information

**Variables Required:**
- ✅ `<<first_name>>`
- ✅ `<<last_name>>`
- ✅ `<<email>>`
- ✅ `<<phone>>`
- ✅ `<<city>>`
- ✅ `<<street_address>>` (optional)
- ✅ `<<zip_code>>` (optional)
- ✅ `<<linkedin_url>>` (optional)
- ⚠️ `<<state>>` - Consider if needed (not all regions use states/provinces)

**Check:** No hardcoded email addresses, phone numbers, or addresses remain

### Profile/Summary Section

**Variables Required:**
- ✅ `<<career_overview_1>>` through `<<career_overview_N>>`
- ✅ `<<professional_summary_1>>` through `<<professional_summary_N>>`
- ✅ `<<profile_header>>` (section header)

**Check:** No hardcoded personality traits, skills, or achievements remain

### Work Experience Section

**For EACH Job (Job 1, Job 2, etc.):**

Required variables:
- ✅ `<<position_N>>` - Job title
- ✅ `<<company_N>>` - Company name
- ✅ `<<start_date_N>>` - Start date
- ✅ `<<end_date_N>>` - End date or "Present"
- ✅ `<<job_city_N>>` - City (if shown)
- ✅ `<<job_state_N>>` - State (if shown)

Experience bullets:
- ✅ `<<job_N_experience_1>>`
- ✅ `<<job_N_experience_2>>`
- ✅ `<<job_N_experience_3>>`
- ✅ Continue numbering for all bullets

**Common template patterns:**
- 3 bullets for Job 1
- 4 bullets for Job 2
- Adjust based on template layout

**Check:**
- ❌ No company names remain (e.g., "Contoso", "ABC Corp")
- ❌ No dates remain (e.g., "2020", "September 20XX")
- ❌ No hardcoded achievement text remains
- ✅ Position_1 used ONLY in Job 1
- ✅ Position_2 used ONLY in Job 2

### Education Section

**For EACH Education Entry:**

Required variables:
- ✅ `<<degree_N>>` - Degree name (e.g., "Bachelor of Science")
- ✅ `<<major_N>>` or `<<minor_N>>` - Field of study (if shown)
- ✅ `<<institution_N>>` - School name
- ✅ `<<institution_city_N>>` - School city
- ✅ `<<institution_state_N>>` - School state/province
- ✅ `<<graduation_date_N>>` or `<<graduation_year_N>>` - When graduated

**Check:**
- ❌ No degree names remain (e.g., "B.S. in Business Administration")
- ❌ No university names remain (e.g., "Cornell University")
- ❌ No graduation dates remain (e.g., "June 20XX", "2018")
- ✅ Institution_1 used for first degree
- ✅ Institution_2 used for second degree

### Skills Section

**Variables Required:**
- ✅ `<<skill_1>>` through `<<skill_N>>`
- ✅ `<<skills_header>>` (section header)

**Common counts:**
- 6 skills for most templates
- Adjust based on template layout

**Check:** No hardcoded skill names (e.g., "Microsoft Excel", "Project Management")

### Interests Section

**Variables Required:**
- ✅ `<<interest_1>>` through `<<interest_N>>`
- ✅ `<<interests_header>>` (section header)

**Common counts:**
- 6 interests for most templates

**Check:** No hardcoded interests (e.g., "Photography", "Travel")

---

## Regional Considerations

### State/Province Variables

**Question to consider:** Does the target user need state/province on their resume?

**Examples:**
- **US users:** Often include state
- **Canadian users:** May NOT want province shown
- **International users:** Varies by country

**Recommendation:** Include state variables but document that they're optional:

```
Contact line options:

Option 1 (with state):
<<city>>, <<state>> <<zip_code>>

Option 2 (without state):
<<city>> <<zip_code>>
```

**Note in documentation:** "For users who don't want state/province displayed, the template can be modified to remove the <<state>> variable."

---

## Quality Assurance Checklist

Before considering a template conversion complete, verify:

### 1. Complete Variable Coverage

- [ ] Read through ENTIRE template from top to bottom
- [ ] Verify every content element has been replaced
- [ ] Check that no example names, companies, or dates remain
- [ ] Confirm no hardcoded achievement text remains

### 2. Variable Consistency

- [ ] Each numbered item uses correct number (position_1 in Job 1, position_2 in Job 2)
- [ ] No variable appears where a different number should be used
- [ ] All variable sets are complete (if job_1_experience_1 exists, job_1_experience_2 should exist)

### 3. Variable Documentation

- [ ] Create list of all variables in template
- [ ] Group by section (Contact, Experience, Education, etc.)
- [ ] Note which variables are optional
- [ ] Document expected data format for each variable

### 4. Test Data Mapping

- [ ] Create sample data showing what each variable expects
- [ ] Test insertion with real user data
- [ ] Verify no placeholders remain visible in output
- [ ] Check that all formatting is preserved

---

## Template Testing Process

### Step 1: Create Variable Inventory

```python
# Extract all variables from template
variables = extract_all_variables(template)

# Group by category
contact_vars = [v for v in variables if v in ['first_name', 'last_name', 'email', ...]]
job_vars = [v for v in variables if 'job_' in v or 'position' in v or 'company' in v]
education_vars = [v for v in variables if 'degree' in v or 'institution' in v]
# etc.
```

### Step 2: Create Test Data

Map real user data to template variables:

```python
test_data = {
    # Contact
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john.doe@email.com',

    # Job 1
    'position_1': 'Senior Manager',
    'company_1': 'Tech Corporation',
    'start_date_1': 'January 2020',
    'end_date_1': 'Present',

    # Check ALL variables have test data
}
```

### Step 3: Run Insertion Test

```python
# Insert test data
output = insert_variables(template, test_data)

# Check for remaining placeholders
remaining = find_placeholders(output)

if remaining:
    print(f"❌ FAILED: {len(remaining)} placeholders remain")
    for placeholder in remaining:
        print(f"  - {placeholder}")
else:
    print("✅ PASSED: All variables replaced")
```

### Step 4: Visual Inspection

- Open generated document
- Read through completely
- Look for:
  - `<<variable_name>>` placeholders still visible
  - Formatting issues
  - Missing content
  - Duplicate content

---

## Example Conversion: Before and After

### Original Template Text

```
John Smith
123 Main Street, New York, NY 10001 | (555) 123-4567 | john.smith@email.com

PROFILE
Results-driven professional with 10+ years of experience in restaurant management.
Passionate about creating exceptional dining experiences.

EXPERIENCE
Restaurant Manager | Contoso Bar and Grill | September 2020 – Present
• Manage daily operations for high-volume establishment
• Increased revenue by 15% through menu optimization
• Trained and supervised team of 30 staff members

Assistant Manager | Downtown Bistro | June 2018 – August 2020
• Supported general manager in all operational decisions
• Reduced food waste by 20%

EDUCATION
B.S. in Hospitality Management | June 2018 | Cornell University, Ithaca, NY

SKILLS
Financial Planning | POS Systems | Staff Training | Menu Development
```

### Properly Converted Template

```
<<first_name>> <<last_name>>
<<street_address>>, <<city>> <<zip_code>> | <<phone>> | <<email>> | <<linkedin_url>>

<<profile_header>>
<<career_overview_1>> <<career_overview_2>> <<career_overview_3>>

<<experience_header>>
<<position_1>> | <<company_1>> | <<start_date_1>> – <<end_date_1>>
<<job_1_experience_1>>
<<job_1_experience_2>>
<<job_1_experience_3>>

<<position_2>> | <<company_2>> | <<start_date_2>> – <<end_date_2>>
<<job_2_experience_1>>
<<job_2_experience_2>>

<<education_header>>
<<degree_1>> | <<graduation_date_1>> | <<institution_1>>, <<institution_city_1>>, <<institution_state_1>>

<<skills_header>>
<<skill_1>> | <<skill_2>> | <<skill_3>> | <<skill_4>>
```

### Conversion Notes

**What was changed:**
- ✅ Names replaced with variables
- ✅ All dates replaced with variables
- ✅ Company names replaced with variables
- ✅ Degree name replaced with variable
- ✅ Institution replaced with variables
- ✅ ALL achievement text replaced with variables
- ✅ Skills replaced with individual variables
- ✅ Section headers made into variables

**Critical fixes:**
- Company "Contoso Bar and Grill" → `<<company_1>>`
- Date "September 2020" → `<<start_date_1>>`
- Company "Downtown Bistro" → `<<company_2>>`
- Degree "B.S. in Hospitality Management" → `<<degree_1>>`
- University "Cornell University" → `<<institution_1>>`
- Location "Ithaca, NY" → `<<institution_city_1>>, <<institution_state_1>>`

---

## Variable Count Guidelines

Different templates will have different variable counts based on complexity:

### Minimal Template (Basic Resume)
- ~20-25 variables
- 1 job, 1 education entry
- Basic contact info
- Few skills/interests

### Standard Template (Mid-Level Resume)
- ~30-40 variables
- 2 jobs, 1-2 education entries
- Full contact info
- Skills and interests sections

### Comprehensive Template (Senior Resume)
- ~45-55 variables
- 2-3 jobs with multiple bullets
- 2 education entries
- Multiple skills and interests
- Additional sections (certifications, etc.)

**Rule:** More detailed template = more variables needed

---

## Common Template Patterns

### Pattern 1: Multiple Jobs

```
Job 1: position_1, company_1, start_date_1, end_date_1
       job_1_experience_1, job_1_experience_2, job_1_experience_3

Job 2: position_2, company_2, start_date_2, end_date_2
       job_2_experience_1, job_2_experience_2, job_2_experience_3, job_2_experience_4

Job 3: position_3, company_3, start_date_3, end_date_3
       job_3_experience_1, job_3_experience_2
```

**Note:** Number of experience bullets can vary per job

### Pattern 2: Multiple Education Entries

```
Education 1: degree_1, major_1, institution_1, institution_city_1,
             institution_state_1, graduation_date_1

Education 2: degree_2, major_2, institution_2, institution_city_2,
             institution_state_2, graduation_date_2
```

**Important:** Each education entry gets its own complete variable set

### Pattern 3: Career Overview Statements

```
<<career_overview_1>> <<career_overview_2>> <<career_overview_3>>
<<career_overview_4>> <<career_overview_5>>
```

**Note:** These often appear as a continuous paragraph but are separate variables for flexibility

---

## Troubleshooting Guide

### Issue: Low Success Rate in Testing

**Symptom:** Data insertion test shows only 50-70% of variables replaced

**Likely causes:**
1. Hardcoded values remain in template
2. Variables missing that should exist
3. Variable numbering inconsistent

**Solution:**
1. Search template for all hardcoded examples
2. Add missing variables
3. Verify numbering consistency

### Issue: Visible Placeholders in Output

**Symptom:** Generated resume shows `<<variable_name>>` in document

**Likely causes:**
1. Variable in template but not in data mapping
2. Variable name misspelled
3. Variable not included in data source

**Solution:**
1. Create complete variable list
2. Verify spelling matches exactly
3. Ensure all variables have data mappings

### Issue: Duplicate Content

**Symptom:** Same position appears in Job 1 and Job 2

**Likely cause:** Variable duplication (using position_1 twice)

**Solution:**
1. Search for all instances of position_1, position_2, etc.
2. Verify each appears only in correct section
3. Add missing position_2, position_3 variables

---

## Agent Workflow Summary

### Phase 1: Analysis (Don't Skip!)
1. Read entire template top to bottom
2. Identify all content that varies per user
3. Note template structure (how many jobs, education entries, etc.)
4. Check for regional considerations (state/province, etc.)

### Phase 2: Conversion
1. Replace ALL variable content with semantic variable names
2. Use consistent numbering (1, 2, 3, not 1, 1, 1)
3. Create complete variable sets for each section
4. Document all variables created

### Phase 3: Verification
1. Search for hardcoded values (company names, dates, degrees)
2. Check variable numbering consistency
3. Verify all section headers are variables
4. Create variable inventory list

### Phase 4: Testing
1. Map real user data to variables
2. Run insertion test
3. Check success rate (target: >85%)
4. Visual inspection of output
5. Document any remaining issues

### Phase 5: Documentation
1. List all variables by category
2. Note optional vs required variables
3. Provide sample data format
4. Include usage examples

---

## Success Criteria

A properly converted template should achieve:

- ✅ **>85% success rate** in data insertion testing
- ✅ **Zero hardcoded values** (no example names, companies, dates)
- ✅ **Consistent variable numbering** (no duplicates)
- ✅ **Complete variable sets** (all jobs/education entries fully variablized)
- ✅ **Professional output** (no visible placeholders for provided data)
- ✅ **Comprehensive documentation** (all variables listed and explained)

---

## Final Reminders

1. **Everything is a variable** - If it could be different for different users, it's a variable
2. **Numbers must be consistent** - position_1 in Job 1, position_2 in Job 2
3. **Complete the sets** - If degree_1 exists, graduation_date_1 should exist
4. **Test with real data** - Don't assume it works without testing
5. **Document thoroughly** - Future users need to know what variables exist

**The goal:** A template where ANY user can insert their data and get a professional, personalized resume with ZERO manual editing required.
