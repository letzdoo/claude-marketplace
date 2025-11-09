# Implementation Plan v2.0.0 - Bold Redesign

## Strategy: All Improvements in One Release

**No gradual migration** - implement all improvements together for v2.0.0.

---

## Timeline: 4-5 Weeks to v2.0.0

### Week 1: Foundation & Setup
### Week 2: Workflow Redesign
### Week 3: Tool Automation
### Week 4: Testing & Documentation
### Week 5: Beta Testing & Launch

---

## Week 1: Foundation & Setup 🏗️

### Day 1-2: One-Command Setup

**Create**: `commands/odoo-setup.md`

```markdown
---
description: Automated setup and validation of Odoo plugin prerequisites
---

# Odoo Plugin Setup

Run comprehensive setup with automatic dependency installation.

## Process

1. **Check Docker**
   ```bash
   docker --version || echo "ERROR: Docker required"
   ```

2. **Check Python Version**
   ```bash
   python3 --version
   # Must be 3.10+
   ```

3. **Check/Install uv**
   ```bash
   if ! command -v uv &> /dev/null; then
     echo "Installing uv..."
     curl -LsSf https://astral.sh/uv/install.sh | sh
   fi
   ```

4. **Detect Odoo Path**
   ```bash
   # Try common locations:
   # - $ODOO_PATH (env var)
   # - /home/coder/letzdoo-sh/odoo/custom/src
   # - ./odoo/custom/src
   # - Ask user if not found
   ```

5. **Build Indexer**
   ```bash
   cd skills/odoo-indexer
   uv run scripts/update_index.py --full
   ```

6. **Validate Installation**
   ```bash
   # Test search
   uv run scripts/search.py "sale.order" --type model --limit 1
   ```

7. **Report Success**
   ```
   ✅ Setup complete!

   Indexed: X modules, Y models, Z fields
   Search speed: <50ms

   Ready to use: /odoo-dev "your request"
   ```
```

**Implementation**: 2 days

---

### Day 3-4: Documentation Consolidation

**Create**: `INSTALLATION.md` (single source of truth)

```markdown
# Installation Guide

## Quick Start (5 minutes)

```bash
# 1. Install plugin
/plugin install odoo-doodba-dev@letzdoo

# 2. Run setup
/odoo-setup
```

Done! 🎉

## Prerequisites

Auto-checked by `/odoo-setup`:
- ✓ Doodba-based Odoo deployment
- ✓ Docker & Docker Compose
- ✓ Python 3.10+
- ✓ uv (auto-installed if missing)

## Manual Setup (if needed)

Only if `/odoo-setup` fails:

1. Set Odoo path:
   ```bash
   export ODOO_PATH=/path/to/odoo/custom/src
   ```

2. Re-run setup:
   ```bash
   /odoo-setup
   ```

## Troubleshooting

### uv installation failed
Install manually:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Odoo path not detected
Set explicitly:
```bash
export ODOO_PATH=/your/path
/odoo-setup
```

### Index build failed
Check permissions and path:
```bash
ls -la $ODOO_PATH
```
```

**Update**: Simplify main `README.md` to point to `INSTALLATION.md`

**Implementation**: 1 day

---

### Day 5: Project Structure Reorganization

**New structure**:
```
odoo-doodba-dev/
├── .claude-plugin/
│   └── plugin.json (v2.0.0)
├── commands/
│   ├── odoo-setup.md (NEW)
│   ├── odoo-dev.md (NEW - replaces workflow)
│   ├── odoo-search.md (NEW - merges info + search)
│   ├── odoo-test.md (KEEP)
│   └── odoo-scaffold.md (KEEP)
├── agents/
│   ├── odoo-developer.md (NEW - merges analyst+implementer)
│   ├── odoo-verifier.md (NEW - merges validator+tester)
│   └── odoo-documenter.md (UPDATED - optional mode)
├── skills/
│   └── odoo-indexer/
│       ├── SKILL.md (UPDATED - proactive description)
│       └── tools/ (NEW - tool wrappers)
├── INSTALLATION.md (NEW)
├── MIGRATION.md (NEW - v1 to v2 guide)
└── README.md (SIMPLIFIED)
```

