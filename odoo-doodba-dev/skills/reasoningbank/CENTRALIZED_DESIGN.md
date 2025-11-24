# Centralized Reasoning Bank - Design Document

## Overview

The Centralized Reasoning Bank extends the local reasoning bank implementation to enable knowledge sharing across users and organizations. Patterns learned by individual users are aggregated into a central knowledge base, creating a continuously improving repository of Odoo development wisdom.

## Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Code Agent                        │
│                                                              │
│  ┌────────────┐    ┌──────────────┐    ┌────────────────┐  │
│  │ Pre-Hook   │───▶│ Retrieval    │◀───│ Local Cache    │  │
│  │            │    │ (hybrid)     │    │ (SQLite)       │  │
│  └────────────┘    └──────────────┘    └────────────────┘  │
│                           │                      │          │
│                           ▼                      │          │
│  ┌────────────┐    ┌──────────────┐            │          │
│  │ Post-Hook  │───▶│ Distillation │            │          │
│  │            │    │              │            │          │
│  └────────────┘    └──────────────┘            │          │
│                           │                      │          │
│                           ▼                      │          │
│                    ┌──────────────┐             │          │
│                    │  User        │             │          │
│                    │  Consent     │             │          │
│                    │  Manager     │             │          │
│                    └──────────────┘             │          │
│                           │                      │          │
│                           ▼                      │          │
│                    ┌──────────────┐             │          │
│                    │  Sync        │◀────────────┘          │
│                    │  Manager     │                        │
│                    └──────────────┘                        │
│                           │                                 │
└───────────────────────────┼─────────────────────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   Remote     │
                    │   Service    │
                    │   API        │
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  Central     │
                    │  Knowledge   │
                    │  Base        │
                    └──────────────┘
```

### Component Responsibilities

#### 1. **User Consent Manager** (NEW)
- Prompts user for approval before uploading patterns
- Manages consent preferences (always allow, always deny, ask each time)
- Tracks which patterns have been shared
- Redacts sensitive information before sharing
- Provides opt-in/opt-out controls per domain

#### 2. **Sync Manager** (NEW)
- Queues patterns for upload to remote service
- Implements retry logic with exponential backoff
- Handles offline mode (queue for later)
- Manages bidirectional sync (upload + download)
- Resolves conflicts between local and remote patterns
- Batch uploads for efficiency

#### 3. **Remote Service API Client** (NEW)
- HTTP/gRPC client for central service
- Authentication and authorization
- Pattern upload/download operations
- User/organization identification
- Rate limiting and quota management

#### 4. **Enhanced Local Cache**
- Continues to store all patterns locally (SQLite)
- Adds sync metadata (uploaded, upload_timestamp, remote_id)
- Tracks pattern provenance (local vs. community)
- Maintains offline-first capability

#### 5. **Hybrid Retrieval**
- Retrieves from both local and community patterns
- Prioritizes local patterns (proven to work in user's context)
- Blends community patterns with local knowledge
- Flags community patterns as "suggested by community"

## Data Flow

### Pattern Creation & Upload Flow

```
1. Task Execution
   └─▶ Post-Hook triggered
       │
2. Judge & Distill (existing logic)
   └─▶ Pattern extracted
       │
3. Store Locally (existing logic)
   └─▶ Pattern saved to local SQLite
       │
4. Consent Check (NEW)
   ├─▶ Check user preferences
   │   ├─ "Always Allow" → Queue for upload
   │   ├─ "Always Deny" → Stop
   │   └─ "Ask Each Time" → Prompt user
   │       │
   │       └─▶ Show pattern preview
   │           ├─ User approves → Queue for upload
   │           └─ User denies → Mark as local-only
   │
5. Queue for Upload (NEW)
   └─▶ Sync Manager adds to upload queue
       │
6. Background Upload (NEW)
   ├─▶ Authenticate with remote service
   ├─▶ Send pattern with metadata
   ├─▶ Receive remote_id
   └─▶ Update local record with sync status
```

### Pattern Retrieval Flow

```
1. Pre-Hook triggered
   └─▶ Compute query embedding
       │
2. Retrieve Local Patterns
   └─▶ Score and rank (existing logic)
       │
