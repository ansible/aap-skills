# Red Hat Reference Sources & Consultation Protocol

## Source Consultation Protocol

Before applying any baseline or threshold in Step 3:

1. Attempt to fetch each official source URL below
2. **If accessible:** Extract current thresholds, lifecycle dates, support
   matrices, and version-specific guidance. These take precedence over
   baked-in values in SKILL.md or `advisory-baselines.md`.
3. **If inaccessible:** Fall back to baked-in rules and add to report header:
   ```
   ⚠ Offline Assessment — official Red Hat documentation was not accessible
   during this assessment. Baselines used are from SKILL.md (last updated
   {skill_version_date}). For the most current guidance, consult the
   Reference Sources listed at the end of this report.
   ```

**Priority order:**
1. Structured API responses (highest authority)
2. Values extracted from live documentation pages
3. Customer-provided organizational baselines (if supplied via `baseline_profile`)
4. Advisory baselines baked into SKILL.md (lowest authority — always label with *)

## Official Red Hat Sources

| Topic | Source | URL |
|-------|--------|-----|
| Health check API endpoints | KCS 7113839 | access.redhat.com/solutions/7113839 |
| Health check service commands | KCS 7116362 | access.redhat.com/solutions/7116362 |
| Prometheus monitoring of AAP | KCS 7125740 | access.redhat.com/solutions/7125740 |
| Prometheus metrics reference | AAP Admin Guide | access.redhat.com/documentation/.../ref-controller-metrics-monitoring |
| API latency KPIs | AAP Performance Tuning | access.redhat.com/documentation/.../con-key-perf-indicators-scaling-API-services |
| System requirements | AAP Planning Guide | access.redhat.com/documentation/.../ref-system-requirements |
| Capacity determination | AAP Admin Guide | access.redhat.com/documentation/.../con-controller-capacity-determination |
| Instance group capacity | AAP Admin Guide | access.redhat.com/documentation/.../ref-controller-instance-group-capacity |
| License compliance model | AAP Admin Guide | access.redhat.com/documentation/.../con-controller-keep-subscription-in-compliance |
| PostgreSQL tuning | AAP Admin Guide | access.redhat.com/documentation/.../ref-controller-database-settings |
| EE lifecycle policy | Red Hat Lifecycle | access.redhat.com/support/policy/updates/ansible-automation-platform-execution-environments |
| Workload sizing (Growth) | AAP Perf Tuning | access.redhat.com/documentation/.../ref-workloads-growth-topologies |
| Workload sizing (Enterprise) | AAP Perf Tuning | access.redhat.com/documentation/.../ref-workloads-enterprise-topologies |
| Job cleanup defaults | AAP Admin Guide | access.redhat.com/documentation/.../assembly-controller-management-jobs |
| Azure cert renewal | KCS 7019408 | access.redhat.com/solutions/7019408 |
