# Test Checklist - Odoo Doodba Dev Plugin v2.0

Comprehensive testing checklist to ensure v2.0 quality standards and verify all improvements.

**Target**: 100% quality preservation from v1.x with 60-80% faster performance.

---

## Testing Overview

### Test Categories

- ✅ **Installation & Setup** - Initial configuration and prerequisite checks
- ✅ **Commands** - All 5 commands functional and intelligent
- ✅ **Agents** - All 3 agents working with proactive behavior
- ✅ **Skills** - Indexer skill with auto-triggers
- ✅ **Workflows** - Quick/Full/Search modes with correct timing
- ✅ **Integration** - End-to-end scenarios
- ✅ **Performance** - Speed and token efficiency
- ✅ **Regression** - v1.x features preserved

### Test Environments

- [ ] Fresh installation (no prior setup)
- [ ] Upgrade from v1.x
- [ ] Multiple Odoo versions (14.0, 15.0, 16.0, 17.0)
- [ ] Different operating systems (Linux, macOS)

---

## 1. Installation & Setup Tests

### 1.1 Fresh Installation

**Command**: `/odoo-setup`

- [ ] **Test**: Run on system without uv
  - Expected: Auto-installs uv successfully
  - Time: <3 minutes

- [ ] **Test**: Run on system without Odoo
  - Expected: Shows clear error, provides guidance
  - Time: <10 seconds

- [ ] **Test**: Run on system with Odoo but no index
  - Expected: Builds index successfully
  - Time: 2-10 minutes (depending on codebase size)

- [ ] **Test**: Run with existing index
  - Expected: Verifies and updates if needed
  - Time: <30 seconds

- [ ] **Test**: Run with incorrect Odoo path
  - Expected: Auto-detects or prompts for correct path
  - Time: <20 seconds

### 1.2 Prerequisite Checks

- [ ] **Python version**: Detects Python 3.8+
- [ ] **Docker**: Detects Docker 20+
- [ ] **Doodba**: Detects invoke tasks
- [ ] **Disk space**: Warns if <500MB available
- [ ] **Permissions**: Checks write access to index directory

### 1.3 Index Building

- [ ] **Small codebase** (50 modules): <2 minutes
- [ ] **Medium codebase** (100-150 modules): 2-5 minutes
- [ ] **Large codebase** (200+ modules): 5-10 minutes
- [ ] **Error handling**: Graceful failures on corrupted files
- [ ] **Progress display**: Shows indexing progress

### 1.4 Installation Verification

After `/odoo-setup` completes:

- [ ] Index database exists: `~/.odoo-indexer/odoo_indexer.sqlite3`
- [ ] Index size: 10-50 MB (reasonable)
- [ ] `/odoo-search "list modules"` works
- [ ] uv command available: `which uv`
- [ ] All scripts executable in `skills/odoo-indexer/tools/`

---

## 2. Command Tests

### 2.1 `/odoo-search` Command

#### Basic Searches

- [ ] **Test**: `/odoo-search "what is sale.order"`
  - Expected: Model details, fields, views, <100ms
  - Result: ⏱️ ______ms

- [ ] **Test**: `/odoo-search "what fields does res.partner have"`
  - Expected: Categorized field list, <100ms
  - Result: ⏱️ ______ms

- [ ] **Test**: `/odoo-search "find task views"`
  - Expected: List of project.task views, <100ms
  - Result: ⏱️ ______ms

- [ ] **Test**: `/odoo-search "where is project.task defined"`
  - Expected: File location and module, <50ms
  - Result: ⏱️ ______ms

#### Advanced Searches

- [ ] **Test**: `/odoo-search "find all Many2one fields in sale module"`
  - Expected: Filtered field list, <150ms
  - Result: ⏱️ ______ms

- [ ] **Test**: `/odoo-search "show me partner_id in sale.order"`
  - Expected: Field details with type, comodel, attributes, <50ms
  - Result: ⏱️ ______ms

- [ ] **Test**: `/odoo-search "list modules"`
  - Expected: All indexed modules with stats, <100ms
  - Result: ⏱️ ______ms

- [ ] **Test**: `/odoo-search "tell me about the sale module"`
  - Expected: Module stats, dependencies, models, <100ms
  - Result: ⏱️ ______ms

#### Error Handling

- [ ] **Test**: Search for non-existent model
  - Expected: "Not found" message with suggestions

- [ ] **Test**: Search with typo
  - Expected: Helpful suggestions ("did you mean...")

- [ ] **Test**: Very broad search
  - Expected: Limited results with "X more available"

