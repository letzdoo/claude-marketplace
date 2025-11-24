# Centralized Reasoning Bank - User Guide

## Overview

The Centralized Reasoning Bank extends the local reasoning bank to enable **knowledge sharing** across the community. When you enable central sync, patterns you learn (with your consent) are shared with a central knowledge base, and you benefit from patterns discovered by other developers.

**Key Benefits:**
- 🌐 **Learn from the community** - Access patterns discovered by other Odoo developers
- 🤝 **Contribute back** - Share your learnings to help others avoid the same issues
- 🔒 **Privacy-first** - You control what gets shared, with automatic PII redaction
- 📈 **Continuously improving** - The knowledge base gets better with every contribution

## Quick Start

### 1. Enable Central Sync

Edit `config.yaml` and set:

```yaml
reasoningbank:
  central:
    enabled: true
    api_url: "https://reasoningbank.example.com/api/v1"
    api_key: "${REASONINGBANK_API_KEY}"
```

Set your API key as an environment variable:

```bash
export REASONINGBANK_API_KEY="your_api_key_here"
```

### 2. Initialize Database

Run the migration to add central sync tables:

```bash
rb-init-central
```

This adds:
- `sync_queue` - Upload queue with retry logic
- `user_consent` - Consent tracking
- `community_patterns` - Downloaded community patterns

### 3. Configure Consent Mode

Choose how you want to handle pattern sharing in `config.yaml`:

```yaml
reasoningbank:
  central:
    consent:
      mode: "ask_each_time"  # Options: ask_each_time, always_allow, always_deny, domain_specific
```

**Consent Modes:**

- **`ask_each_time`** (Recommended) - Prompt for consent before each upload
- **`always_allow`** - Auto-share all patterns (respects block_domains)
- **`always_deny`** - Never share patterns (local-only mode)
- **`domain_specific`** - Auto-share specific domains, ask for others

### 4. Start Using

That's it! The system will now:
1. **Judge** your task trajectories (success/failure)
2. **Distill** patterns from what you learned
3. **Request consent** before sharing (based on your mode)
4. **Upload** approved patterns to the central service
5. **Download** relevant community patterns for your work

## How It Works

### Pattern Creation Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. You complete a task (e.g., fix an Odoo N+1 query issue)  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Post-hook judges: Was it successful?                     │
│    └─ Label: Success/Failure, Confidence: 0.85             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. System distills pattern from your trajectory:            │
│    "N+1 Query in Computed Field"                            │
│    - Problem: search() in loop → N+1 queries                │
│    - Fix: Use read_group() before loop                       │
│    - Recognition: @api.depends + loop + search              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Pattern saved locally (always)                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Consent check (if central sync enabled):                 │
│                                                              │
│    ┌────────────────────────────────────────────┐           │
│    │ 🌐 New Pattern Ready to Share              │           │
│    │                                            │           │
│    │ Pattern: N+1 Query in Computed Field      │           │
│    │ Domain: odoo.orm                           │           │
│    │ Confidence: 0.85                           │           │
│    │                                            │           │
│    │ [s] Share  [l] Keep Local  [a] Always     │           │
│    └────────────────────────────────────────────┘           │
│                                                              │
│    You choose: [s] Share ✅                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Pattern added to upload queue                            │
│    Uploaded in background with retry logic                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. Pattern anonymized and sent to central service           │
│    - PII redacted (file paths, usernames)                   │
│    - Remote ID assigned (e.g., cp_01HZX...)                 │
│    - Available to community                                 │
└─────────────────────────────────────────────────────────────┘
```

### Pattern Retrieval Flow

When you start a new task, the system:

1. **Retrieves local patterns** - Patterns you've learned (weight: 1.0)
2. **Queries central service** - Relevant community patterns (weight: 0.7)
3. **Blends results** - Combines both using MMR for diversity
4. **Injects into context** - Top 5 patterns added to your system prompt
5. **You benefit** - Avoid issues others have already solved

## Configuration Options

### Consent Settings

```yaml
reasoningbank:
  central:
    consent:
      mode: "ask_each_time"

      # For domain_specific mode
      share_domains:
        - "odoo.orm"          # Auto-share ORM patterns
        - "odoo.performance"  # Auto-share performance patterns

      block_domains:
        - "odoo.security"     # Never auto-share security patterns

      # Auto-approve high confidence patterns
      auto_approve_high_confidence: true
      min_confidence_auto: 0.90

      # UI options
      show_preview: true              # Show pattern before asking
      remember_choice: true           # Allow "always share this domain"

      # Privacy
      anonymize_paths: true           # Redact file paths
      anonymize_org: true             # Redact org info
