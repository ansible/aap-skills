# Red Hat Reference Sources & Consultation Protocol

## Source Consultation Protocol

Before applying assessment rules in Step 3:

1. **First: query the Product Life Cycle Data API** — the single most
   important external call:
   ```
   GET https://access.redhat.com/product-life-cycles/api/v1/products?name=Automation+Execution+Environment
   ```
   Public API (no auth, no VPN), returns structured JSON. If successful,
   AAP version lifecycle classification is deterministic.

2. **Then: fetch remaining official sources** for support matrices,
   deprecated features, and compatibility data. These take precedence
   over baked-in rules.

3. **If inaccessible:** Fall back to baked-in rules and add to report header:
   ```
   ⚠ Offline Assessment — official Red Hat documentation was not accessible
   during this assessment. Rules used are from SKILL.md (last updated
   {skill_version_date}). For definitive support status, consult the
   Reference Sources listed at the end of this report.
   ```

**Priority order:**
1. Structured API responses (Product Life Cycle Data API) — deterministic
2. Values from live Red Hat documentation — authoritative, requires parsing
3. Assessment rules baked into SKILL.md — fallback, always cite source
4. Conservative default: if no rule matches → INFO/Unknown

## Official Red Hat Sources

| Topic | Source | URL |
|-------|--------|-----|
| **AAP Lifecycle (API)** | **Product Life Cycle Data API** | `access.redhat.com/product-life-cycles/api/v1/products?name=Automation+Execution+Environment` |
| AAP Lifecycle (human) | Red Hat Lifecycle Policy | access.redhat.com/support/policy/updates/ansible-automation-platform |
| EE Lifecycle Policy | Red Hat Lifecycle Policy | access.redhat.com/support/policy/updates/ansible-automation-platform-execution-environments |
| Supported Topologies | AAP Planning Guide | access.redhat.com/documentation/.../ref-installation-deployment-models |
| Topology Support | Article 7117676 | access.redhat.com/articles/7117676 |
| Aligning to Topologies | Article 7095801 | access.redhat.com/articles/7095801 |
| System Requirements | AAP Planning Guide | access.redhat.com/documentation/.../ref-system-requirements |
| Authentication Backends | AAP Central Auth Guide | access.redhat.com/documentation/.../con-gw-pluggable-authentication |
| External Credentials | AAP Admin Guide | access.redhat.com/documentation/.../assembly-controller-secret-management |
| Certified Collections | Automation Hub Guide | access.redhat.com/documentation/.../assembly-managing-cert-valid-content |
| Deprecated Features (2.6) | AAP 2.6 Release Notes | access.redhat.com/documentation/.../aap-26-deprecated-features |
| EE Base Images | AAP EE Guide | access.redhat.com/documentation/.../con-about-ee |

## Product Life Cycle API Response Structure

```json
{
  "data": [{
    "name": "Automation Execution Environment",
    "versions": [{
      "name": "ansible-automation-platform-25",
      "type": "Maintenance Support",
      "phases": [
        { "name": "General availability", "date_start": "...", "date_end": "..." },
        { "name": "Full support", "date_start": "...", "date_end": "..." },
        { "name": "Maintenance support 1", "date_start": "...", "date_end": "..." },
        { "name": "Maintenance support 2", "date_start": "...", "date_end": "..." }
      ]
    }]
  }]
}
```

**Version mapping:** AAP 2.5 → `ansible-automation-platform-25`