**Remove**:
- `commands/odoo-workflow.md` (replaced by odoo-dev)
- `commands/odoo-validate.md` (auto in workflow)
- `commands/odoo-info.md` (merged into odoo-search)
- `commands/odoo-addons.md` (rarely used, remove)
- `commands/odoo-shell.md` (rarely used, remove)
- `commands/odoo-logs.md` (rarely used, remove)

**Keep only essentials**: setup, dev, search, test, scaffold

**Implementation**: 1 day

---

## Week 2: Workflow Redesign ⚡

### Day 6-8: Unified Developer Agent

**Create**: `agents/odoo-developer.md`

Merges `odoo-analyst` + `odoo-implementer`:

```markdown
---
name: odoo-developer
description: |
  PROACTIVELY develop Odoo features when user requests implementation.
  AUTO-TRIGGER on: "create", "add", "implement", "develop", "build"
  Handles analysis + implementation in one flow.
---

# Odoo Developer Agent

You analyze requirements AND implement code. Complete development workflow.

## Process

1. **Quick Analysis** (not a separate stage)
   - Ask clarifying questions if needed
   - Use indexer to validate references
   - Propose architecture inline
   - Get architecture approval ONLY

2. **Immediate Implementation** (after approval)
   - Auto-validate all references with indexer
   - Create all files
   - Run auto-validation
   - Report completion

## Architecture Decision (Inline)

Don't create a spec file. Present architecture inline:

```
📐 Architecture:
   Module: quality_project_task (NEW)
   Models: 1 (extends project.task)
   Fields: quality_result_id (Many2one)
   Views: Form view update

   Proceed? [y/n]
```

## Implementation Rules

- Validate ALL references with indexer before coding
- Follow field naming: _id (Many2one), _ids (Many2many/One2many)
- Use <list> not <tree> for Odoo 18+
- Create tests automatically
- Run auto-validation with indexer

## Auto-Validation

After code generation, automatically:

```bash
# Validate models
uv run skills/odoo-indexer/scripts/search.py "{model_name}"

# Validate fields
uv run skills/odoo-indexer/scripts/get_details.py field "{field}" --parent "{model}"

# Validate XML IDs
uv run skills/odoo-indexer/scripts/search_xml_id.py "{xml_id}"
```

Report validation results inline.

## Output Format

```markdown
✅ Development Complete!

**Module**: quality_project_task
**Location**: odoo/custom/src/private/quality_project_task/
**Files Created**:
- models/project_task.py
- views/project_task_views.xml
- security/ir.model.access.csv
- tests/test_quality.py

**Validation**: ✓ All references validated
**Tests**: ✓ Generated (3 tests)

Ready to verify and test!
```

No spec file, no separate stages, just results.
```

**Implementation**: 3 days

---

### Day 9-10: Unified Verifier Agent

**Create**: `agents/odoo-verifier.md`

Merges `odoo-validator` + `odoo-tester`:

```markdown
---
name: odoo-verifier
description: |
  PROACTIVELY verify and test Odoo modules after development.
  AUTO-TRIGGER after implementation completion.
  Handles validation + testing in one flow.
---

# Odoo Verifier Agent

You validate structure AND run tests. Complete verification workflow.

## Process

1. **Structure Validation** (automatic)
   - Check file structure
   - Validate with indexer
   - Check security files exist
   - Verify manifest

2. **Test Execution** (automatic)
   - Run existing tests
   - Report results
   - Identify failures

3. **Report** (inline, no file unless failures)

## Validation Checks

Auto-run:
```bash
# Structure
ls -la {module_path}

# Indexer validation
uv run skills/odoo-indexer/scripts/search.py "{module}" --type model

# Run tests
invoke test --modules={module_name}
```

## Output Format

**If all passed**:
```markdown
✅ Verification Complete!

**Structure**: ✓ Valid
**References**: ✓ All found
**Tests**: ✓ 3/3 passed

Module ready for installation!
Install: invoke install -m {module_name}
```

**If failures**:
```markdown
⚠️ Verification Issues Found

**Tests Failed**: 1/3
- test_quality_result: AssertionError

**Suggested Fixes**:
1. Check quality_result_id field computation
2. Verify access rights

Fix issues and re-run verification?
```

Only create report file if there are failures.
```

