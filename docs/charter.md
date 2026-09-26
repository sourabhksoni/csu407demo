# Team Charter, Team 10, Chhattisgarh

**CS F/U 407: Artificial Intelligence, Class Project**

## Members and roles

The brief requires a team of 3 with declared roles. One person may hold two roles in a team
of 3.

| Name | BITS ID | Role | NDA and IP signed |
|---|---|---|---|
| Pushti Amish Shah | 2024A7PS0514P | Source Lead and Data Engineering Lead | Pending |
| Sourabh Kumar Soni | 2025A7PS0642P | Model Lead | Pending |
| Priyanshu Khandal | 2025PHXP0406P | Evaluation Lead | Pending |

## Role definitions

| Role | Owns |
|---|---|
| Source Lead | Source inventory, verification of flagged sources, licensing record, data/manifest.md |
| Data Engineering Lead | Repository, schema implementation, database build, ingestion code, reproducibility |
| Model Lead | Agent scaffolding (tools, prompts, memory, control loop), LoRA or QLoRA adapter training |
| Evaluation Lead | Held out evaluation set kept out of training, with and without adapter comparison, metrics reporting |

## Working scope

Four fact areas: procurement, prices, storage, advisories. Two dimension tables and a
provenance pair. See schema/knowledge_base_schema.md.

Minor forest produce is recorded inside the procurement fact table, not as a separate
subsystem. Record level and beneficiary level farmer data is excluded entirely.

## Ways of working

- All communication with the Instructor and TAs goes through Nalanda only, per the brief.
- The Instructor in Charge and TA are added as repository collaborators so review comments can
  be left directly in the codebase.
- All project code and documentation stays in this single repository from the beginning.
- Large datasets and model weights are stored in the designated location, with links recorded
  in the repository rather than the files themselves.
- Naming convention for all submitted artifacts: TEAM10_CHHATTISGARH_ARTIFACT_vN.
- Individual contribution is tracked through commit history, since the brief flags one student
  doing all technical work as a red flag checked at viva.

## Ethics and compliance commitments

- robots.txt and rate limits respected on every scrape. Official APIs and bulk downloads
  preferred wherever available.
- Licence or terms of every source recorded in the inventory and manifest.
- No personal data. No farmer names, no Aadhaar linked identifiers, no beneficiary level
  records. Aggregate figures only.
- Base model licence verified to permit fine tuning and adapter redistribution before training.
