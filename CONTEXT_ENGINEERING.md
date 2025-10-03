# Context Engineering for AI Agents - DroneWatch Reference

**Source**: [Anthropic - Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Applied**: October 3, 2025
**Status**: Core methodology for DroneWatch development

---

## Core Principle

> **"Treat context as a finite resource with diminishing marginal returns"**

Goal: Find the **smallest possible set of high-signal tokens** that maximize the likelihood of desired outcomes.

---

## 1. Lightweight Identifiers (Don't Load Everything)

### The Problem
❌ Loading all 873 files into context
❌ Reading entire codebase upfront
❌ Context rot after ~50 files
❌ Diminishing returns on additional content

### The Solution
✅ **Create navigation maps** (directory structure)
✅ **Use file paths as pointers** (reference, don't load)
✅ **Load content just-in-time** (only when needed)
✅ **Maintain references** (file:line format)

### DroneWatch Example
```bash
# DON'T DO THIS:
find . -name "*.py" -exec cat {} \;  # ❌ Load everything

# DO THIS INSTEAD:
tree -L 2 -I 'node_modules'          # ✅ Map structure
# Then load specific files only when investigating
```

### Implementation
```markdown
## Architecture Map (Lightweight Identifiers)

dronewatch-2/
├── frontend/           # Next.js 14 app
│   ├── app/           # Route handlers
│   ├── components/    # React components
│   └── api/           # Python serverless
├── ingestion/         # Scraper system
└── migrations/        # DB migrations

**Reference**: Load files from these paths only when needed
**Format**: `file:line` for precise references
```

---

## 2. Progressive Disclosure (Incremental Discovery)

### The Problem
❌ Trying to understand everything at once
❌ Broad, unfocused exploration
❌ Analysis paralysis
❌ Missing the forest for the trees

### The Solution
✅ **Start with high-level questions**
✅ **Drill down based on findings**
✅ **Use targeted searches**
✅ **Follow evidence trails**

### DroneWatch Example

**Level 1: High-Level Questions**
```markdown
Q1: What's the data quality issue?
Q2: Why are sources empty?
Q3: What migrations are pending?
```

**Level 2: Targeted Investigation** (based on Q1)
```markdown
Q1 → Evidence: Non-drone articles in API
Q1 → Hypothesis: Content filtering broken
Q1 → Investigation: Read ONLY filtering code
   - ingestion/utils.py (validation)
   - ingestion/scrapers/news_scraper.py (matching)
   - ingestion/config.py (keywords)
```

**Level 3: Deep Dive** (if needed)
```markdown
Root cause found? → Document and move on
Still unclear? → Read related files
```

### Implementation Template
```markdown
## Investigation Questions (Progressive Disclosure)

### Q1: [High-level question]
**Evidence**: [What you observed]
**Hypothesis**: [What you think is wrong]
**Files to investigate**: [Specific paths]
**Status**: 🔍 NEEDS DEEP DIVE

### Findings:
- [Specific finding with file:line reference]
- [Root cause identified]
- [Recommended fix]
```

---

## 3. Structured Note-Taking (Persistent Memory)

### The Problem
❌ Losing context across sessions
❌ Forgetting previous findings
❌ Repeating investigations
❌ No decision trail

### The Solution
✅ **Create living documents** (markdown files)
✅ **Maintain outside context window** (persistent storage)
✅ **Structure findings clearly** (sections, bullets)
✅ **Document decisions** (why you did what)

### DroneWatch Example Files

**INVESTIGATION_FINDINGS.md**
- Architecture map (reference)
- Investigation questions (progressive)
- Findings (structured)
- Decision log (reasoning)

**SESSION_SUMMARY_*.md**
- What was done
- What was found
- What's pending
- Next steps

**CONTEXT_ENGINEERING.md** (this file)
- Methodology reference
- Principles and patterns
- Examples and anti-patterns

### Implementation Template
```markdown
# [Project] Investigation Findings

## Architecture Map (Lightweight Identifiers)
[Directory structure as reference]

## Investigation Questions (Progressive Disclosure)
[Q1, Q2, Q3... with status]

## Findings (Structured Notes)
### 🔴 CRITICAL
1. **Issue** - Evidence, location, fix, effort

### ⚠️ HIGH
2. **Issue** - Evidence, location, fix, effort

## Decision Log
**Why did we X?** - Reasoning with evidence
```

---

## 4. Sub-Agent Architecture (Specialized Tasks)

### The Problem
❌ Single agent trying to do everything
❌ Context mixing across concerns
❌ Loss of focus during investigation
❌ Inefficient use of context window

### The Solution
✅ **Delegate focused tasks** to specialized agents
✅ **One concern per agent** (scraper analysis, API investigation)
✅ **Clear deliverables** (specific questions to answer)
✅ **Parallel investigation** (when possible)

### DroneWatch Example

**Main Agent** (orchestrator):
- Creates architecture map
- Defines investigation questions
- Launches sub-agents
- Aggregates findings

**Sub-Agent 1** (scraper analysis):
```
Task: Find root cause of content filtering issue
Scope: ONLY read 3 files (utils.py, news_scraper.py, config.py)
Deliverable: Root cause + specific fix with file:line references
Result: Found substring matching bug in 5 minutes ✅
```

**Sub-Agent 2** (sources investigation):
```
Task: Why are sources arrays empty?
Scope: ONLY read API and database code
Deliverable: Schema issue or query bug
Result: [Pending]
```

### Implementation with Task Tool
```python
# Launch focused sub-agent
Task(
    subagent_type="general-purpose",
    description="Analyze scraper content filtering",
    prompt="""
    **Focused task**: Find root cause of filtering issue

    **Context** (lightweight):
    - Issue: Non-drone articles in production
    - Evidence: API shows couple's anniversary as drone incident

    **Your scope** (just-in-time):
    Read ONLY these files:
    - ingestion/utils.py (validation)
    - ingestion/scrapers/news_scraper.py (matching)
    - ingestion/config.py (keywords)

    **Deliverable**:
    - Root cause (1-2 sentences)
    - Code references (file:line)
    - Recommended fix (concrete code)
    """
)
```

---

## 5. Tool Design Patterns

### Principles from Anthropic

**Self-Contained Tools**:
- Each tool does ONE thing well
- Clear input/output contracts
- Robust error handling

**Unambiguous Parameters**:
- Descriptive names
- Type-safe definitions
- Validation built-in

**Avoid Bloat**:
- Don't create "do everything" tools
- Prefer composition over monoliths

### DroneWatch Application

**Good Tool Usage** ✅:
```bash
# Read specific file (just-in-time)
Read(file_path="ingestion/utils.py", limit=50)

# Targeted search (progressive)
Grep(pattern="is_drone_incident", path="ingestion", output_mode="content")

# Focused agent (sub-agent)
Task(description="Analyze scraper", prompt="[focused scope]")
```

**Bad Tool Usage** ❌:
```bash
# Load everything (context bloat)
Bash("find . -name '*.py' -exec cat {} \;")

# Vague search (too broad)
Grep(pattern=".*", path=".")

# Unfocused agent (no clear scope)
Task(description="Fix everything", prompt="Make it better")
```

---

## 6. Anti-Patterns to Avoid

### From Anthropic Research

**❌ Context Bloat**:
- Loading all files upfront
- Exhaustive edge case documentation
- Redundant information

**❌ Vague Guidance**:
- High-level instructions without specifics
- "Make it better" without criteria
- No clear success metrics

**❌ Brittle Logic**:
- Hardcoded complex rules in prompts
- Over-specified behavior
- Rigid workflows that don't adapt

**❌ Premature Optimization**:
- Investigating everything before finding issues
- Reading code "just in case"
- Building tools before knowing needs

### DroneWatch Examples

**Anti-Pattern**: Read entire codebase
```bash
# ❌ BAD
for file in $(find . -name "*.py"); do
    cat $file
done
# Result: 873 files, context rot, no findings
```

**Best Practice**: Progressive investigation
```bash
# ✅ GOOD
1. Map structure (tree -L 2)
2. Define questions (what's broken?)
3. Targeted reading (3 files max)
4. Root cause found ✅
```

---

## 7. Practical Workflow for DroneWatch

### Step 1: Architecture Mapping (5 min)
```bash
# Get lightweight identifier map
tree -L 2 -I 'node_modules|__pycache__|.next|venv'

# Count files (don't load)
find . -type f -name "*.py" | wc -l

# Document in INVESTIGATION_FINDINGS.md
```

### Step 2: Define Questions (5 min)
```markdown
## Investigation Questions

### Q1: What's the main issue?
**Evidence**: [API output, user complaint, error logs]
**Status**: 🔍 NEEDS INVESTIGATION

### Q2: Are there related issues?
**Evidence**: [Build warnings, deprecations]
**Status**: ⏳ PENDING

### Q3: What's already documented?
**Evidence**: [Read SESSION_SUMMARY, CLAUDE.md]
**Status**: ✅ REVIEWED
```

### Step 3: Progressive Investigation (10-30 min)
```python
# Launch focused sub-agent per question
Task(
    description="Analyze [specific concern]",
    prompt="""
    **Focused task**: Answer Q1
    **Scope**: Read ONLY [3-5 files]
    **Deliverable**: Root cause + fix
    """
)

# Document findings in structured notes
# Repeat for next question only if needed
```

### Step 4: Structured Documentation (5 min)
```markdown
## Findings

### 🔴 CRITICAL
1. **Issue** - Root cause, file:line, fix, effort ✅

### Decision Log
**Why focused on scraper?** - API evidence showed bad data
**Why sub-agent?** - Specialized task, clear scope
**Why not read all files?** - Diminishing returns
```

### Step 5: Action Plan (5 min)
```markdown
## Next Actions

**Immediate** (do now):
1. Apply word boundary fix - 5 min
2. Fix Next.js warnings - 15 min

**High Priority** (today):
3. Investigate sources issue - Sub-agent
4. Run migration 008 - 2 min

**Medium Priority** (this week):
5. Update dependencies - 2-3 hours
```

---

## 8. Success Metrics

### How to Know It's Working

**Before Context Engineering**:
- 2-3 hours to find issue
- Read 100+ files
- Vague findings
- Context rot midway
- "I think maybe..."

**After Context Engineering**:
- 15-30 min to find issue ✅
- Read 3-5 files ✅
- Specific findings with file:line ✅
- Persistent memory ✅
- "Root cause: file.py:139, fix: [code]" ✅

### DroneWatch Results

**Investigation**: Content filtering issue
- **Time**: 15 minutes (vs 2+ hours traditional)
- **Files read**: 3 (vs 50+ traditional)
- **Finding**: Specific bug with line number ✅
- **Fix**: Concrete code change ✅
- **Confidence**: HIGH (evidence-based)

---

## 9. Templates for Future Use

### Investigation Template
```markdown
# [Feature/Issue] Investigation

## Architecture (Lightweight Identifiers)
[Map relevant components only]

## Questions (Progressive Disclosure)
Q1: [High-level] → Investigate [3 files] → Finding: [specific]
Q2: [Next question] → Status: PENDING

## Findings (Structured Notes)
- 🔴 CRITICAL: [issue] - [file:line] - [fix]
- ⚠️ HIGH: [issue] - [evidence]

## Decision Log
**Why X?** - [reasoning]
```

### Sub-Agent Launch Template
```python
Task(
    subagent_type="general-purpose",
    description="[5-word description]",
    prompt="""
    **Focused task**: [Specific question to answer]

    **Context** (lightweight identifiers):
    - Repository: [path]
    - Issue: [1-2 sentence summary]
    - Evidence: [Specific observation]

    **Your scope** (just-in-time context):
    Read ONLY these files:
    - [file1.py] ([why needed])
    - [file2.py] ([why needed])
    - [file3.py] ([why needed])

    **Answer these questions**:
    1. [Specific question]
    2. [Specific question]
    3. [Specific question]

    **Deliverable**:
    - Root cause (1-2 sentences)
    - Code references (file:line format)
    - Recommended fix (concrete code change)

    **Important**:
    - Do NOT explore broadly
    - Focus ONLY on [specific concern]
    - Provide actionable findings
    """
)
```

---

## 10. Integration with Claude Code

### Leverage Native Tools

**File Operations**:
```python
# ✅ Good: Targeted reading
Read(file_path="specific/file.py", limit=50)

# ❌ Bad: Load everything
Bash("cat **/*.py")
```

**Search Operations**:
```python
# ✅ Good: Specific pattern
Grep(pattern="is_drone_incident", path="ingestion", output_mode="content", -n=True)

# ❌ Bad: Broad search
Grep(pattern=".*", path=".")
```

**Code Exploration**:
```python
# ✅ Good: Progressive discovery
Glob(pattern="**/scrapers/*.py")  # Find candidates
Read("ingestion/scrapers/news_scraper.py", limit=100)  # Read relevant

# ❌ Bad: Exhaustive loading
for file in glob("**/*.py"):
    read(file)
```

### Persistent Memory Strategy

**Session-Level** (ephemeral):
- TodoWrite for current task tracking
- In-memory investigation notes

**Project-Level** (persistent):
- INVESTIGATION_FINDINGS.md (findings)
- CONTEXT_ENGINEERING.md (methodology)
- SESSION_SUMMARY_*.md (history)
- CLAUDE.md (instructions)

**Cross-Session Continuity**:
```markdown
1. New session starts
2. Read INVESTIGATION_FINDINGS.md (catch up)
3. Read TODO list from previous session
4. Continue where left off
5. Update findings with new discoveries
```

---

## 11. Continuous Improvement

### Track What Works

**Effective Patterns** (keep using):
- Sub-agent for scraper analysis → Found bug in 15 min ✅
- Progressive disclosure → Avoided reading 870 unnecessary files ✅
- Structured notes → Easy handoff to next session ✅

**Ineffective Patterns** (stop using):
- Reading all session summaries → Too much context
- Broad searches → Low signal-to-noise
- Premature optimization → Wasted effort

### Iterate and Refine

**After each investigation**:
1. What worked well?
2. What was inefficient?
3. How can we improve?
4. Update this document

---

## Summary: Context Engineering Checklist

✅ **Lightweight Identifiers**: Map structure, don't load all files
✅ **Progressive Disclosure**: Start high-level, drill down based on evidence
✅ **Structured Note-Taking**: Document findings in persistent markdown files
✅ **Sub-Agent Architecture**: Delegate focused tasks to specialized agents
✅ **Just-in-Time Context**: Load content only when needed
✅ **Specific Deliverables**: File:line references, concrete fixes
✅ **Decision Logging**: Document why you chose each approach
✅ **Avoid Anti-Patterns**: No context bloat, vague guidance, or premature loading

---

**Last Updated**: October 3, 2025
**Status**: Active methodology for DroneWatch development
**Reference**: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

🤖 Generated with [Claude Code](https://claude.com/claude-code)