**Implementation**: 2 days

---

### Day 11-12: Smart Development Command

**Create**: `commands/odoo-dev.md`

Replaces `odoo-workflow.md`:

```markdown
---
description: Smart Odoo development with automatic mode detection
---

# Odoo Development Command

Intelligent development that adapts to task complexity.

## Auto-Mode Detection

**Simple Task** (Quick Mode):
- 1-2 field additions
- Minor view changes
- Small extensions
→ Direct implementation with tests

**Complex Task** (Full Mode):
- New modules
- Multiple models
- Complex workflows
→ Architecture discussion + phased development

**Question** (Search Mode):
- "What is..."
- "Show me..."
- "Find..."
→ Use indexer to answer

## Usage

```bash
# Simple task (auto: quick mode)
/odoo-dev "add quality_result field to project.task"

# Complex task (auto: full mode)
/odoo-dev "create inventory management module"

# Question (auto: search mode)
/odoo-dev "what fields does sale.order have?"
```

## Process

### Quick Mode Flow
```
User request
  ↓
Detect: Simple task
  ↓
Call: odoo-developer agent (inline architecture)
  ↓ (architecture approval)
Implement + auto-validate
  ↓
Call: odoo-verifier agent
  ↓
Done! (5-7 minutes)
```

### Full Mode Flow
```
User request
  ↓
Detect: Complex task
  ↓
Call: odoo-developer agent
  ↓
Architecture discussion → approval
  ↓
Phased implementation
  ↓
Call: odoo-verifier agent
  ↓
Optional: Documentation? (ask user)
  ↓ (if yes)
Call: odoo-documenter agent
  ↓
Done! (20-25 minutes)
```

### Search Mode Flow
```
User question
  ↓
Detect: Question
  ↓
Auto-use indexer tools
  ↓
Answer immediately (<2 seconds)
```

## Key Differences from v1

**v1** (old):
- Manual workflow invocation
- 5 stages with 5 approvals
- Always creates spec files
- Always creates documentation

**v2** (new):
- Auto-detects mode
- 1-2 approvals only
- No spec files for simple tasks
- Optional documentation

**Result**: 60-80% faster
```

**Implementation**: 2 days

---

## Week 3: Tool Automation 🤖

### Day 13-15: Proactive Skill Description

**Update**: `skills/odoo-indexer/SKILL.md`

```markdown
---
name: Odoo Indexer
description: |
  PROACTIVELY index and search Odoo codebase when user asks about code structure.

  AUTO-TRIGGER for:
  - "what is [model/field/view]"
  - "find [element]"
  - "search for [element]"
  - "show me [element]"
  - "where is [element]"
  - "does [model] have [field]"

  This skill provides 95% faster responses than file reading.
  ALWAYS prefer indexer over Read tool for Odoo code exploration.

allowed-tools: Read, Bash, Grep, Glob
proactive: true
trigger-keywords: ["what is", "find", "search", "show me", "where is", "does", "list", "get"]
---

# Odoo Indexer

**USE THIS SKILL PROACTIVELY** when user asks about Odoo code.

## When to Auto-Use

✅ User asks: "What fields does sale.order have?"
→ AUTO-USE: uv run scripts/get_details.py model "sale.order"

✅ User asks: "Find all Many2one fields in sale"
→ AUTO-USE: uv run scripts/search_by_attr.py field --filters '{"field_type":"Many2one"}' --module sale

✅ User asks: "Where is project.task defined?"
→ AUTO-USE: uv run scripts/search.py "project.task" --type model

✅ User asks: "Does sale.order have partner_id?"
→ AUTO-USE: uv run scripts/search.py "partner_id" --type field --parent "sale.order"

## Commands

[... rest of existing documentation ...]
```

**Add**: Trigger keywords in frontmatter for automatic invocation

**Implementation**: 1 day

---

### Day 16-17: Native Tool Wrappers

**Create**: `skills/odoo-indexer/tools/` directory

Create wrapper scripts that are easier to invoke:

**`tools/search_model.sh`**:
```bash
#!/bin/bash
# Wrapper for model search
cd "$(dirname "$0")/.."
uv run scripts/search.py "$1" --type model --limit "${2:-20}"
```