### 2.2 `/odoo-dev` Command

#### Quick Mode (Simple Tasks)

- [ ] **Test**: `/odoo-dev "add notes field (Text) to res.partner"`
  - Expected:
    - Mode detected: Quick
    - Inline architecture proposal
    - 1 approval request
    - Implementation with auto-validation
    - Automatic verification
    - Time: 5-7 minutes
  - Actual time: _______ minutes

- [ ] **Test**: `/odoo-dev "add priority field to project.task with values low, normal, high, urgent"`
  - Expected:
    - Quick Mode
    - Field added with Selection type
    - View updated
    - Tests generated
    - Time: 5-7 minutes
  - Actual time: _______ minutes

- [ ] **Test**: `/odoo-dev "update sale order form view to show delivery status"`
  - Expected:
    - Quick Mode
    - View inheritance created
    - Field added to form
    - Time: 5-7 minutes
  - Actual time: _______ minutes

#### Full Mode (Complex Features)

- [ ] **Test**: `/odoo-dev "create equipment_tracking module with equipment model, maintenance requests, and scheduling"`
  - Expected:
    - Mode detected: Full
    - Codebase research with indexer
    - Detailed architecture proposal
    - 1 approval request
    - Phased implementation
    - Automatic verification
    - Documentation prompt
    - Time: 20-25 minutes
  - Actual time: _______ minutes

- [ ] **Test**: `/odoo-dev "create warranty management module with warranty registration, claims, and expiry tracking"`
  - Expected:
    - Full Mode
    - Multiple models created
    - Views, menus, security configured
    - Integration with existing modules
    - Time: 20-25 minutes
  - Actual time: _______ minutes

#### Search Mode (Questions)

- [ ] **Test**: `/odoo-dev "what is sale.order"`
  - Expected:
    - Mode detected: Search
    - Instant indexer query
    - Detailed model info
    - Time: <2 seconds
  - Actual time: _______ seconds

- [ ] **Test**: `/odoo-dev "show me fields in project.task"`
  - Expected:
    - Search Mode
    - Instant field list
    - Time: <2 seconds
  - Actual time: _______ seconds

#### Mode Detection Accuracy

- [ ] Simple task → Quick Mode (5 tests)
- [ ] Complex task → Full Mode (5 tests)
- [ ] Question → Search Mode (5 tests)
- [ ] Ambiguous task → Asks for clarification

#### Validation Integration

- [ ] **Test**: Add field with invalid comodel
  - Expected: Indexer catches error, shows available models

- [ ] **Test**: Reference non-existent XML ID
  - Expected: Indexer suggests correct XML ID with module prefix

- [ ] **Test**: Create duplicate field
  - Expected: Indexer warns field already exists

### 2.3 `/odoo-scaffold` Command

- [ ] **Test**: `/odoo-scaffold my_custom_module`
  - Expected:
    - Module created in odoo/custom/src/odoo-sh/
    - All required files present
    - Validated with indexer
    - Ready for development

- [ ] **Test**: Scaffold with dependency
  - Expected: Dependency validated before creation

- [ ] **Test**: Scaffold existing module
  - Expected: Error, suggests extension instead

### 2.4 `/odoo-test` Command

- [ ] **Test**: `/odoo-test sale`
  - Expected: Runs all sale module tests, reports results

- [ ] **Test**: `/odoo-test sale.order`
  - Expected: Runs model-specific tests

- [ ] **Test**: `/odoo-test --coverage sale`
  - Expected: Test coverage report

---

## 3. Agent Tests

### 3.1 `odoo-developer` Agent

#### Proactive Triggering

- [ ] **Test**: User says "create partner contact module"
  - Expected: Agent auto-triggered (no Task() call needed)

- [ ] **Test**: User says "add field to model"
  - Expected: Agent auto-triggered

- [ ] **Test**: User says "implement warranty tracking"
  - Expected: Agent auto-triggered

#### Architecture Proposals

- [ ] **Test**: Simple task architecture (inline, brief)
  - Expected: 2-3 lines, clear, immediate approval flow

- [ ] **Test**: Complex task architecture (detailed)
  - Expected: Comprehensive proposal with phases, dependencies

- [ ] **Test**: User requests changes to architecture
  - Expected: Agent adjusts, re-proposes, iterates

#### Auto-Validation

- [ ] **Test**: Agent validates all model references with indexer
  - Expected: Real-time checkmarks, <2s per validation

- [ ] **Test**: Agent validates field types
  - Expected: Correct comodel detection

- [ ] **Test**: Agent validates XML IDs
  - Expected: Full module.xml_id format used

