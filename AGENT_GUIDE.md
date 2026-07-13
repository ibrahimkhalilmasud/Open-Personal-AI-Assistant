# AGENT GUIDE

## Purpose
Describe agent capabilities and task execution flow.

## Audience
Developers and operators.

## Prerequisites
Task queue basics.

## Step-by-step
Current discovered agent:
- `planning-agent` (`app/agents/planner.py`)
  - capabilities: planning, sequential_execution, validation, summarization
  - supports tasks: research, travel, document_analysis, project_summary, insurance_review

Agent flow:
1. `TaskPlanner` creates tasks from agent plan.
2. `TaskQueue` stores tasks in SQLite.
3. `TaskExecutionEngine` executes approved tasks.
4. `AgentHistoryStore` writes execution history.

## Examples
```bash
python main.py --agent-list
python main.py --plan "review insurance"
python main.py --execute
```

## Troubleshooting
If planning fails, ensure at least one planning-capable agent is discoverable.

## Related documents
- [USER_GUIDE.md](USER_GUIDE.md)
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
