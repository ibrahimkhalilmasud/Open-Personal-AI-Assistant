# WORKFLOW EXAMPLES

## Purpose
Provide practical workflow playbooks.

## Audience
End users and operations teams.

## Prerequisites
Vault contains relevant documents; scan/index completed.

## Step-by-step
### 1) Research workflow
- Objective: produce evidence-based summary.
- Commands: `python main.py --plan "research topic X"` then `python main.py --execute`
- Expected results: sequential tasks and completed summaries with citations.
- Common mistakes: running execute without planning first.

### 2) Travel workflow
- Objective: prepare trip checklist and insurance tasks.
- Commands: `python main.py --plan "prepare my trip to Bali"`; `python main.py --execute`
- Expected results: passport/insurance/budget steps.
- Common mistakes: missing travel documents in vault.

### 3) Medical document workflow
- Objective: quickly locate and summarize medical records.
- Commands: `python main.py --search "medical"`; `python main.py --ask "Summarize my medical documents"`
- Expected results: matched records and grounded answer.
- Common mistakes: skipping scan/index after adding new records.

### 4) Insurance workflow
- Objective: compare policy details and renewal information.
- Commands: `python main.py --search "insurance"`; `python main.py --ask "What are my renewal dates?"`; optional plan/execute.
- Expected results: extracted policy context and recommendations.
- Common mistakes: ambiguous query terms.

### 5) Office workflow
- Objective: find project/admin docs quickly.
- Commands: `python main.py --search "invoice" --folder office`; `python main.py --memory-search "client"`
- Expected results: focused office file retrieval.
- Common mistakes: not using folder/type filters.

### 6) Project workflow
- Objective: review project state and team relationships.
- Commands: `python main.py --project <project_name>`; `python main.py --timeline 2025`
- Expected results: project summary + related graph context.
- Common mistakes: expecting project output before enough source files exist.

## Examples
See built-in workflow names with `python main.py --workflow-list`.

## Troubleshooting
If no results, verify scan/index health first.

## Related documents
- [USER_GUIDE.md](USER_GUIDE.md)
- [AGENT_GUIDE.md](AGENT_GUIDE.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
