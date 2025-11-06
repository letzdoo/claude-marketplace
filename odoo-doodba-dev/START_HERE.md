# 🚀 Start Here - Odoo Doodba Dev Plugin v2.0

Quick reference guide to get you started with v2.0 in minutes.

---

## ⚡ Quick Start (5 Minutes)

### 1. Install the Plugin

```bash
# Plugin is already in your Claude Code marketplace
# Just ensure you're in your Odoo project directory
cd /path/to/your/odoo/project
```

### 2. Run Automated Setup

```bash
/odoo-setup
```

This single command will:
- ✅ Check prerequisites (Python, Docker, Doodba)
- ✅ Install uv if needed
- ✅ Detect your Odoo directory
- ✅ Build the code indexer database
- ✅ Verify everything works

**Time**: 2-5 minutes

### 3. Start Developing

```bash
# Simple task (5-7 min)
/odoo-dev "add priority field to project.task with values: low, normal, high, urgent"

# Complex feature (20-25 min)
/odoo-dev "create equipment_tracking module to manage company equipment"

# Quick search (<2 sec)
/odoo-search "what is sale.order"
```

---

## 🎯 Core Commands (Just 5!)

| Command | Use When | Time |
|---------|----------|------|
| `/odoo-setup` | First time setup or troubleshooting | 2-5 min |
| `/odoo-dev` | Building features (auto-detects complexity) | 5-25 min |
| `/odoo-search` | Finding info about models, fields, views | <2 sec |
| `/odoo-scaffold` | Creating new module structure | 2-3 min |
| `/odoo-test` | Running tests on modules | Varies |

**90% of your work**: `/odoo-dev` and `/odoo-search`

---

## 💡 How v2.0 Works

### Three Intelligent Modes

`/odoo-dev` automatically detects what you need:

**🚀 Quick Mode** (Simple tasks: 5-7 minutes)
```bash
/odoo-dev "add description field to res.partner"
```
- Inline architecture proposal
- 1 approval
- Direct implementation
- Auto-verification

**🏗️ Full Mode** (Complex features: 20-25 minutes)
```bash
/odoo-dev "create warranty management module with claims and tracking"
```
- Research with indexer
- Detailed architecture
- 1 approval
- Phased implementation
- Auto-verification
- Optional documentation

**🔍 Search Mode** (Questions: <2 seconds)
```bash
/odoo-dev "what fields does sale.order have"
```
- Instant indexer query
- No approvals
- Immediate answer

### No More Manual Steps

v2.0 is **90% automated**:
- ✅ Agents auto-trigger when you describe tasks
- ✅ Indexer auto-searches for code information
- ✅ Validation happens automatically (no separate command)
- ✅ Testing runs automatically (no separate command)
- ✅ One approval for simple tasks (vs 5 in v1.x)

---

## 📖 Common Workflows

### Workflow 1: Add Field to Existing Model

```bash
# Just describe what you want
/odoo-dev "add phone field (Char) to res.partner, add to form view"

# That's it! Plugin will:
# 1. Propose inline architecture (30 sec)
# 2. You approve (1 click)
# 3. Implement with validation (4 min)
# 4. Auto-verify and test (1 min)
# Total: 5-7 minutes, 1 approval
```

### Workflow 2: Create New Module

```bash
/odoo-dev "create asset_tracking module to track company assets with depreciation calculations"

# Plugin will:
# 1. Research existing modules with indexer (1 min)
# 2. Propose detailed architecture (1 min)
# 3. You approve (1 click)
# 4. Create models, views, security, tests (15 min)
# 5. Auto-verify everything (2 min)
# 6. Offer to create documentation (optional)
# Total: 20-25 minutes, 1-2 approvals
```

### Workflow 3: Understand Existing Code

```bash
# Search for model info
/odoo-search "what is sale.order"

# Find fields
/odoo-search "what fields does res.partner have"

# Locate views
/odoo-search "find partner form view"

# List modules
/odoo-search "list modules"

# All searches: <100ms, 0 approvals
```

### Workflow 4: Extend Existing Module

```bash
/odoo-dev "extend sale.order with warranty_id field linking to product.warranty"

# Plugin will:
# 1. Search for sale.order with indexer (instant)
# 2. Propose extension architecture (30 sec)
# 3. You approve (1 click)
# 4. Create extension module (5 min)
# 5. Auto-verify (1 min)
# Total: 7-8 minutes
```

---

## 🎓 What's Different from v1.x?

If you're migrating from v1.x, here's what changed:

### Commands Changed

| Old v1.x | New v2.0 | Why |
|----------|----------|-----|
| `/odoo-workflow` | `/odoo-dev` | Smarter, auto-detects mode |
| `/odoo-validate` | (automatic) | Happens during `/odoo-dev` |
| `/odoo-info` | `/odoo-search` | Faster, natural language |
| `/odoo-addons` | `/odoo-search` | Unified search |
| `/odoo-shell` | (removed) | Use `invoke shell` |
| `/odoo-logs` | (removed) | Use `invoke logs` |

### Workflow Simplified