3. Retrieve Community Patterns (NEW)
   ├─▶ Query remote service API
   ├─▶ Filter by relevance threshold
   └─▶ Cache locally for offline use
       │
4. Blend Results
   ├─▶ Combine local (weight 1.0) + community (weight 0.7)
   ├─▶ Apply MMR for diversity
   └─▶ Return top-k with provenance tags
```

## Database Schema Changes

### New Tables

#### `sync_queue` - Upload queue with retry management
```sql
CREATE TABLE sync_queue (
    id TEXT PRIMARY KEY,                  -- ULID
    pattern_id TEXT NOT NULL,             -- FK to patterns.id
    operation TEXT NOT NULL,              -- 'upload', 'update', 'delete'
    status TEXT NOT NULL,                 -- 'pending', 'uploading', 'success', 'failed'
    retry_count INTEGER DEFAULT 0,
    last_retry_at TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(pattern_id) REFERENCES patterns(id)
);
CREATE INDEX idx_sync_queue_status ON sync_queue(status);
CREATE INDEX idx_sync_queue_pattern ON sync_queue(pattern_id);
```

#### `user_consent` - Consent tracking
```sql
CREATE TABLE user_consent (
    id TEXT PRIMARY KEY,                  -- ULID
    pattern_id TEXT NOT NULL,             -- FK to patterns.id
    consent_given BOOLEAN NOT NULL,       -- User approved?
    consent_timestamp TEXT NOT NULL,
    consent_mode TEXT,                    -- 'explicit', 'global_allow', 'domain_allow'
    notes TEXT,
    FOREIGN KEY(pattern_id) REFERENCES patterns(id)
);
CREATE INDEX idx_consent_pattern ON user_consent(pattern_id);
```

#### `community_patterns` - Downloaded community patterns
```sql
CREATE TABLE community_patterns (
    id TEXT PRIMARY KEY,                  -- ULID (local)
    remote_id TEXT UNIQUE NOT NULL,       -- ID from central service
    pattern_type TEXT NOT NULL,
    pattern_data TEXT NOT NULL,           -- JSON
    confidence REAL NOT NULL,
    usage_count INTEGER DEFAULT 0,        -- Community usage
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    source_org TEXT,                      -- Anonymous org identifier
    downloaded_at TEXT NOT NULL,
    last_synced_at TEXT NOT NULL,
    is_cached BOOLEAN DEFAULT 1           -- For offline use
);
CREATE INDEX idx_community_type ON community_patterns(pattern_type);
CREATE INDEX idx_community_remote ON community_patterns(remote_id);
```

### Modified Tables

#### `patterns` - Add sync metadata
```sql
ALTER TABLE patterns ADD COLUMN is_uploaded BOOLEAN DEFAULT 0;
ALTER TABLE patterns ADD COLUMN remote_id TEXT UNIQUE;
ALTER TABLE patterns ADD COLUMN uploaded_at TEXT;
ALTER TABLE patterns ADD COLUMN consent_required BOOLEAN DEFAULT 1;
ALTER TABLE patterns ADD COLUMN is_local_only BOOLEAN DEFAULT 0;
```

## Remote Service API Specification

### REST API Endpoints

#### Authentication
```
POST /api/v1/auth/token
Request: { "api_key": "...", "user_id": "...", "org_id": "..." }
Response: { "access_token": "...", "expires_in": 3600 }
```

#### Pattern Upload
```
POST /api/v1/patterns
Headers: Authorization: Bearer <token>
Request: {
    "pattern": {
        "type": "odoo_antipattern",
        "data": { ... },                   // Pattern JSON
        "confidence": 0.85,
        "domain": "odoo.orm",
        "tags": ["performance", "orm"]
    },
    "metadata": {
        "user_consent": true,
        "created_at": "2025-11-24T...",
        "source_version": "1.0.0",
        "odoo_version": "16.0",
        "anonymize": true                  // Strip user-specific info
    }
}
Response: {
    "remote_id": "cp_01HZX...",
    "status": "accepted",
    "deduplicated": false,
    "similar_patterns": []                 // If duplicates found
}
```

#### Pattern Search
```
POST /api/v1/patterns/search
Headers: Authorization: Bearer <token>
Request: {
    "query": "N+1 query performance",
    "embedding": [0.123, ...],             // 1024-dim vector
    "k": 10,
    "filters": {
        "domain": "odoo.orm",
        "min_confidence": 0.6,
        "min_upvotes": 5,
        "odoo_version": "16.0+"
    }
}
Response: {
    "patterns": [
        {
            "remote_id": "cp_01HZX...",
            "type": "odoo_antipattern",
            "data": { ... },
            "confidence": 0.90,
            "usage_count": 145,
            "upvotes": 23,
            "downvotes": 2,
            "similarity_score": 0.87
        },
        ...
    ],
    "total": 145,
    "cached_until": "2025-11-24T..."
}
```

#### Pattern Feedback
```
POST /api/v1/patterns/{remote_id}/feedback
Request: {
    "feedback_type": "upvote" | "downvote" | "report",
    "comment": "This helped solve my issue",
    "context": { "task_id": "...", "outcome": "success" }
}
Response: { "status": "recorded" }
```

#### User Statistics
```
GET /api/v1/users/me/stats
Response: {
    "patterns_contributed": 47,
    "patterns_downloaded": 203,
    "upvotes_received": 156,
    "reputation_score": 342
}
```

## User Consent System

### Consent Modes

1. **Ask Each Time** (Default)
   - Prompt user for approval before each upload
   - Show pattern preview with sensitive data highlighted
   - Allow "Remember this choice" option

2. **Always Allow for Domain**
   - Auto-approve patterns in specific domains (e.g., "odoo.orm")
   - Still apply PII redaction

3. **Always Allow All**
   - Auto-approve all patterns
   - Apply privacy controls

4. **Always Deny**
   - Keep all patterns local-only
   - Disable central sync

### Consent UI Flow

```
┌─────────────────────────────────────────────────────┐
│ New Pattern Ready to Share                           │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Pattern: "N+1 Query in Computed Field"              │
│ Domain: odoo.orm                                     │
│ Confidence: 0.85                                     │
│                                                      │
│ Preview:                                             │
│ ┌────────────────────────────────────────────────┐  │
│ │ Problem: Using search() in loop within         │  │
│ │ computed field causes N+1 queries              │  │
│ │                                                │  │
│ │ Fix: Use read_group() or comodel_name.search()│  │
│ │ with domain before loop                        │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ This pattern will be anonymized and shared with     │
│ the community to help other developers.             │
│                                                      │
│ [ ] Remember this choice for odoo.orm patterns      │
│                                                      │
│ [Cancel]  [Keep Local Only]  [Share with Community] │
└─────────────────────────────────────────────────────┘
```

### Privacy Controls

#### Automatic Redaction
- PII detection (existing `utils/pii.py`)
- File path anonymization (`/home/user/projects/...` → `<project>`)
- User-specific identifiers removed
- Organization names anonymized (opt-in to share)

#### Manual Review
- User can review pattern before sharing
- Edit content before upload
- Flag specific fields as sensitive

#### Selective Sharing
```yaml
# In config.yaml
central:
  consent:
    mode: "ask_each_time"  # or "always_allow", "always_deny", "domain_specific"
    share_domains:
      - "odoo.orm"
      - "odoo.performance"
    block_domains:
      - "odoo.security"    # Never share security patterns
    auto_approve_high_confidence: true
    min_confidence_auto: 0.85
    anonymize_paths: true
    anonymize_org: true
