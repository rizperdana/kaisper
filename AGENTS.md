---
title: Kaisper Agent Directives
version: 0.1.0
status: active
last_updated: 2026-04-26
---

# Kaisper Agent Directives

## Project Context

**Project**: Kaisper — Universal AI‑Driven Scraper
**Location**: `/home/anon/Projects/experiment/kaisper`
**Documentation**: See `docs/PROJECT_SPEC.md` for requirements, `docs/ARCHITECTURE.md` for technical design

## Agent Behavior for Kaisper

### When Working on Kaisper

1. **Always read project documentation first**:
   - Start with `docs/PROJECT_SPEC.md` for requirements and constraints
   - Check `docs/TASKS.md` for current work items
   - Reference `docs/RULES.md` for coding patterns
   - Consult `docs/ARCHITECTURE.md` for technical decisions

2. **Follow modular documentation structure**:
   - Each document serves a specific purpose
   - Use YAML frontmatter for metadata
   - Keep files modular and focused
   - Update relevant docs when making changes

3. **Use subagent presets for research and planning**:
   - `subagent-researcher` - For researching universal scraping approaches
   - `subagent-architect` - For reviewing system design
   - `subagent-auditor` - For security/legal reviews
   - `subagent-analyst` - For cost/performance analysis
   - `subagent-strategist` - For integration planning
   - `subagent-tester` - For test design
   - `subagent-validator` - For reviewing outputs
   - `subagent-documenter` - For writing documentation

4. **Always include anti-hallucination rules**:
   ```
   YOU MUST FOLLOW THE ANTI-HALLUCINATION RULES DESCRIBED IN THE SUBAGENT-[TYPE] SKILL.
   ```

5. **Use validator preset for critical outputs**:
   - Review architecture designs before implementation
   - Validate research findings before accepting
   - Check cost analysis before proceeding

### Task Delegation for Kaisper

#### Research Tasks
- Use `subagent-researcher` for:
  - Researching universal data models (Schema.org, JSON-LD)
  - Researching LLM extraction patterns
  - Researching template systems
  - Researching content type detection
  - Comparing scraping frameworks

#### Architecture Tasks
- Use `subagent-architect` for:
  - Reviewing system design
  - Identifying architectural flaws
  - Suggesting improvements
  - Designing components

#### Security/Legal Tasks
- Use `subagent-auditor` for:
  - Security reviews
  - Legal compliance checks
  - Privacy impact assessments
  - Terms of service analysis

#### Analysis Tasks
- Use `subagent-analyst` for:
  - Cost modeling
  - Performance analysis
  - TCO calculations
  - Benchmarking

#### Strategy Tasks
- Use `subagent-strategist` for:
  - Integration planning
  - Migration paths
  - Rollout strategies
  - Feature prioritization

#### Testing Tasks
- Use `subagent-tester` for:
  - Test suite design
  - Edge case identification
  - Failure scenario planning
  - Test case generation

#### Documentation Tasks
- Use `subagent-documenter` for:
  - Writing README
  - Creating API docs
  - Writing usage guides
  - Documenting architecture

#### Validation Tasks
- Use `subagent-validator` for:
  - Reviewing other subagents' outputs
  - Checking for hallucinations
  - Verifying citations
  - Assessing completeness

### Coding Tasks

#### For Kaisper Development

**Simple Tasks** (single module, <500 lines):
- Use `opencode` as primary coder
- Use `kilocode` as fallback

**Complex Tasks** (3+ modules, full-stack, research):
- Use `clawteam` to spawn a team
- Spawn specialized workers for each component

**You Handle Only**:
- Git operations (commit, push, branch)
- Directory creation
- Reading files for context
- Spawning agents
- Updating documentation

**Never**:
- Write code directly
- Edit code directly
- Create scripts directly
- Run build/test commands directly

### Decision Tree for Kaisper

```
User asks to code something for Kaisper?
  → Is it complex (3+ modules, full-stack, research)?
    YES → clawteam spawn-team + spawn workers
    NO  → opencode (or kilocode if unavailable)

User asks to research something for Kaisper?
  → Use subagent-researcher with anti-hallucination rules
  → Validate output with subagent-validator

User asks to review Kaisper architecture?
  → Use subagent-architect with anti-hallucination rules
  → Validate output with subagent-validator

User asks to analyze costs for Kaisper?
  → Use subagent-analyst with anti-hallucination rules
  → Validate output with subagent-validator

User asks to plan Kaisper integration?
  → Use subagent-strategist with anti-hallucination rules
  → Validate output with subagent-validator

User asks to design tests for Kaisper?
  → Use subagent-tester with anti-hallucination rules
  → Validate output with subagent-validator

User asks to document Kaisper?
  → Use subagent-documenter with anti-hallucination rules
  → Validate output with subagent-validator
```

### Documentation Updates

When making changes to Kaisper:

1. **Update relevant documentation**:
   - Code changes → Update `docs/RULES.md` if patterns change
   - Architecture changes → Update `docs/ARCHITECTURE.md`
   - New features → Update `docs/PROJECT_SPEC.md`
   - Completed tasks → Update `docs/TASKS.md`

2. **Follow documentation structure**:
   - Keep files modular
   - Use YAML frontmatter
   - Update version numbers
   - Add change notes

3. **Maintain single source of truth**:
   - `docs/PROJECT_SPEC.md` is the main requirements document
   - `docs/ARCHITECTURE.md` is the main technical design document
   - `docs/TASKS.md` tracks progress
   - `docs/RULES.md` defines coding standards

### Anti-Hallucination Enforcement

**Critical Rule**: All subagent work for Kaisper MUST follow anti-hallucination rules:

1. **Source citations required** for all factual claims
2. **Confidence scoring** on all statements
3. **No speculation** - state "unable to verify" if info not found
4. **Known unknowns** must be listed
5. **Tool usage** - must use web_search, web_fetch, read_file for evidence

**Validation Required**:
- Use `subagent-validator` to review all critical outputs
- Check citations are accurate
- Verify no hallucinations
- Assess completeness

### Project-Specific Constraints

**Non-Negotiable** (from PROJECT_SPEC.md):
1. Universal content support - handle ANY type without engine modification
2. Deterministic extraction - no LLM calls during extraction
3. Template reusability - cache and reuse templates
4. CLI-first - primary interface is command-line
5. Modular architecture - extensible without core changes
6. Unified storage - single database for all content types
7. Anti-hallucination - strict rules for all subagent work

**Always Check**:
- Does this change support universal content types?
- Does this maintain deterministic extraction?
- Does this follow the modular architecture?
- Does this use the unified storage solution?
- Does this follow the coding rules?

### Communication Style

**When working on Kaisper**:
- Be concise and accurate
- Focus on technical details
- Cite sources for claims
- State confidence levels
- List unknowns and assumptions
- Follow the persona defined in `SOUL.md`

### Error Handling

**When something goes wrong**:
1. Check documentation first
2. Review relevant docs (PROJECT_SPEC, ARCHITECTURE, RULES)
3. Identify the constraint or requirement violated
4. Propose a solution that respects constraints
5. Update documentation if needed

### Success Criteria

**For Kaisper**:
- Coverage: ≥80% of tested sites yield working template
- Reliability: ≥95% extraction success rate on cached templates
- Cost: <$0.01 per template generation; <$0.001 per extraction
- Latency: <2s template generation; <500ms extraction
- Maintainability: <200 lines core engine code
- Universal Support: 5+ content types without engine modification

### Notes

- These directives are specific to the Kaisper project
- Always reference project documentation when in doubt
- Use subagent presets for all research and planning
- Validate all critical outputs
- Update documentation as the project evolves
