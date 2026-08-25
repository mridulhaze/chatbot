# AI Skills Architecture Documentation

## What is a Skill?
A **Skill** represents an autonomous domain module containing AI instructions, conversational workflows, trigger conditions, allowed MCP tools, and privacy guardrails.

Skills live under the `skills/` directory:
- `skills/nu_general/SKILL.md`
- `skills/token_service/SKILL.md`
- `skills/examination/SKILL.md`
- `skills/admission/SKILL.md`
- `skills/result/SKILL.md`
- `skills/document_search/SKILL.md`

## Why Skills and MCP are Separated
| Aspect | AI Skill (`skills/`) | MCP Server (`mcp_servers/`) |
|---|---|---|
| **Core Question** | *What should the AI do?* | *What tools/data can the AI access?* |
| **Contents** | Prompt rules, workflows, multi-turn steps | Python functions, SQL queries, REST tools |
| **Coupling** | Zero direct database/API code | Strict typed operations, validation |
| **Security** | Guides conversational policy | Enforces RBAC, input safety, audit logs |

## How to Create a New Skill
1. Create a new directory under `skills/your_skill_name/`.
2. Add a `SKILL.md` file with frontmatter:
```markdown
---
name: migration_service
version: 1.0.0
description: Handles college migration and transfer guidelines.
---

# Migration Skill

## Purpose
...
## Trigger Conditions
...
## Available MCP Tools
- get_services
- search_nu_knowledge
## Conversational Workflow
1. Detect migration category
2. Present rules and eligibility
...
```
3. The Skill is automatically discovered and registered by `SkillRegistry` upon restart.