```

## Sync Strategy

### Upload Strategy

#### Immediate Upload (Online)
```
1. Pattern distilled
2. User consent obtained
3. Add to sync_queue with status='pending'
4. Background worker picks up (within 1 second)
5. Authenticate with remote service
6. Upload pattern
7. Update sync_queue status='success' and patterns.remote_id
8. Log event
```

#### Queued Upload (Offline/Rate Limited)
```
1. Pattern distilled
2. User consent obtained
3. Add to sync_queue with status='pending'
4. Background worker attempts upload
5. If network error:
   - Update status='failed', retry_count++, last_retry_at
   - Schedule retry with exponential backoff (2^retry_count seconds)
   - Max retries: 5
6. If rate limited:
   - Update status='pending'
   - Schedule retry after rate limit reset
7. If permanent error:
   - Update status='failed', error_message
   - Notify user (optional)
```

#### Retry Schedule
```
Attempt 1: Immediate
Attempt 2: +2 seconds
Attempt 3: +4 seconds
Attempt 4: +8 seconds
Attempt 5: +16 seconds
Attempt 6: +32 seconds (final)
```

### Download Strategy

#### Initial Sync
- Download top 100 most relevant patterns for user's domains
- Cache locally in `community_patterns` table
- Update embeddings for hybrid retrieval

#### Periodic Sync
- Every 6 hours: Check for pattern updates
- Download new patterns matching user's domains
- Update cached patterns if remote version changed

#### On-Demand Sync
- During retrieval, fetch from remote if local cache miss
- Cache result for offline use

### Conflict Resolution

#### Local vs. Remote Pattern Conflict
```
If pattern exists both locally and remotely:
1. Compare by pattern_data hash
2. If identical:
   - Link local pattern to remote_id
   - Mark as uploaded