#### Implementation Quality

- [ ] **Test**: Generated code follows Odoo conventions
  - PEP 8 compliance
  - Proper field definitions
  - Correct view inheritance
  - Security rules present

- [ ] **Test**: Generated tests are comprehensive
  - Model creation tests
  - Field validation tests
  - Method tests
  - Access rights tests

### 3.2 `odoo-verifier` Agent

#### Automatic Invocation

- [ ] **Test**: Verifier called automatically after developer
  - Expected: No manual Task() call needed

- [ ] **Test**: Verifier runs on both Quick and Full modes
  - Expected: Appropriate validation depth

#### Validation Coverage

- [ ] **Test**: Structure validation
  - __manifest__.py present and valid
  - Required files present
  - Module structure correct

- [ ] **Test**: Security validation
  - Access rights defined
  - Record rules present (if needed)
  - Groups properly referenced

- [ ] **Test**: Code validation
  - Python syntax correct
  - XML well-formed
  - Field definitions valid
  - View inheritance correct

- [ ] **Test**: Reference validation
  - All model references exist
  - All field references valid
  - All XML ID references correct

- [ ] **Test**: Test validation
  - Tests present
  - Tests executable
  - Coverage adequate

#### Inline Reporting

- [ ] **Test**: All tests pass
  - Expected: Inline summary, no file created, auto-proceed

- [ ] **Test**: Some tests fail
  - Expected: Detailed report file created, issues listed

- [ ] **Test**: Critical failures
  - Expected: Report with fixes suggested

#### Auto-Proceed

- [ ] **Test**: Verification passes
  - Expected: Continues without approval

- [ ] **Test**: Verification fails
  - Expected: Asks user: fix automatically / review / skip

### 3.3 `odoo-documenter` Agent

- [ ] **Test**: User requests documentation
  - Expected: Creates README, USER-GUIDE, DEVELOPER-GUIDE

- [ ] **Test**: User skips documentation
  - Expected: Agent not called, process completes

- [ ] **Test**: Documentation quality
  - Expected: Comprehensive, accurate, well-formatted

---

## 4. Skill Tests

### 4.1 `odoo-indexer` Skill

#### Proactive Usage

- [ ] **Test**: User asks "what is sale.order"
  - Expected: Skill auto-used without Task() call

- [ ] **Test**: User asks "find partner fields"
  - Expected: Skill auto-used

- [ ] **Test**: User asks about model that doesn't exist
  - Expected: Skill used, returns "not found" with suggestions

#### Performance

- [ ] **Exact search**: <20ms
- [ ] **Wildcard search**: <100ms
- [ ] **Attribute search**: <150ms
- [ ] **Module stats**: <50ms

#### Accuracy

- [ ] **Test**: Search returns correct model details
  - All fields listed
  - Types correct
  - Relationships accurate

- [ ] **Test**: Search finds all matches
  - Wildcard patterns work
  - Case-insensitive search works

#### Tool Wrappers

- [ ] `search_model.sh` works correctly
- [ ] `search_field.sh` works correctly
- [ ] `validate_field.sh` works correctly
- [ ] `validate_xml_id.sh` works correctly
- [ ] `get_model_details.sh` works correctly
- [ ] `update_index.sh` works correctly

---

## 5. Workflow Tests

### 5.1 Quick Mode Workflow

**End-to-End Test**: Simple field addition

1. **User Request**: "add phone field to res.partner"