```

### Sync Settings

```yaml
reasoningbank:
  central:
    sync:
      upload_enabled: true
      download_enabled: true
      mode: "hybrid"                  # hybrid, upload_only, download_only

      batch_size: 10                  # Patterns per batch upload
      retry_max: 5                    # Max upload retries
      retry_backoff_base: 2           # Exponential backoff (seconds)

      sync_interval: 21600            # Auto-sync every 6 hours
      offline_queue_max: 1000         # Max queued patterns
```

### Community Pattern Retrieval

```yaml
reasoningbank:
  central:
    retrieval:
      include_community: true
      community_weight: 0.7           # vs. 1.0 for local patterns

      # Quality filters
      min_community_confidence: 0.65
      min_community_upvotes: 3

      # Caching
      cache_community_patterns: true
      cache_ttl: 86400                # 24 hours
```

### Privacy Controls

```yaml
reasoningbank:
  central:
    privacy:
      redact_file_paths: true
      redact_usernames: true
      redact_ips: true

      # Custom patterns to redact
      redact_custom_patterns:
        - '\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'  # Emails

      hash_task_ids: true             # Hash task IDs before upload
```

## CLI Commands

### Check Sync Status

```bash
rb-sync-status
```

Output:
```
==================================================
Central Reasoning Bank - Sync Status
==================================================

📋 Configuration:
   Status: ✅ Enabled
   API URL: https://reasoningbank.example.com/api/v1
   User ID: your_username
   Consent Mode: ask_each_time

📤 Upload Status:
   Upload Enabled: ✅ Yes
   Last Upload: 2 hours ago
   Queue:
      Pending: 0
      Success: 47
      Failed: 0

📥 Download Status:
   Download Enabled: ✅ Yes
   Last Download: 30 minutes ago
   Cached Patterns: 203

🔐 Consent Statistics:
   Total Requests: 52
   Approved: 47 (90.4%)
   Denied: 5

🌐 Remote Service:
   Status: ✅ Reachable
   Your Statistics:
      Patterns Contributed: 47
      Patterns Downloaded: 203
      Upvotes Received: 156
      Reputation: 342
```

### Manual Sync

Upload pending patterns:
```bash
rb-sync --upload
```

Download community patterns:
```bash
rb-sync --download
```

Full bidirectional sync:
```bash
rb-sync --full
```

Download specific domain patterns:
```bash
rb-sync --download --domains odoo.orm odoo.security --limit 50
```

Search and download:
```bash
rb-sync --download --query "N+1 query performance" --limit 10
```

### Database Migration

Initialize central sync tables:
```bash
rb-init-central
```

Dry run (see what would change):
```bash
rb-init-central --dry-run
```

Rollback (for testing):
```bash
rb-init-central --rollback
```

## Privacy & Security

### What Gets Shared

When you approve a pattern for sharing, the system:

✅ **Shares:**
- Pattern title and description
- Generalized problem and solution
- Odoo domain and tags
- Confidence score and usage count

❌ **Never shares:**
- Your file paths (redacted to `<project>`)
- Your username (anonymized)
- IP addresses
- Email addresses
- Task-specific variable names
- Organization-specific details

### How Redaction Works

Before upload, patterns are automatically sanitized:

```python
# Original
"Fixed N+1 in /home/john/mycompany/odoo/modules/sale/models/sale_order.py"

# After redaction
"Fixed N+1 in <project>/modules/sale/models/sale_order.py"
```

### Consent Control

You have full control:

- **Review before sharing** - See exactly what will be uploaded
- **Selective sharing** - Choose which domains to share
- **Revoke at any time** - Keep patterns local-only
- **Per-pattern decisions** - Approve/deny each pattern individually

### Data Ownership

- **Your local patterns** - Always yours, stored locally
- **Uploaded patterns** - You retain ownership, can request deletion
- **Community patterns** - Cached locally for offline use
- **No lock-in** - Disable central sync anytime

## Troubleshooting

### "Central sync is not enabled"

**Solution:** Edit `config.yaml` and set:
```yaml
reasoningbank:
  central:
    enabled: true