3. If different:
   - Keep both
   - Local pattern remains local-only
   - Remote pattern cached separately
   - User can merge manually
```

## Configuration

### Extended `config.yaml`

```yaml
reasoningbank:
  # ... existing config ...

  central:
    enabled: true                         # Enable centralized sync
    api_url: "https://reasoningbank.example.com/api/v1"
    api_key: "${REASONINGBANK_API_KEY}"  # From environment
    user_id: "${USER}"                    # Anonymous by default
    org_id: null                          # Optional organization

    consent:
      mode: "ask_each_time"               # ask_each_time, always_allow, always_deny, domain_specific
      share_domains:                      # Only for domain_specific mode
        - "odoo.orm"
        - "odoo.performance"
        - "odoo.views"
      block_domains:
        - "odoo.security"                 # Never auto-share security patterns
      auto_approve_high_confidence: true
      min_confidence_auto: 0.90
      show_preview: true                  # Show pattern before sharing
      anonymize_paths: true
      anonymize_org: true
      remember_choice: true               # Allow "Remember this choice"

    sync:
      upload_enabled: true
      download_enabled: true
      mode: "hybrid"                      # hybrid, upload_only, download_only
      batch_size: 10                      # Patterns per batch upload
      retry_max: 5
      retry_backoff_base: 2               # Seconds
      sync_interval: 21600                # 6 hours in seconds
      offline_queue_max: 1000             # Max queued patterns

    retrieval:
      include_community: true
      community_weight: 0.7               # vs. 1.0 for local patterns
      min_community_confidence: 0.65
      min_community_upvotes: 3
      cache_community_patterns: true
      cache_ttl: 86400                    # 24 hours

    privacy:
      redact_file_paths: true
      redact_usernames: true
      redact_ips: true
      redact_custom_patterns:             # Custom regex patterns to redact
        - '\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'  # Emails
      hash_task_ids: true                 # Hash task IDs before upload

    feedback:
      auto_report_failures: false         # Report if pattern didn't help
      auto_upvote_successes: false        # Upvote if pattern helped
```

## Implementation Files

### New Files to Create

1. **`scripts/sync_manager.py`** (~400 lines)
   - `SyncManager` class
   - `upload_pattern()`, `download_patterns()`, `sync_periodic()`
   - Upload queue management
   - Retry logic with exponential backoff
   - Batch uploads

2. **`scripts/remote_client.py`** (~300 lines)
   - `RemoteServiceClient` class
   - HTTP client with auth
   - `upload_pattern()`, `search_patterns()`, `submit_feedback()`
   - Rate limiting
   - Error handling

3. **`scripts/consent_manager.py`** (~250 lines)
   - `ConsentManager` class
   - `request_consent()` - prompt user
   - `check_consent()` - check preferences
   - `record_consent()` - save decision
   - Privacy controls

4. **`scripts/hybrid_retrieve.py`** (~350 lines)
   - `retrieve_hybrid()` - blend local + community
   - `fetch_community_patterns()` - query remote
   - `cache_community_pattern()` - save locally
   - Scoring and ranking

5. **`scripts/init_central.py`** (~150 lines)
   - Database migration script
   - Add new tables (sync_queue, user_consent, community_patterns)
   - Update patterns table schema
   - Initialize config

6. **`scripts/central_status.py`** (~100 lines)
   - Status reporting for central sync
   - Show upload queue stats
   - Show community pattern cache
   - Show sync health

### Modified Files

1. **`scripts/post_hook.py`**
   - Add consent check after distillation
   - Queue pattern for upload if approved
   - Trigger sync manager

2. **`scripts/pre_hook.py`**
   - Use hybrid retrieval instead of local-only
   - Blend local and community patterns
   - Tag pattern provenance

3. **`scripts/database.py`**
   - Add methods for new tables
   - `add_to_sync_queue()`, `get_pending_uploads()`
   - `record_consent()`, `get_consent()`
   - `cache_community_pattern()`, `get_community_patterns()`

4. **`config.yaml`**
   - Add `central` section (see above)

5. **`SKILL.md`**
   - Update with central sync information
   - Document consent system
   - Document privacy controls

## CLI Commands

### New Commands

```bash
# Initialize central sync
rb-init-central
    --api-url https://reasoningbank.example.com/api/v1
    --api-key <key>
    --consent-mode ask_each_time