**v1.x**: 5 stages, 5 approvals, 30-80 minutes
```
Analysis → Architecture → Validate → Implement → Test → Document
  ↓          ↓              ↓          ↓         ↓       ↓
Approve    Approve        Approve    Approve   Approve Approve
```

**v2.0**: 3 stages, 1-2 approvals, 5-25 minutes
```
Inline Proposal → Implement (with auto-validation) → Auto-verify
       ↓                                                   ↓
    Approve                                      (Optional: Document)
```

### Speed Improvements

- **Setup**: 15-30 min → 2-5 min (75% faster)
- **Simple tasks**: 30-60 min → 5-7 min (88% faster)
- **Complex tasks**: 50-80 min → 20-25 min (65% faster)
- **Searches**: 2-5 sec → <100ms (95% faster)

---

## 🔧 Troubleshooting

### "Indexer not found"

```bash
# Rebuild the index
/odoo-setup
```

### "Module not found in search"

```bash
# Update the index
cd ~/.odoo-indexer
uv run scripts/update_index.py --full
```

### "Command not working"

```bash
# Check you're in the right directory
pwd  # Should show your Odoo project

# Verify plugin installation
# Commands should appear in Claude Code
```

### "Performance seems slow"

```bash
# Check index status
ls -lh ~/.odoo-indexer/odoo_indexer.sqlite3

# Should be 10-50 MB
# If missing or 0 bytes, run /odoo-setup
```

---

## 📚 Learn More

### For Quick Reference

- **This file** - You're reading it! Quick start and common patterns

### For Installation

- **[INSTALLATION.md](INSTALLATION.md)** - Detailed setup guide, prerequisites, troubleshooting

### For Migration

- **[MIGRATION.md](MIGRATION.md)** - v1.x → v2.0 upgrade guide, breaking changes

### For Examples

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Comprehensive examples, best practices, workflows

### For Changes

- **[CHANGELOG.md](CHANGELOG.md)** - Complete list of what's new in v2.0

### For Testing

- **[TEST_CHECKLIST.md](TEST_CHECKLIST.md)** - Comprehensive testing guide

### For General Info

- **[README.md](README.md)** - Overview, features, philosophy

---

## 💪 Pro Tips

### 1. Trust the Automation

Let the plugin use its tools automatically. Don't manually run bash commands for searches - the indexer is 95% faster.

### 2. Be Descriptive

The smarter your request, the better the result:

❌ **Vague**: "add field"
✅ **Clear**: "add priority (Selection) to project.task with values: low, normal, high, urgent"

### 3. Use Search Liberally

Before developing, search to understand:

```bash
/odoo-search "what is project.task"
/odoo-dev "add priority field..."
```

### 4. Let Verification Auto-Proceed

When verification passes, it auto-continues. Don't wait for prompts.

### 5. Quick Tasks Stay Quick

Simple 1-2 field additions get Quick Mode automatically. No need to specify.

---

## 🎯 Your First Task

Try this now to see v2.0 in action:

```bash
# 1. Ensure setup is complete
/odoo-setup

# 2. Search for a model (instant)
/odoo-search "what is res.partner"

# 3. Make a simple change (5-7 min)
/odoo-dev "add notes field (Text) to res.partner form view"

# You'll see:
# - Instant mode detection (Quick)
# - Brief architecture proposal
# - One approval request
# - Real-time implementation with ✓ checkmarks
# - Automatic verification
# - Success in ~6 minutes!
```

---

## ❓ FAQ

**Q: Do I need to specify Quick vs Full mode?**
A: No! `/odoo-dev` auto-detects based on task complexity.

**Q: Can I still create spec files?**
A: For complex features, yes. But simple tasks use inline proposals now.

**Q: Where did `/odoo-validate` go?**
A: Validation is automatic during `/odoo-dev`. No separate command needed.

**Q: How do I know what models exist?**
A: Use `/odoo-search "list modules"` or search for specific models.

**Q: Can I customize the workflow?**
A: Advanced users can modify agent files, but defaults work great for 90% of cases.

**Q: What if indexer is slow?**
A: Indexer queries are <100ms. If slow, rebuild: `/odoo-setup`

**Q: Does v2.0 maintain code quality?**
A: Yes! 100% of v1.x validation and testing is preserved.

---

## 🚀 Next Steps

1. ✅ **Run** `/odoo-setup` (if you haven't)
2. ✅ **Try** a search: `/odoo-search "what is sale.order"`
3. ✅ **Build** something: `/odoo-dev "add field..."`
4. ✅ **Read** [USAGE_GUIDE.md](USAGE_GUIDE.md) for advanced patterns
5. ✅ **Share** feedback and suggestions

---

## 📞 Support

- **Installation issues**: See [INSTALLATION.md](INSTALLATION.md)
- **Migration questions**: See [MIGRATION.md](MIGRATION.md)
- **Usage examples**: See [USAGE_GUIDE.md](USAGE_GUIDE.md)
- **Bug reports**: Open GitHub issue with details

---

**Welcome to v2.0! Happy coding! 🎉**

---

*Last Updated: 2025-11-06*
*Version: 2.0.0*