**`tools/get_model_details.sh`**:
```bash
#!/bin/bash
# Wrapper for model details
cd "$(dirname "$0")/.."
uv run scripts/get_details.py model "$1"
```

**`tools/validate_field.sh`**:
```bash
#!/bin/bash
# Wrapper for field validation
cd "$(dirname "$0")/.."
MODEL="$1"
FIELD="$2"
uv run scripts/search.py "$FIELD" --type field --parent "$MODEL" --limit 1
```

**Update agents** to use these wrappers instead of full commands.

**Implementation**: 2 days

---

### Day 18-19: Inline Validation Display

**Update all agents** to show validation as it happens:

```markdown
💻 Creating model quality.check...
   🔍 Validating inheritance...
      ✓ project.task found in project module
   🔍 Validating field: quality_result_id
      ✓ quality.result model exists
      ✓ Many2one relationship valid
   🔍 Validating field: check_ids
      ✓ One2many relationship valid
      ✓ Comodel: quality.check.line exists
   ⚠️  Consider: Add security rule for quality.manager

   ✅ All validations passed!
```

**Implementation**: 2 days

---

## Week 4: Testing & Documentation 📝

### Day 20-22: Comprehensive Testing

**Test scenarios**:

1. **Setup Command**
   - First-time setup
   - Re-run setup (should be idempotent)
   - Setup with missing dependencies
   - Setup with wrong paths
   - Setup recovery from errors

2. **Quick Mode Development**
   - Simple field addition
   - View modification
   - Small extension
   - Validation success
   - Validation failure handling

3. **Full Mode Development**
   - New module creation
   - Multiple models
   - Complex workflows
   - Architecture approval
   - Optional documentation

4. **Search Mode**
   - Model queries
   - Field queries
   - View queries
   - Complex searches

5. **Tool Auto-Invocation**
   - Verify triggers work
   - Test keyword matching
   - Ensure tool responses

6. **Error Handling**
   - Invalid module names
   - Missing dependencies
   - Test failures
   - Validation errors

**Implementation**: 3 days

---

### Day 23-24: Updated Documentation

**Update all docs**:

1. **README.md** (simplified)
   - Quick overview
   - Link to INSTALLATION.md
   - Basic usage examples
   - Link to full docs

2. **INSTALLATION.md** (created in Week 1)
   - Complete setup guide
   - Troubleshooting

3. **MIGRATION.md** (new)
   - v1 → v2 changes
   - Command mapping
   - What's removed
   - What's new
   - Migration checklist

4. **USAGE_GUIDE.md** (new)
   - Quick start examples
   - Command reference
   - Best practices
   - Common workflows

**Implementation**: 2 days

---

### Day 25: Polish & Optimization

- Code cleanup
- Remove old files
- Update version to 2.0.0
- Test all scenarios again
- Performance optimization
- Error message improvements

**Implementation**: 1 day

---

## Week 5: Beta & Launch 🚀

### Day 26-28: Beta Testing

**Beta testers**: 3-5 existing users

**Test protocol**:
1. Clean install
2. Setup process
3. Simple task
4. Complex task
5. Search queries
6. Error scenarios
7. Gather feedback

**Metrics to track**:
- Setup success rate (target: 95%+)
- Setup time (target: <5 min)
- Simple task time (target: <10 min)
- User satisfaction (target: 4.5+/5.0)

**Implementation**: 3 days

---

### Day 29: Final Adjustments

Based on beta feedback:
- Fix critical issues
- Improve error messages
- Update documentation
- Optimize performance

**Implementation**: 1 day

---

### Day 30: Release v2.0.0

**Release checklist**:

- ✅ All tests passing
- ✅ Documentation complete
- ✅ MIGRATION.md ready
- ✅ CHANGELOG.md updated
- ✅ Version bumped to 2.0.0
- ✅ Git tagged: v2.0.0
- ✅ Pushed to main branch
- ✅ Release notes published
- ✅ Announcement prepared

