# Red Hat Reference Sources & Consultation Protocol

## Source Consultation Protocol

Before applying validation rules in Step 3:

1. Detect the installed AAP version from `config_retrieve`
2. Attempt to fetch the **Tested deployment models** guide for that version
   (this is THE primary source — defines what Red Hat tests and supports)
3. **If accessible:** Extract tested topologies, component counts,
   infrastructure requirements, and HA components. Use as validation
   baseline instead of baked-in rules.
4. Also fetch node type definitions, mesh configuration, and alignment articles.
5. **If inaccessible:** Fall back to baked-in rules and add to report header:
   ```
   ⚠ Offline Validation — official Red Hat documentation was not accessible
   during this validation. Topology definitions used are from SKILL.md (last
   updated 2026-04-09). For the most current tested deployment models, consult
   the Reference Sources listed at the end of this report.
   ```

## Official Red Hat Sources

| Topic | Source | URL |
|-------|--------|-----|
| **Tested Models (2.5)** | **THE primary source** | docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/tested_deployment_models/ |
| **Tested Models (2.6)** | **THE primary source** | docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html-single/tested_deployment_models/ |
| Container Growth | Tested Deployment Models | .../tested_deployment_models/container-topologies#cont-a-env-a |
| Container Enterprise | Tested Deployment Models | .../tested_deployment_models/container-topologies#cont-b-env-a |
| Operator Growth | Tested Deployment Models | .../tested_deployment_models/ocp-topologies#ocp-a-env-a |
| Operator Enterprise | Tested Deployment Models | .../tested_deployment_models/ocp-topologies#ocp-b-env-a |
| RPM Growth | Tested Deployment Models | .../tested_deployment_models/rpm-topologies#rpm-a-env-a |
| RPM Enterprise | Tested Deployment Models | .../tested_deployment_models/rpm-topologies#rpm-b-env-a |
| Topology Support | Article 7117676 | access.redhat.com/articles/7117676 |
| Aligning to Topologies | Article 7095801 | access.redhat.com/articles/7095801 |
| Node Types | AAP Admin Guide | access.redhat.com/documentation/.../con-automation-mesh-node-types |
| Minimum Resilient Config | AAP Admin Guide | access.redhat.com/documentation/.../ref-mesh-minimum-resilient-config |
| Scaling Control Nodes | AAP Admin Guide | access.redhat.com/documentation/.../ref-scaling-control-nodes |
| Automation Mesh Overview | AAP Admin Guide | access.redhat.com/documentation/.../con-about-automation-mesh |
