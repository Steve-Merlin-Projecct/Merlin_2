---
title: "Librarian"
type: technical_doc
component: general
status: draft
tags: []
---

Execute librarian system commands for documentation management

## Available Commands

### /librarian index
Regenerate the documentation index (JSON + HTML)

Usage: `/librarian index`

Runs: `python tools/librarian_index.py`

Output:
- docs/indexes/documentation-index.json
- docs/indexes/documentation-map.html

### /librarian validate
Validate all documentation metadata and organization

Usage: `/librarian validate`

Runs: `python tools/librarian_validate.py --summary`

Shows:
- Files with errors
- Files with warnings
- Total validation status

### /librarian scan
Scan metadata coverage across all documentation

Usage: `/librarian scan`

Runs: `python tools/librarian_metadata.py --scan`

Shows:
- Total files
- Metadata completeness percentages
- Missing fields report

### /librarian archive
Run archival workflow (preview mode)

Usage: `/librarian archive`

Runs: `python tools/librarian_archive.py --dry-run`

Shows what files would be archived based on completion status

### /librarian audit
Launch librarian agent for comprehensive documentation audit

Usage: `/librarian audit`

Launches specialized librarian agent to:
- Analyze all 400+ project files
- Identify organizational issues
- Generate detailed audit report
- Provide prioritized recommendations

### /librarian status
Show current librarian system status and metrics

Usage: `/librarian status`

Displays:
- Last index update timestamp
- Last validation run results
- Metadata coverage percentage
- Broken links count
- Archive candidates count
- Quick actions

## Quick Start

```bash
# Check current state
/librarian scan
/librarian validate

# Update documentation index
/librarian index

# Preview what would be archived
/librarian archive

# Run comprehensive audit (quarterly)
/librarian audit
```

## Implementation

When user types `/librarian <command>`, execute the corresponding tool or agent.

Example responses:

```markdown
# For /librarian scan
Running metadata scan...

[Execute: python tools/librarian_metadata.py --scan]

Current metadata coverage: 65% (133/203 files)
See output above for details.

# For /librarian audit
Launching librarian agent for comprehensive audit...

[Launch Task tool with librarian agent]

Agent will analyze all files and generate detailed audit report.
This typically takes 20-30 minutes.
```

## Notes

- Commands execute librarian tools in the tools/ directory
- All commands are read-only except /librarian archive (which can be run with --auto flag)
- /librarian audit launches the specialized librarian agent
- Status command reads from generated index files