**Release notes structure**:
```markdown
# Odoo Doodba Dev Plugin v2.0.0

## 🎉 Major Release: Streamlined & Fast

### ⚡ Performance Improvements
- 75% faster setup (2-5 min vs 15-30 min)
- 60-80% faster development
- 90% less manual tool invocation

### 🎯 New Features
- `/odoo-setup` - One-command automated setup
- `/odoo-dev` - Smart development with auto-mode detection
- Proactive tool usage - Indexer auto-triggers
- Inline validation - See validation as it happens

### 🔄 Breaking Changes
- Removed: `/odoo-workflow` → Use `/odoo-dev`
- Removed: `/odoo-validate` → Automatic in workflow
- Removed: `/odoo-info` → Merged into `/odoo-search`
- Removed: `/odoo-addons`, `/odoo-shell`, `/odoo-logs`
- Agent changes: Combined agents for efficiency

### 📚 Migration Guide
See MIGRATION.md for complete v1 → v2 migration guide.

### 🙏 Credits
Thanks to beta testers: [names]
```

**Implementation**: 1 day

---

## File Changes Summary

### New Files (10)
```
commands/odoo-setup.md
commands/odoo-dev.md
commands/odoo-search.md
agents/odoo-developer.md
agents/odoo-verifier.md
skills/odoo-indexer/tools/search_model.sh
skills/odoo-indexer/tools/get_model_details.sh
skills/odoo-indexer/tools/validate_field.sh
INSTALLATION.md
MIGRATION.md
USAGE_GUIDE.md
```

### Modified Files (4)
```
.claude-plugin/plugin.json (v2.0.0)
skills/odoo-indexer/SKILL.md (proactive)
agents/odoo-documenter.md (optional mode)
README.md (simplified)
```

### Removed Files (8)
```
commands/odoo-workflow.md
commands/odoo-validate.md
commands/odoo-info.md
commands/odoo-addons.md
commands/odoo-shell.md
commands/odoo-logs.md
agents/odoo-analyst.md
agents/odoo-implementer.md
agents/odoo-validator.md
agents/odoo-tester.md
workflows/templates/SPEC-template.md
workflows/templates/VALIDATION-template.md
workflows/templates/TEST-REPORT-template.md
```

Net: +10 new, -8 removed, 4 modified = **Simpler structure**

---

## Command Mapping (v1 → v2)

| v1 Command | v2 Command | Notes |
|------------|------------|-------|
| `/odoo-workflow` | `/odoo-dev` | Auto-detects mode |
| `/odoo-validate` | (automatic) | Built into workflow |
| `/odoo-info` | `/odoo-search` | Merged functionality |
| `/odoo-addons` | (removed) | Use invoke directly |
| `/odoo-shell` | (removed) | Use invoke directly |
| `/odoo-logs` | (removed) | Use invoke directly |
| (new) | `/odoo-setup` | New one-command setup |
| `/odoo-test` | `/odoo-test` | Kept as-is |
| `/odoo-scaffold` | `/odoo-scaffold` | Kept as-is |

---

## Risk Mitigation

### High-Risk Areas

1. **Breaking Changes**
   - Risk: Users confused by removed commands
   - Mitigation: Clear MIGRATION.md + announcement
   - Mitigation: Helpful error messages pointing to new commands

2. **Auto-Tool Invocation**
   - Risk: Tools trigger when not intended
   - Mitigation: Careful keyword selection
   - Mitigation: Beta testing to tune triggers

3. **Setup Automation**
   - Risk: Setup fails in edge cases
   - Mitigation: Comprehensive error handling
   - Mitigation: Fallback to manual setup

### Testing Strategy

- ✅ Unit tests for each component
- ✅ Integration tests for workflows
- ✅ Beta testing with real users
- ✅ Edge case testing
- ✅ Error scenario testing

---

## Success Criteria

### Must Have (Launch Blockers)
- ✅ Setup success rate: >90%
- ✅ All core workflows functional
- ✅ No data loss or corruption
- ✅ Documentation complete
- ✅ Migration guide ready

### Should Have (Post-Launch)
- ⭐ Setup success rate: >95%
- ⭐ User satisfaction: >4.5/5.0
- ⭐ Simple task time: <10 min
- ⭐ Support issues: <50% of v1

### Nice to Have (Future)
- 💫 Auto-tool accuracy: >95%
- 💫 Zero-config setup (detect everything)
- 💫 Interactive tutorials
- 💫 Video documentation

---

## Post-Launch Plan

