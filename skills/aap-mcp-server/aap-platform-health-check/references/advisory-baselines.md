# Advisory Baselines & Severity Model

This file contains the detailed threshold tables and severity model for the
Platform Health Check skill. These are applied in Step 3 (Analyze Against
Baselines and Flag Anomalies).

## Baseline Profiles

| Metric | Default | Small (<100 hosts) | Medium (100-1000) | Large (1000+) |
|--------|---------|--------------------|--------------------|---------------|
| Task queue depth * | < 10% of remaining capacity sustained | < 10% sustained | < 10% sustained | < 5% sustained |
| Failed jobs (24h) * | < 5% of total | < 5% | < 5% | < 3% |
| License compliance | Compliant per Red Hat model | Same | Same | Same |
| EE lifecycle status | Supported ansible-core version | Same | Same | Same |
| Project sync errors * | 0 | 0 | 0 | 0 |
| Instance group capacity * | > 25% available | > 25% | > 30% | > 40% |
| Certificate expiry * | > 30 days | > 30 days | > 60 days | > 90 days |
| Disk usage * | < 80% | < 80% | < 75% | < 70% |
| Database replication lag * | < 100ms | < 200ms | < 100ms | < 50ms |

> **Advisory Baselines:** Thresholds marked with * are advisory baselines derived
> from operational best practices. Red Hat does not publish health thresholds for
> these metrics. Adjust based on organizational benchmarks.

> **Task queue note:** Thresholds are capacity-relative, not absolute. A queue
> depth of 200 on a platform with 2000 capacity slots is healthy; same depth
> with 250 total capacity is a warning.

## License Assessment (Official Model)

The primary license assessment uses Red Hat's official compliance model:
- **Compliant:** `managed_hosts <= licensed_hosts` AND `time_remaining > 0`
- **Non-compliant:** either condition fails
- Trial licenses block automation when non-compliant. Enterprise licenses
  continue with warnings.
- Ref: "Keeping your subscription in compliance" (AAP Admin Guide)

*Advisory addition:* If compliant but `managed_hosts > 80%` of `licensed_hosts`,
flag as INFO ("approaching license limit — plan capacity"). The 80% threshold
is advisory.

## EE Assessment (Official Model)

Uses Red Hat's EE Lifecycle Policy:
- Check EE images against the EE Lifecycle Policy. EEs using ansible-core in
  "Full Support" or "Maintenance" phase are supported.
- EEs using EOL ansible-core versions are unsupported regardless of managed flag.
- Ref: access.redhat.com/support/policy/updates/ansible-automation-platform-execution-environments

*Advisory addition:* If unmanaged EEs with known supported images haven't
updated in >90 days, flag INFO (may be missing security patches).

## Severity Classification (Advisory)

> Red Hat does not publish a severity model for platform health metrics.

| Severity | Criteria | Action Required |
|----------|----------|-----------------|
| **CRITICAL** | Service down, database unreachable, license expired, all capacity consumed, certs expired, disk > 95% | Immediate attention required |
| **WARNING** | Metrics approaching thresholds, license expiring within 30 days, elevated failure rate, certs expiring within 30 days | Schedule remediation |
| **INFO** | Metrics within normal range, version updates available, optimization suggestions | No action required |

## Contextual Anomaly Correlation Guidelines

The LLM must correlate multiple health signals into a unified diagnosis:

- A task queue depth of 200 is normal during a scheduled maintenance window
  but anomalous at 2 PM on a Tuesday
- A 10% job failure rate concentrated in a single project suggests a
  project-specific issue, not a platform problem
- License utilization at 85% with renewal in 60 days warrants a different
  recommendation than 85% with 300 days remaining
- High disk usage + many failed jobs + old EE images together suggest a
  neglected platform — the report should say so
- Database replication lag increasing over time suggests growing load;
  a sudden spike suggests a network issue

The LLM prioritizes what needs attention first and explains root cause
vs. symptom.

## Official Disk/System Requirements (Reference)

Red Hat published minimums (from AAP Planning Guide):
- `/var/lib/awx`: 20 GB minimum
- Database: 100 GB minimum
- No percentage-based threshold is published by Red Hat

## Official Certificate Reference

Only published reference: Azure 14-day renewal (KCS 7019408). No general
certificate expiry threshold is published by Red Hat.
