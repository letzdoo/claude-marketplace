# GitHub Verification Guide for Odoo Development

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  GITHUB VERIFICATION PATTERNS                                                ║
║  Use this guide to verify Odoo patterns against official source code.        ║
║  ALWAYS verify patterns when in doubt about version-specific syntax.         ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Official Odoo Repository

### Repository URLs

| Version | Branch | Base URL |
|---------|--------|----------|
| 14.0 | `14.0` | `https://github.com/odoo/odoo/tree/14.0` |
| 15.0 | `15.0` | `https://github.com/odoo/odoo/tree/15.0` |
| 16.0 | `16.0` | `https://github.com/odoo/odoo/tree/16.0` |
| 17.0 | `17.0` | `https://github.com/odoo/odoo/tree/17.0` |
| 18.0 | `18.0` | `https://github.com/odoo/odoo/tree/18.0` |
| 19.0 | `master` | `https://github.com/odoo/odoo/tree/master` |

### Enterprise Repository
Enterprise modules: `https://github.com/odoo/enterprise/tree/{version}`

## Key Reference Files by Topic

### Model Patterns

| Topic | Path | Purpose |
|-------|------|---------|
| Base model | `odoo/models.py` | Core ORM implementation |
| Fields | `odoo/fields.py` | Field type definitions |
| API decorators | `odoo/api.py` | Decorator implementations |
| Mail thread | `addons/mail/models/mail_thread.py` | Chatter mixin |
| Sale order | `addons/sale/models/sale_order.py` | Complex model example |
| Product | `addons/product/models/product_template.py` | Multi-company example |

### View Patterns

| Topic | Path | Purpose |
|-------|------|---------|
| Base views | `odoo/addons/base/views/` | Core view patterns |
| Form widgets | `addons/web/static/src/views/fields/` | Field widgets |
| View registry | `addons/web/static/src/views/view.js` | View registration |
| Sale views | `addons/sale/views/sale_order_views.xml` | Complex view example |

### OWL Components

| Topic | Path | Purpose |
|-------|------|---------|
| Core OWL | `addons/web/static/src/core/` | Core utilities |
| Hooks | `addons/web/static/src/core/utils/hooks.js` | Service hooks |
| Registry | `addons/web/static/src/core/registry.js` | Component registry |
| Dialog | `addons/web/static/src/core/dialog/dialog.js` | Dialog component |
| Notifications | `addons/web/static/src/core/notifications/` | Notification service |
| Action service | `addons/web/static/src/webclient/actions/` | Action handling |

### Security

| Topic | Path | Purpose |
|-------|------|---------|
| Base security | `odoo/addons/base/security/` | Core security files |
| Sale security | `addons/sale/security/` | Module security example |
| Record rules | `odoo/addons/base/security/base_security.xml` | Rule examples |

## Verification Workflow

### Step 1: Identify Version
```
Target version → GitHub branch
- v18.0 → branch "18.0"
- v17.0 → branch "17.0"
- etc.
```

### Step 2: Locate Reference Module
Find a similar official module for your use case:

| Use Case | Reference Module | Path |
|----------|------------------|------|
| Sales workflow | sale | `addons/sale/` |
| Purchase workflow | purchase | `addons/purchase/` |
| Inventory | stock | `addons/stock/` |
| Accounting | account | `addons/account/` |
| HR | hr | `addons/hr/` |
| Project | project | `addons/project/` |
| CRM | crm | `addons/crm/` |
| Website | website | `addons/website/` |

### Step 3: Verify Pattern
Compare your code against official implementation:

```
Your pattern → Official pattern in same version
```

## Verification Examples

### Example 1: Verify Model Structure (v18)

**URL**: `https://github.com/odoo/odoo/blob/18.0/addons/sale/models/sale_order.py`

Check for:
- Model attributes (`_name`, `_inherit`, `_order`)
- Field definitions
- `@api.model_create_multi` usage
- `_check_company_auto` attribute

