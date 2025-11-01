# Textbox Documentation Guide

**Quick navigation to all project documentation**

---

## 🚀 Getting Started

**New to the project?** Start here:

1. **README.md** - Project overview and installation
2. **docs/getting-started.md** - Usage tutorial
3. **docs/examples.md** - Code examples

---

## 📋 Current Development Planning

**For developers continuing work on textbox:**

### Primary Documents (claude-output/plan-v2/)

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[IMPROVEMENT_SUMMARY.md](claude-output/plan-v2/IMPROVEMENT_SUMMARY.md)** | Executive summary of recommendations | Start here - 5 min read |
| **[IMPROVEMENT_PLAN.md](claude-output/plan-v2/IMPROVEMENT_PLAN.md)** | Detailed implementation guide | When implementing features - 30 min read |
| **[ROADMAP.md](claude-output/plan-v2/ROADMAP.md)** | Version planning with checkboxes | Track progress - update as you work |
| **[README.md](claude-output/plan-v2/README.md)** | Plan navigation guide | How to use these docs |

**Quick link**: `claude-output/plan-v2/README.md` explains how to use all planning documents.

---

## 📚 Project Context

**For understanding project history and decisions:**

### [docs/PROJECT_HISTORY.md](docs/PROJECT_HISTORY.md)
**THE definitive source for project context**

Consolidated history covering:
- ✅ What's been completed (refactoring, testing, type hints)
- ✅ Current state (82% coverage, 329 tests, 0 bugs)
- ✅ Technology decisions and why
- ✅ Architecture patterns and rationale
- ✅ Lessons learned
- ✅ What's next (v0.2.0 priorities)

**Read this if**: You're an AI agent continuing work or a developer joining the project.

---

## 📖 User Documentation

**For users of the textbox library:**

Located in `docs/`:
- **quick-start.md** - Get up and running quickly
- **getting-started.md** - Comprehensive tutorial
- **api-reference.md** - API documentation
- **architecture.md** - How textbox is built
- **text-handling.md** - Working with Text objects
- **color-support.md** - Using colors
- **examples.md** - Code examples
- **troubleshooting.md** - Common issues
- **advanced-topics.md** - Advanced usage

---

## 🗄️ Historical Documentation

**For reference only - superseded by current docs:**

### archive/
Contains detailed historical reports from development phases:

- **progress-reports-legacy/** - Step-by-step refactoring and testing reports
- **claude-output-legacy/** - Original code reviews and analysis

**When to read**: Only if you need to understand a specific past decision in detail.

**Instead, read**: `docs/PROJECT_HISTORY.md` for consolidated context.

---

## 🎯 Quick Decision Tree

**"What should I read?"**

### I want to...

**...understand the project quickly**
→ Read `docs/PROJECT_HISTORY.md` (10 min)

**...start development work**
→ Read `claude-output/plan-v2/IMPROVEMENT_SUMMARY.md` (5 min)
→ Then check `claude-output/plan-v2/ROADMAP.md` for priorities

**...implement a specific feature**
→ Read relevant section in `claude-output/plan-v2/IMPROVEMENT_PLAN.md`
→ Check `ROADMAP.md` checkboxes to track progress

**...use textbox in my application**
→ Read `docs/quick-start.md`
→ Browse `docs/examples.md`

**...understand a past decision**
→ Check `docs/PROJECT_HISTORY.md` first
→ If not answered, check `archive/` for details

**...contribute to the project**
→ Read `docs/PROJECT_HISTORY.md` section "For Future Contributors"
→ Check `claude-output/plan-v2/ROADMAP.md` for current priorities

---

## 📁 Directory Structure

```
textbox/
├── README.md                      # Project overview
├── DOCUMENTATION_GUIDE.md         # This file - navigation hub
│
├── docs/                          # User documentation
│   ├── PROJECT_HISTORY.md         # 🌟 Consolidated project context
│   ├── getting-started.md         # Tutorial
│   ├── api-reference.md           # API docs
│   └── [other guides...]
│
├── claude-output/                 # Development planning
│   └── plan-v2/                   # 🌟 Current development plan
│       ├── README.md              # Plan navigation
│       ├── IMPROVEMENT_SUMMARY.md # 🌟 Start here for development
│       ├── IMPROVEMENT_PLAN.md    # Detailed implementation guide
│       └── ROADMAP.md             # Version planning & tracking
│
└── archive/                       # Historical documentation
    ├── README.md                  # Archive guide
    ├── progress-reports-legacy/   # Detailed historical reports
    └── claude-output-legacy/      # Original code reviews
```

---

## 🎨 Document Status Legend

| Symbol | Meaning |
|--------|---------|
| 🌟 | Essential reading |
| ✅ | Complete and current |
| 🔄 | Active - update as you work |
| 🗄️ | Archived - reference only |

---

## 🔍 Finding Information

### Current State Questions
- "What's the test coverage?" → `docs/PROJECT_HISTORY.md`
- "What bugs were fixed?" → `docs/PROJECT_HISTORY.md`
- "What's the package structure?" → `docs/PROJECT_HISTORY.md`

### Future Work Questions
- "What should I work on next?" → `claude-output/plan-v2/ROADMAP.md`
- "How do I implement visual mode?" → `claude-output/plan-v2/IMPROVEMENT_PLAN.md`
- "What's the priority order?" → `claude-output/plan-v2/IMPROVEMENT_SUMMARY.md`

### Historical Questions
- "Why was uvloop removed?" → `docs/PROJECT_HISTORY.md`
- "What was the refactoring process?" → `archive/progress-reports-legacy/`
- "What did the code review find?" → `archive/claude-output-legacy/review/`

### Usage Questions
- "How do I use textbox?" → `docs/quick-start.md`
- "What's the API?" → `docs/api-reference.md`
- "Can I see examples?" → `docs/examples.md`

---

## ✨ For AI Agents

**Context Loading Priority:**

1. **First**, read `docs/PROJECT_HISTORY.md` (comprehensive context)
2. **Then**, read `claude-output/plan-v2/IMPROVEMENT_SUMMARY.md` (current priorities)
3. **Finally**, check `claude-output/plan-v2/ROADMAP.md` (specific tasks)

This gives you complete context without reading 10+ historical documents.

---

## 📝 Keeping Documentation Updated

### When you complete work:

1. ✅ Check off items in `claude-output/plan-v2/ROADMAP.md`
2. ✅ Update metrics in `docs/PROJECT_HISTORY.md` if significant (e.g., new version)
3. ✅ Update user docs in `docs/` if API changes

### Don't update:
- ❌ `archive/` - Historical, kept as-is
- ❌ `claude-output/plan-v2/IMPROVEMENT_PLAN.md` - Reference document

---

**Last Updated**: 2025-10-31
**Documentation Status**: ✅ Consolidated and organized
**Next Review**: After v0.2.0 release