### Week 6-7: Monitor & Support
- Monitor for issues
- Quick bug fixes
- User support
- Gather feedback

### Week 8: Iteration
- Implement feedback
- Performance tuning
- Documentation improvements
- Release v2.1.0 (bug fixes + minor improvements)

---

## Implementation Team Roles

**If solo developer**: 5 weeks full-time

**If team**:
- **Backend Dev** (3 weeks): Agents, workflow logic
- **DevOps** (2 weeks): Setup automation, testing
- **Doc Writer** (1 week): Documentation, migration guide
- **QA** (1 week): Testing, beta coordination

**Parallel work**: Weeks can overlap, potentially 3-4 weeks total

---

## Decision Points

### Week 1 End
**Review**: Setup command working?
**Decision**: Continue or adjust timeline

### Week 2 End
**Review**: Workflow redesign complete?
**Decision**: Agent logic sound? Need changes?

### Week 3 End
**Review**: Tool automation working?
**Decision**: Triggers accurate? Need tuning?

### Week 4 End
**Review**: Tests passing? Docs complete?
**Decision**: Ready for beta? Need more time?

### Week 5 End
**Review**: Beta feedback positive?
**Decision**: Launch or delay?

---

## Rollback Plan

If major issues found during beta:

1. **Stop release** - Don't push v2.0.0
2. **Analyze issues** - Categorize by severity
3. **Quick fixes** - If fixable in 1-2 days, fix
4. **Delay release** - If needs major rework, delay 1 week
5. **Communicate** - Update beta testers and planned launch date

**Rollback threshold**: >3 critical bugs or <80% beta approval

---

## Communication Plan

### Week 1-4 (Development)
- Weekly progress updates (internal)
- Demo videos (optional)

### Week 5 (Beta)
- Beta invitations
- Daily check-ins with beta testers
- Feedback collection

### Launch Day
- Release announcement
- Social media (if applicable)
- Email to existing users
- Update marketplace listing

### Post-Launch
- Monitor support channels
- Quick response to issues
- Regular updates

---

## Budget Estimate (Time)

| Phase | Solo Dev | Small Team (3) |
|-------|----------|----------------|
| Week 1 | 40 hrs | 40 hrs (1 person) |
| Week 2 | 40 hrs | 40 hrs (1 person) |
| Week 3 | 40 hrs | 40 hrs (1 person) |
| Week 4 | 40 hrs | 60 hrs (2 people) |
| Week 5 | 40 hrs | 30 hrs (full team) |
| **Total** | **200 hrs** | **210 hrs** |

**Calendar time**:
- Solo: 5 weeks
- Team: 3-4 weeks (with parallel work)

---

## Final Checklist

### Pre-Development
- [ ] Review this plan
- [ ] Set up development branch
- [ ] Prepare development environment
- [ ] Schedule beta testers

### Development (Week 1-4)
- [ ] Week 1: Foundation & Setup complete
- [ ] Week 2: Workflow Redesign complete
- [ ] Week 3: Tool Automation complete
- [ ] Week 4: Testing & Documentation complete

### Pre-Launch (Week 5)
- [ ] Beta testing complete
- [ ] All critical issues fixed
- [ ] Documentation finalized
- [ ] Migration guide ready
- [ ] Release notes written
- [ ] Version bumped to 2.0.0
- [ ] Git tagged

### Launch
- [ ] Merged to main
- [ ] Released v2.0.0
- [ ] Announcement sent
- [ ] Marketplace updated

### Post-Launch (Week 6-7)
- [ ] Monitor for issues
- [ ] Support users
- [ ] Gather feedback
- [ ] Plan v2.1.0 improvements

---

## Next Steps: Start Today! 🎬

1. **Create branch**: `git checkout -b feature/v2.0.0-redesign`
2. **Start Week 1, Day 1**: Create `commands/odoo-setup.md`
3. **Track progress**: Update this document with checkboxes
4. **Regular commits**: Commit daily with clear messages
5. **Stay focused**: Follow the week-by-week plan

---

**Let's build v2.0.0! 🚀**

**Timeline**: 4-5 weeks
**Target Release**: [Set date based on start]
**Expected Impact**: 60-80% faster, 90% less friction, same quality!