```

### "No API key configured"

**Solution:** Set environment variable:
```bash
export REASONINGBANK_API_KEY="your_key"
```

Or configure in `config.yaml`:
```yaml
reasoningbank:
  central:
    api_key: "your_key"  # Not recommended - use env var
```

### "Authentication failed"

**Causes:**
- Invalid API key
- Expired key
- Network issues

**Solution:** Check your API key and network connection:
```bash
curl -I https://reasoningbank.example.com/api/v1/health
```

### "Upload failed: Rate limit exceeded"

**Solution:** The system will automatically retry with exponential backoff. You can check retry status:
```bash
rb-sync-status
```

### "Remote service unreachable"

**Causes:**
- Network connectivity issue
- Service down
- Firewall blocking

**Solution:** The system operates in offline mode, queuing patterns for later upload. Check:
```bash
rb-sync-status  # See queued patterns
rb-sync --upload  # Retry upload when online
```

## Advanced Usage

### Custom Consent Workflow

Create a custom consent handler:

```python
from scripts.consent_manager import ConsentManager

class MyConsentManager(ConsentManager):
    async def request_consent(self, pattern_id, pattern_data, confidence):
        # Custom logic here
        # E.g., integrate with Slack, email, web dashboard
        return consent_given, consent_mode
```

### Batch Operations

Upload all pending patterns:
```bash
rb-sync --upload
```

Download patterns for specific task:
```bash
rb-sync --download --query "your task description" --limit 20
```

### Monitoring

Check upload queue:
```bash
rb-sync-status --json | jq '.sync.queue'
```

Get consent statistics:
```bash
rb-sync-status --json | jq '.consent'
```

### Offline Mode

The system works offline:
1. Patterns are always saved locally first
2. Upload queue stores pending patterns
3. When online, patterns sync automatically
4. No data loss in offline mode

## Best Practices

### 1. Start with `ask_each_time`

Begin with explicit consent for each pattern. Once comfortable, switch to `domain_specific` or `always_allow`.

### 2. Block Sensitive Domains

Always block security-related domains from auto-sharing:

```yaml
block_domains:
  - "odoo.security"
  - "odoo.authentication"
```

### 3. Review Before Sharing

Use `show_preview: true` to see patterns before approving.

### 4. Regular Syncs

Run periodic syncs to stay updated:

```bash
# Add to cron
0 */6 * * * rb-sync --full
```

### 5. Monitor Your Impact

Check your contribution stats:

```bash
rb-sync-status | grep "Your Statistics"
```

### 6. Give Feedback

Help improve community patterns:

```bash
# Upvote helpful pattern
rb-feedback cp_01HZX... --upvote

# Report incorrect pattern
rb-feedback cp_01HZX... --report "Incorrect for Odoo 17"
```

## FAQ

**Q: Will my code be uploaded?**
A: No. Only generalized patterns are uploaded, not your actual code.

**Q: Can I disable central sync?**
A: Yes. Set `central.enabled: false` in config.yaml.

**Q: What if I accidentally share something sensitive?**
A: Contact the service to delete your pattern. Also review your `block_domains` config.

**Q: Do I need to be online?**
A: No. The system works offline, queuing patterns for later upload.

**Q: How much does it cost?**
A: Check the service website for pricing. Typically free tier available.

**Q: Can I self-host the central service?**
A: Yes! The service API specification is documented in CENTRALIZED_DESIGN.md.

**Q: How do I opt out completely?**
A: Set `consent.mode: always_deny` or disable central sync entirely.

**Q: Are patterns versioned?**
A: Yes. Patterns track Odoo version compatibility (e.g., "16.0+").

## Support

- **Issues:** https://github.com/your-repo/issues
- **Docs:** https://reasoningbank.example.com/docs
- **Community:** https://reasoningbank.example.com/community

## License

MIT License - See LICENSE file for details.

---

**Made with ❤️ by the Odoo community**
