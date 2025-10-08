# Branch Review Workflow

**Purpose:** Standardized workflow for reviewing and archiving merged feature branches

## Review Checklist

Before archiving any merged branch, verify:

- [ ] Associated slash command works correctly (if applicable)
- [ ] Documentation is clear and comprehensive
- [ ] Scripts execute properly (if applicable)
- [ ] Examples are helpful and accurate
- [ ] No broken links in documentation
- [ ] Integration with existing CLAUDE.md is correct

## Post-Review Actions

### If Approved

1. Mark branch as archived in branch status file
2. Add archival note to master changelog
3. Delete local branch: `git branch -d <branch-name>`
4. Delete remote branch: `git push origin --delete <branch-name>`

### If Changes Needed

1. Document required changes in branch status file
2. Create new commits on the branch
3. Re-merge to main (if necessary)
4. Update review checklist

## Testing Recommendations

### For Slash Commands

1. Test command execution with simple use case
2. Verify all phases execute correctly
3. Check output formatting and completeness

### For Automation Scripts

1. Run scripts with test inputs
2. Verify file operations complete
3. Check commit creation and messages

### For Documentation

1. Read through all new/updated documentation
2. Follow examples step-by-step
3. Verify all links work
4. Check for consistency with existing docs

## Branch Status File Location

Store branch-specific status files in:
`/workspace/docs/git_workflow/branch-status/<branch-name>.md`

## Archival Process

1. **Review Phase:** Complete checklist above
2. **Update Status:** Mark branch as ARCHIVED in status file
3. **Document:** Add to master changelog
4. **Clean Up:** Delete local and remote branches
5. **Preserve:** Keep branch status file for historical reference

## Best Practices

- Review branches promptly after merge (within 1-2 days)
- Test all new functionality thoroughly before archival
- Document any issues discovered during review
- Preserve branch status files even after deletion
- Link to relevant PRs and commits in status files