### Example 2: Verify View Syntax (v17+)

**URL**: `https://github.com/odoo/odoo/blob/18.0/addons/sale/views/sale_order_views.xml`

Check for:
- `invisible` expression syntax
- `readonly` expression syntax
- Button visibility patterns
- No `attrs` usage

### Example 3: Verify OWL Component (v18)

**URL**: `https://github.com/odoo/odoo/blob/18.0/addons/web/static/src/core/dialog/dialog.js`

Check for:
- Import patterns
- Component structure
- Service usage
- Registry registration

## Common Verification Checks

### For Python Models

```python
# Check these patterns in official code:

# 1. Decorator usage
@api.model_create_multi  # v17+: Should be present on create()

# 2. Company handling
_check_company_auto = True  # v18+: Should be present

# 3. Field attributes
check_company=True  # v18+: Should be on cross-company fields

# 4. Type hints
def method(self, arg: int) -> bool:  # v18+: Encouraged, v19+: Required
```

### For XML Views

```xml
<!-- Check these patterns in official views: -->

<!-- 1. Visibility (v17+) -->
<field name="x" invisible="state != 'draft'"/>

<!-- 2. NOT this (v16 and earlier) -->
<field name="x" attrs="{'invisible': [('state', '!=', 'draft')]}"/>

<!-- 3. Button patterns -->
<button name="action" invisible="state != 'draft'"/>
```

### For JavaScript/OWL

```javascript
// Check these patterns in official components:

// 1. Module declaration
/** @odoo-module **/

// 2. Imports
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

// 3. Service usage
this.orm = useService("orm");

// 4. Registry
registry.category("actions").add("key", Component);
```

## Quick Verification URLs

### v18.0 Quick Links

| Component | Direct URL |
|-----------|------------|
| sale_order.py | `github.com/odoo/odoo/blob/18.0/addons/sale/models/sale_order.py` |
| sale_order_views.xml | `github.com/odoo/odoo/blob/18.0/addons/sale/views/sale_order_views.xml` |
| mail_thread.py | `github.com/odoo/odoo/blob/18.0/addons/mail/models/mail_thread.py` |
| hooks.js | `github.com/odoo/odoo/blob/18.0/addons/web/static/src/core/utils/hooks.js` |
| dialog.js | `github.com/odoo/odoo/blob/18.0/addons/web/static/src/core/dialog/dialog.js` |

### v17.0 Quick Links

| Component | Direct URL |
|-----------|------------|
| sale_order.py | `github.com/odoo/odoo/blob/17.0/addons/sale/models/sale_order.py` |
| sale_order_views.xml | `github.com/odoo/odoo/blob/17.0/addons/sale/views/sale_order_views.xml` |

## AI Agent Instructions

When generating Odoo code:

1. **ALWAYS** verify critical patterns against GitHub when unsure
2. **USE** version-specific branch (e.g., `18.0` not `master`)
3. **COMPARE** your generated code with official examples
4. **CHECK** these key indicators:
   - Decorator usage
   - View attribute syntax
   - OWL import patterns
   - Security rule syntax

5. **IF PATTERN UNCLEAR**: Fetch the relevant file from GitHub and verify

```
Verification workflow:
User request → Determine version → Generate code → Verify against GitHub → Deliver
```

## Using WebFetch for Verification

When you need to verify a pattern, use WebFetch:

```
URL: https://raw.githubusercontent.com/odoo/odoo/{version}/addons/{module}/models/{file}.py
Prompt: "Extract the pattern for [specific feature] from this Odoo model"
```

Example:
```
URL: https://raw.githubusercontent.com/odoo/odoo/18.0/addons/sale/models/sale_order.py
Prompt: "Show how the create method is decorated and structured"
```

---

**IMPORTANT**: GitHub verification is your source of truth. When documentation conflicts with actual code, trust the code.