# Sync status
rb-sync-status
    # Shows:
    # - Upload queue (pending, uploading, failed)
    # - Last sync time
    # - Community pattern cache size
    # - Sync health

# Manual sync
rb-sync
    --upload          # Upload pending patterns
    --download        # Download community patterns
    --full            # Bidirectional sync

# Consent management
rb-consent
    --mode always_allow | always_deny | ask_each_time | domain_specific
    --allow-domain odoo.orm
    --block-domain odoo.security

# Review pending uploads
rb-pending-uploads
    # Shows patterns awaiting user consent

# Approve/deny pattern
rb-approve <pattern_id>
rb-deny <pattern_id> --local-only

# Community pattern search
rb-search "N+1 query" --community-only -k 10

# Submit feedback
rb-feedback <remote_id> --upvote
rb-feedback <remote_id> --downvote
rb-feedback <remote_id> --report "Incorrect advice"
```

## Security Considerations

### Authentication
- API key stored in environment variable (not in config)
- Short-lived access tokens (1 hour expiry)
- Refresh token rotation

### Data Protection
- TLS 1.3 for all API communication
- Pattern data encrypted at rest on remote service
- Optional E2E encryption for sensitive patterns

### Privacy
- Anonymous user IDs by default
- Organization opt-in for attribution
- PII redaction before upload
- Right to delete patterns (GDPR compliance)

### Rate Limiting
- 100 uploads per hour per user
- 1000 downloads per hour per user
- Burst allowance: 20 uploads in 1 minute

## Rollout Plan

### Phase 1: Local Infrastructure (Week 1)
- [ ] Create sync_queue, user_consent, community_patterns tables
- [ ] Implement ConsentManager
- [ ] Update post_hook to request consent
- [ ] Implement local queuing (no remote yet)

### Phase 2: Remote Client (Week 2)
- [ ] Implement RemoteServiceClient
- [ ] Implement SyncManager with retry logic
- [ ] Add background upload worker
- [ ] Test with mock remote service

### Phase 3: Hybrid Retrieval (Week 3)
- [ ] Implement hybrid retrieval
- [ ] Download and cache community patterns
- [ ] Blend local + community in pre_hook
- [ ] Add provenance tagging

### Phase 4: Polish & Testing (Week 4)
- [ ] CLI commands for sync management
- [ ] Comprehensive testing
- [ ] Documentation
- [ ] Privacy controls refinement

## Success Metrics

### Technical Metrics
- Upload success rate > 99%
- Average upload latency < 500ms
- Queue processing time < 2s for p95
- Zero data loss in offline mode

### User Metrics
- % of users who enable central sync
- Consent approval rate
- Average patterns contributed per user
- Community pattern usage rate

### Quality Metrics
- Community pattern confidence > 0.75
- Upvote rate > 80%
- Duplicate rate < 10%
- User-reported quality issues < 5%

## Open Questions

1. **Remote Service Implementation**: Should we build the central service, or assume it exists?
2. **Consent UI**: CLI prompt vs. web dashboard?
3. **Pattern Ownership**: Can users edit/delete their uploaded patterns?
4. **Versioning**: How to handle pattern updates/improvements?
5. **Moderation**: Who reviews/approves patterns before making them public?
6. **Economics**: Free tier limits? Premium features?

---

**Document Version**: 1.0
**Last Updated**: 2025-11-24
**Author**: Claude Code Centralized RB Team
