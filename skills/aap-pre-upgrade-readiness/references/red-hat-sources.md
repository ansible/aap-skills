# Red Hat Reference Sources & Consultation Protocol

## Source Consultation Protocol

Before Step 3 (Assess Upgrade Readiness):

1. Attempt to fetch each official source URL below
2. **If accessible:** Extract current upgrade paths, prerequisites,
   deprecated features, auth migration requirements, and topology changes
3. **If inaccessible:** Fall back to baked-in rules in `upgrade-matrices.md`
   and flag report as "offline assessment":
   ```
   ⚠ Offline Assessment — official Red Hat documentation was not accessible
   during this assessment. Rules used are from SKILL.md (last updated
   {skill_version_date}). For the most current guidance, consult the
   Reference Sources listed at the end of this report.
   ```

**Priority order:**
1. Live official Red Hat documentation (highest authority)
2. Official documentation previously retrieved or cached
3. Advisory baselines baked into SKILL.md (lowest — always label with *)

## Official Red Hat Sources

| Topic | Source | URL |
|-------|--------|-----|
| Upgrade support matrix | Planning Your Upgrade | docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/planning_your_upgrade/upgrade-support-matrix |
| Upgrade prerequisites | Planning Your Upgrade | docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/planning_your_upgrade/aap-upgrade-planning |
| Infrastructure changes | Planning Your Upgrade | docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/planning_your_upgrade/upgrade-infrastructure-changes |
| Auth migration (2.4→2.6) | Planning Your Upgrade | docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/planning_your_upgrade/upgrade-authentication-movement-2.4-to-2.6 |
| IAM data movement | Planning Your Upgrade | docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/planning_your_upgrade/upgrade-data-movement |
| API changes | Planning Your Upgrade | docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/planning_your_upgrade/upgrade-api-changes |
| Deprecated features | Release Notes | docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/release_notes |
| RPM upgrade procedure | RPM Upgrade Guide | docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/rpm_upgrade |
| Container upgrade | Containerized Install | docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/containerized_installation |
| Operator upgrade | Deploying with Operator | docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/deploying_ansible_automation_platform_on_openshift_container_platform |
| EE lifecycle policy | Red Hat Lifecycle | access.redhat.com/support/policy/updates/ansible-automation-platform-execution-environments |
| AAP lifecycle policy | Red Hat Lifecycle | access.redhat.com/support/policy/updates/ansible-automation-platform |
| System requirements | Planning Your Install | docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/planning_your_installation |
| Upgrade FAQs | Planning Your Upgrade | docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/planning_your_upgrade/upgrade-faqs |
| Migration guide | Migrating to AAP | docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/migrating_to_ansible_automation_platform |

## Advisory Baselines (Fallback Only)

The following items in `upgrade-matrices.md` are advisory (NOT published by Red Hat):
- Custom content risk thresholds (0/1-5/6-20/20+ items)
- Operational readiness checks (running jobs, active schedules)
- Contextual risk correlations (cross-dimension risk scoring)

When used, always label as advisory and recommend consulting official sources.
