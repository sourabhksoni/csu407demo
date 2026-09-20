# Intelligent Agriculture Information System: Chhattisgarh

**Course:** CS F/U 407, Artificial Intelligence, Class Project (30%)
**Team:** Team 10
**State:** Chhattisgarh
**Repository:** https://github.com/sourabhsoni0104/cs-u407

## Team and roles

| Name | BITS ID | Role |
|---|---|---|
| Pushti Amish Shah | 2024A7PS0514P | Source and Data Engineering Lead |
| Sourabh Kumar Soni | 2025A7PS0642P | Model Lead |
| Priyanshu Khandal | 2025PHXP0406P | Evaluation Lead |

## Project overview

This project builds an end to end agriculture information system for Chhattisgarh.

Chhattisgarh is a Decentralized Procurement (DCP) state. The state government buys paddy
directly from farmers at a declared support price through cooperative society run purchase
centres, while an open mandi market operates alongside it under the state Mandi Board. The
same district therefore carries two price signals at the same time, an administered one and a
market one, with storage capacity and weather advisories sitting between them.

The system consolidates procurement, price, storage and advisory information from official
sources into a single queryable database in which every stored number can be traced back to
the document and page it came from.

## Current phase

Phase 1: Statement of purpose, problem framework, source discovery and initial progress.

## Phase 1 status

- State selected and registered as Team 10
- Repository created; Instructor in Charge and TA to be added as collaborators
- Roles declared (see table above)
- Source discovery completed: 21 candidate sources reviewed, 14 verified live, 5 flagged for
  verification, 2 retained as documented data gaps
- Knowledge base schema drafted and frozen for Phase 1
- Agent and tool architecture drafted
- Source inventory workbook prepared

## Repository structure

```
data/                                          Collected documents and datasets (Phase 2)
data/manifest.md                               Provenance manifest for every collected file
docs/charter.md                                Team charter, roles and ways of working
docs/phase1/statement_of_purpose.md            Statement of purpose and problem framework
docs/phase1/agent_tool_plan.md                 Proposed agent and tool architecture
logs/progress_log.md                           Dated progress log
schema/knowledge_base_schema.md                Knowledge base schema and reasoning
src/                                           Pipeline code (Phase 2)
reports/                                       Interim and final reports
Team10_Chhattisgarh_Source_Inventory_Phase1.xlsx   Phase 1 submission workbook
```

## Note on source verification

Every candidate source was opened and checked against live results before being included.
Sources are marked VERIFIED where the portal was confirmed to exist and serve the stated
content, NEEDS VERIFICATION where the organisation is real but the exact data page has not yet
been confirmed, and GAP where no usable official source could be located. Gaps are kept in the
inventory rather than deleted, because the Phase 1 acceptance criteria ask for the limitations
of current sources, not only a list of working links.

## Scope discipline

Four fact areas (procurement, prices, storage, advisories) over two dimension tables and one
provenance table. Tendu leaf and other minor forest produce are handled inside the procurement
fact table rather than as a separate subsystem, because the Federation buys them at a declared
rate per standard unit in the same shape as paddy. Record level and beneficiary level farmer
data is out of scope throughout.