2. **Expected Flow**:
   - ⏱️ Start timer
   - 🎯 Mode detected: Quick
   - 💻 Developer agent triggered
   - 📐 Architecture proposed inline
   - ✅ User approves (Approval #1)
   - 💻 Implementation with real-time validation
   - 🧪 Verifier runs automatically
   - ✅ Verification passes, auto-proceeds
   - ⏱️ Stop timer

3. **Validation**:
   - [ ] Mode detection correct
   - [ ] 1 approval only
   - [ ] Implementation correct
   - [ ] Verification automatic
   - [ ] Total time: 5-7 minutes
   - [ ] Actual time: _______ minutes

### 5.2 Full Mode Workflow

**End-to-End Test**: New module creation

1. **User Request**: "create asset_tracking module for company assets with depreciation"

2. **Expected Flow**:
   - ⏱️ Start timer
   - 🎯 Mode detected: Full
   - 🔍 Developer researches with indexer
   - 📐 Detailed architecture proposed
   - ✅ User approves (Approval #1)
   - 💻 Phase 1: Models created
   - 💻 Phase 2: Views created
   - 💻 Phase 3: Security configured
   - 🧪 Verifier runs automatically
   - ✅ Verification passes
   - 📚 Documentation prompted
   - ✅ User decides (Approval #2 - optional)
   - ⏱️ Stop timer

3. **Validation**:
   - [ ] Mode detection correct
   - [ ] 1-2 approvals max
   - [ ] Comprehensive implementation
   - [ ] All components present
   - [ ] Verification automatic
   - [ ] Total time: 20-25 minutes
   - [ ] Actual time: _______ minutes

### 5.3 Search Mode Workflow

**End-to-End Test**: Information query

1. **User Request**: "what fields does sale.order have?"

2. **Expected Flow**:
   - ⏱️ Start timer
   - 🔍 Mode detected: Search
   - 📊 Indexer queried directly
   - 📋 Results formatted and displayed
   - ⏱️ Stop timer

3. **Validation**:
   - [ ] Mode detection correct
   - [ ] 0 approvals
   - [ ] Accurate results
   - [ ] Total time: <2 seconds
   - [ ] Actual time: _______ ms

---

## 6. Integration Tests

### 6.1 Multi-Step Workflows

- [ ] **Test**: Create module → Add field → Update view → Test
  - Expected: Seamless flow, minimal approvals

- [ ] **Test**: Search model → Extend model → Verify
  - Expected: Indexer used for search and validation

- [ ] **Test**: Create module → Fail verification → Fix → Verify again
  - Expected: Iterative fixing works

### 6.2 Cross-Agent Coordination

- [ ] Developer → Verifier → Documenter flow
- [ ] Developer uses indexer for validation
- [ ] Verifier uses indexer for checks
- [ ] No redundant approvals

### 6.3 Error Recovery

- [ ] **Test**: Validation fails → User chooses "fix automatically"
  - Expected: Developer fixes, verifier runs again, succeeds

- [ ] **Test**: Invalid field type
  - Expected: Caught by indexer, corrected before implementation

- [ ] **Test**: Missing dependency
  - Expected: Detected during architecture, added automatically

---

## 7. Performance Tests

### 7.1 Speed Benchmarks

Compare v1.x vs v2.0:

| Task | v1.x Time | v2.0 Target | v2.0 Actual | Pass/Fail |
|------|-----------|-------------|-------------|-----------|
| Setup | 15-30 min | 2-5 min | _____ min | ⬜ |
| Simple field add | 30-60 min | 5-7 min | _____ min | ⬜ |
| Complex module | 50-80 min | 20-25 min | _____ min | ⬜ |
| Model search | 2-5 sec | <100ms | _____ ms | ⬜ |
| Field validation | 30-60 sec | <2 sec | _____ sec | ⬜ |

### 7.2 Token Efficiency

- [ ] **Test**: Search with indexer vs Read tool
  - Indexer: ~500 tokens
  - Read tool: ~10,000 tokens
  - Expected: 95% reduction

- [ ] **Test**: Inline architecture vs spec file
  - Inline: ~2,000 tokens
  - Spec file: ~5,000 tokens
  - Expected: 60% reduction

### 7.3 Automation Rate

- [ ] **Manual commands in v1.x**: ~10 per workflow
- [ ] **Manual commands in v2.0**: ~1 per workflow
- [ ] **Expected**: 90% automation

---

## 8. Regression Tests

### 8.1 Feature Preservation

Ensure v1.x features are preserved:

- [ ] **Module scaffolding**: Still works, enhanced
- [ ] **Code generation**: Quality maintained
- [ ] **Validation**: Coverage same or better
- [ ] **Testing**: Coverage same or better
- [ ] **Documentation**: Quality maintained
- [ ] **Best practices**: All enforced

### 8.2 Quality Standards

- [ ] **PEP 8 compliance**: All generated Python code
- [ ] **XML formatting**: Well-formed, indented
- [ ] **Security**: Access rights always defined
- [ ] **Tests**: Comprehensive coverage
- [ ] **Documentation**: Clear and complete

### 8.3 Edge Cases

- [ ] **Empty module**: Scaffolds correctly
- [ ] **Complex inheritance**: Multiple _inherit works
- [ ] **Many2many fields**: Through table created
- [ ] **Computed fields**: Dependencies specified
- [ ] **Translated fields**: Properly marked

---

## 9. Documentation Tests

### 9.1 Accuracy

- [ ] **INSTALLATION.md**: All steps work
- [ ] **USAGE_GUIDE.md**: Examples executable
- [ ] **MIGRATION.md**: Migration steps complete
- [ ] **README.md**: Quick start accurate
- [ ] **CHANGELOG.md**: All changes documented

### 9.2 Completeness

- [ ] All commands documented
- [ ] All agents documented
- [ ] All skills documented
- [ ] Troubleshooting covers common issues
- [ ] Examples for all workflows

---

## 10. User Acceptance Tests

### 10.1 First-Time User

- [ ] Can install plugin in <5 minutes
- [ ] Can run first development task in <10 minutes
- [ ] Understands workflow without extensive reading
- [ ] Gets helpful error messages
- [ ] Can find help when stuck

### 10.2 Experienced User (v1.x)

- [ ] Can migrate from v1.x successfully
- [ ] Finds v2.0 faster and easier
- [ ] Misses no v1.x features
- [ ] Appreciates reduced approvals
- [ ] Adapts to new workflow quickly

### 10.3 Power User

- [ ] Can customize workflows
- [ ] Can extend with new commands
- [ ] Can debug issues
- [ ] Can contribute improvements
- [ ] Can integrate with other tools

---

## 11. Cross-Platform Tests

### 11.1 Linux

- [ ] Ubuntu 20.04+
- [ ] Debian 11+
- [ ] Fedora 35+
- [ ] All commands work
- [ ] All paths resolve correctly

### 11.2 macOS

- [ ] macOS 11 (Big Sur)+
- [ ] macOS 12 (Monterey)+
- [ ] macOS 13 (Ventura)+
- [ ] All commands work
- [ ] Homebrew integration works

---

## 12. Stress Tests

### 12.1 Large Codebase

- [ ] **Test**: 200+ modules
  - Index build time: <10 minutes
  - Search performance: <100ms
  - Memory usage: <500MB

### 12.2 Concurrent Operations

- [ ] Multiple searches in parallel
- [ ] Development during indexing
- [ ] No corruption or conflicts

---

## Test Execution

### Pre-Test Setup

1. [ ] Clean test environment prepared
2. [ ] Test data ready (sample Odoo installation)
3. [ ] Metrics collection tools ready
4. [ ] Test accounts configured

### Test Execution Order

1. **Day 1**: Installation & Setup (Section 1)
2. **Day 2**: Commands (Section 2)
3. **Day 3**: Agents & Skills (Sections 3-4)
4. **Day 4**: Workflows & Integration (Sections 5-6)
5. **Day 5**: Performance & Regression (Sections 7-8)

### Test Reporting

For each test:
- ✅ Pass
- ⚠️ Pass with warnings
- ❌ Fail (document issue)
- ⏭️ Skipped (document reason)

### Bug Tracking

For failures:
1. Document exact steps to reproduce
2. Record expected vs actual behavior
3. Note severity (Critical/High/Medium/Low)
4. Create GitHub issue with details
5. Retest after fix

---

## Success Criteria

### Must Pass (Blocking)

- [ ] All installation tests pass
- [ ] All command core functionality works
- [ ] All agents trigger correctly
- [ ] Mode detection 90%+ accurate
- [ ] Performance targets met (within 20%)
- [ ] No quality regressions
- [ ] Documentation accurate

### Should Pass (High Priority)

- [ ] All edge cases handled
- [ ] Error messages helpful
- [ ] Cross-platform compatibility
- [ ] Stress tests pass

### Nice to Have (Medium Priority)

- [ ] Performance exceeds targets by 20%+
- [ ] Automation rate >90%
- [ ] User acceptance scores 9/10+

---

## Test Summary Report

### Overview

- **Total Tests**: _______
- **Passed**: _______
- **Failed**: _______
- **Skipped**: _______
- **Pass Rate**: _______%

### Performance Results

- **Setup Time**: _______ min (Target: 2-5 min)
- **Simple Tasks**: _______ min (Target: 5-7 min)
- **Complex Tasks**: _______ min (Target: 20-25 min)
- **Search Time**: _______ ms (Target: <100ms)

### Quality Results

- **Code Quality**: ⬜ Pass ⬜ Fail
- **Test Coverage**: ⬜ Pass ⬜ Fail
- **Documentation**: ⬜ Pass ⬜ Fail
- **User Experience**: ⬜ Pass ⬜ Fail

### Recommendation

⬜ **Approve for Release** - All critical tests pass
⬜ **Approve with Fixes** - Minor issues to address
⬜ **Do Not Release** - Critical issues present

---

## Sign-Off

**Tester**: _______________________
**Date**: _______________________
**Version Tested**: 2.0.0-beta.1
**Environment**: _______________________

---

*Last Updated: 2025-11-06*
