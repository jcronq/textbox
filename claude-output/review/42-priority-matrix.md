# Priority Matrix - All Improvements Ranked

Complete list of all recommended improvements, prioritized by impact and effort.

---

## Critical Priority (P0) - Do First

| ID | Issue | File | Effort | Impact | Week |
|----|-------|------|--------|--------|------|
| P0-1 | IndexError in next_line | text.py:191 | 5min | Critical | 1 |
| P0-2 | Missing return in replace_character | text_line.py:153 | 5min | Critical | 1 |
| P0-3 | Property getter side effect | input_box.py:100 | 5min | Critical | 1 |
| P0-4 | Wrong type in erase() | text_box.py:188 | 10min | Critical | 1 |
| P0-5 | Strip result not assigned | input_output_workspace.py:222 | 2min | Critical | 1 |
| P0-6 | State updated before validation | window.py:144 | 15min | High | 1 |
| P0-7 | Assignment vs comparison | curses_utils.py:71 | 2min | Medium | 1 |
| P0-8 | ColorCode not Enum + typo | color_code.py | 20min | Medium | 1 |
| P0-9 | Type hint mismatch | __init__.py:78 | 10min | Medium | 1 |
| P0-10 | Create pytest configuration | - | 30min | High | 1 |
| P0-11 | Create GitHub Actions CI | - | 2h | High | 1 |
| P0-12 | Add TextSegment tests | - | 4h | Critical | 1 |
| P0-13 | Add App tests | - | 8h | Critical | 1 |
| P0-14 | Add InputBox tests | - | 8h | High | 1 |
| P0-15 | Enhance README.md | - | 30min | High | 1 |

**Total P0: 15 items, ~24 hours**

---

## High Priority (P1) - Week 2-3

### Testing (P1-T)

| ID | Issue | Effort | Impact | Week |
|----|-------|--------|--------|------|
| P1-T1 | Add TextBox tests | 6h | High | 2 |
| P1-T2 | Add Window tests | 6h | High | 2 |
| P1-T3 | Add InputOutputWorkspace tests | 8h | High | 2 |
| P1-T4 | Add integration tests | 12h | High | 2 |
| P1-T5 | Add edge case tests | 8h | Medium | 2 |
| P1-T6 | Add async/InputManager tests | 8h | High | 2 |
| P1-T7 | Expand Text class tests | 4h | Medium | 2 |
| P1-T8 | Fix duplicate test names | 1h | Low | 2 |
| P1-T9 | Achieve 70%+ coverage | - | High | 2 |

**Subtotal Testing: 9 items, ~53 hours**

### Infrastructure (P1-I)

| ID | Issue | Effort | Impact | Week |
|----|-------|--------|--------|------|
| P1-I1 | Add coverage reporting | 2h | High | 1 |
| P1-I2 | Configure ruff linter | 2h | High | 3 |
| P1-I3 | Configure mypy | 2h | High | 3 |
| P1-I4 | Add pre-commit hooks | 2h | High | 3 |
| P1-I5 | Set up tox | 2h | Medium | 3 |
| P1-I6 | Complete pyproject.toml | 2h | High | 1 |
| P1-I7 | Add Dependabot | 1h | Medium | 3 |
| P1-I8 | Create MANIFEST.in | 30min | Medium | 3 |

**Subtotal Infrastructure: 8 items, ~13.5 hours**

### Documentation (P1-D)

| ID | Issue | Effort | Impact | Week |
|----|-------|--------|--------|------|
| P1-D1 | Create CHANGELOG.md | 30min | High | 1 |
| P1-D2 | Create CONTRIBUTING.md | 1h | Medium | 1 |
| P1-D3 | Add docstrings to App | 2h | High | 3 |
| P1-D4 | Add docstrings to Text classes | 3h | High | 3 |
| P1-D5 | Add docstrings to UI classes | 3h | High | 3 |
| P1-D6 | Create comprehensive examples | 4h | High | 3 |
| P1-D7 | Create examples/README.md | 1h | Medium | 3 |

**Subtotal Documentation: 7 items, ~14.5 hours**

**Total P1: 24 items, ~81 hours**

---

## Medium Priority (P2) - Week 3-4

### Code Quality (P2-Q)

| ID | Issue | Effort | Impact | Week |
|----|-------|--------|--------|------|
| P2-Q1 | Add comprehensive type hints | 8h | Medium | 3 |
| P2-Q2 | Add validation to constructors | 4h | Medium | 4 |
| P2-Q3 | Improve error messages | 3h | Medium | 4 |
| P2-Q4 | Add logging throughout | 2h | Low | 4 |
| P2-Q5 | Fix incorrect type hints | 2h | Medium | 3 |

**Subtotal Quality: 5 items, ~19 hours**

### Refactoring (P2-R)

| ID | Issue | Effort | Impact | Week |
|----|-------|--------|--------|------|
| P2-R1 | Refactor colored.py (remove duplication) | 2h | Medium | 4 |
| P2-R2 | Refactor mode entry methods | 3h | Medium | 4 |
| P2-R3 | Refactor SegmentedTextLine slicing | 4h | Medium | 4 |
| P2-R4 | Refactor complex backspace logic | 3h | Medium | 4 |
| P2-R5 | Simplify command handlers | 3h | Medium | 4 |
| P2-R6 | Extract validation methods | 2h | Low | 4 |

**Subtotal Refactoring: 6 items, ~17 hours**

### Performance (P2-P)

| ID | Issue | Effort | Impact | Week |
|----|-------|--------|--------|------|
| P2-P1 | Cache line offsets in Text | 3h | High | 4 |
| P2-P2 | Lazy reduce in SegmentedTextLine | 2h | Medium | 4 |
| P2-P3 | Avoid unnecessary copies | 2h | Medium | 4 |
| P2-P4 | Optimize cursor_position | 2h | High | 4 |
| P2-P5 | Profile and benchmark | 3h | Medium | 4 |

**Subtotal Performance: 5 items, ~12 hours**

### Organization (P2-O)

| ID | Issue | Effort | Impact | Week |
|----|-------|--------|--------|------|
| P2-O1 | Move tests to tests/ directory | 2h | Medium | 2 |
| P2-O2 | Remove textbox.bck/ | 5min | Low | 1 |
| P2-O3 | Remove scratch.py | 2min | Low | 1 |
| P2-O4 | Improve .gitignore | 5min | Low | 1 |
| P2-O5 | Create textbox/py.typed | 1min | Medium | 3 |
| P2-O6 | Organize into subpackages (optional) | 8h | Low | - |

**Subtotal Organization: 6 items, ~10 hours (excluding optional)**

**Total P2: 22 items, ~58 hours**

---

## Low Priority (P3) - Nice to Have

### Advanced Features (P3-F)

| ID | Issue | Effort | Impact | Week |
|----|-------|--------|--------|------|
| P3-F1 | Implement undo/redo | 16h | Medium | 5 |
| P3-F2 | Add search/replace | 12h | Medium | 5 |
| P3-F3 | Add clipboard support | 8h | Low | 5 |
| P3-F4 | Add mouse support | 12h | Low | 5 |
| P3-F5 | Create plugin system | 20h | Low | 6 |
| P3-F6 | Add event system | 12h | Medium | 5 |

**Subtotal Features: 6 items, ~80 hours**

### Publishing (P3-P)

| ID | Issue | Effort | Impact | Week |
|----|-------|--------|--------|------|
| P3-P1 | Set up Sphinx docs | 8h | Medium | 3 |
| P3-P2 | Publish to PyPI | 4h | Medium | 6 |
| P3-P3 | Set up Read the Docs | 2h | Low | 6 |
| P3-P4 | Create video tutorials | 12h | Low | 6 |
| P3-P5 | Write blog post | 4h | Low | 6 |

**Subtotal Publishing: 5 items, ~30 hours**

### Polish (P3-L)

| ID | Issue | Effort | Impact | Week |
|----|-------|--------|--------|------|
| P3-L1 | Add issue templates | 1h | Low | 3 |
| P3-L2 | Add PR template | 30min | Low | 3 |
| P3-L3 | Add security scanning | 1h | Medium | 3 |
| P3-L4 | Add badges to README | 30min | Low | 3 |
| P3-L5 | Create architecture diagrams | 4h | Low | 6 |

**Subtotal Polish: 5 items, ~7 hours**

**Total P3: 16 items, ~117 hours**

---

## Summary by Category

| Category | P0 | P1 | P2 | P3 | Total Items | Total Hours |
|----------|----|----|----|----|-------------|-------------|
| Bug Fixes | 9 | 0 | 0 | 0 | 9 | 1h |
| Testing | 3 | 9 | 0 | 0 | 12 | 61h |
| Infrastructure | 3 | 8 | 0 | 0 | 11 | 17h |
| Documentation | 1 | 7 | 0 | 0 | 8 | 15h |
| Code Quality | 0 | 0 | 5 | 0 | 5 | 19h |
| Refactoring | 0 | 0 | 6 | 0 | 6 | 17h |
| Performance | 0 | 0 | 5 | 0 | 5 | 12h |
| Organization | 0 | 0 | 6 | 0 | 6 | 10h |
| Features | 0 | 0 | 0 | 6 | 6 | 80h |
| Publishing | 0 | 0 | 0 | 5 | 5 | 30h |
| Polish | 0 | 0 | 0 | 5 | 5 | 7h |
| **Total** | **15** | **24** | **22** | **16** | **77** | **269h** |

---

## Recommended Execution Order

### Phase 1: Foundation (Week 1, ~24 hours)
Focus on P0 items to establish stable foundation.

**Day 1:**
- [ ] P0-1 through P0-9 (bug fixes)
- [ ] P0-10 (pytest config)
- [ ] P2-O2, P2-O3, P2-O4 (cleanup)

**Day 2:**
- [ ] P0-11 (GitHub Actions)
- [ ] P1-I1 (coverage)
- [ ] P1-I6 (pyproject.toml)

**Day 3:**
- [ ] P0-12 (TextSegment tests)
- [ ] P0-13 (App tests)

**Day 4-5:**
- [ ] P0-14 (InputBox tests)
- [ ] P0-15, P1-D1, P1-D2 (docs)

### Phase 2: Testing (Week 2, ~53 hours)
Focus on P1-T items to achieve comprehensive coverage.

**Day 6-10:**
- [ ] All P1-T items
- [ ] P2-O1 (move tests)

### Phase 3: Quality (Week 3, ~28 hours)
Focus on P1-I and P1-D items.

**Day 11-15:**
- [ ] Remaining P1-I items
- [ ] All P1-D items
- [ ] P2-O5 (py.typed)

### Phase 4: Optimization (Week 4, ~58 hours)
Focus on P2 items.

**Day 16-20:**
- [ ] All P2-Q items
- [ ] All P2-R items
- [ ] All P2-P items

### Optional Phase 5-6 (Weeks 5-6, ~117 hours)
P3 items if time and motivation allow.

---

## Effort vs Impact Matrix

```
High Impact ▲
            │
     P0-1 ──┼── P0-12,13,14
     P0-2   │   P1-T4
     P0-3   │   P2-P1,4
     P0-4   │
            │
     P1-I2 ─┼── P1-T1,2,3
     P1-I3  │   P1-D3,4,5
     P1-D6  │   P2-R1-5
            │
            │
     P2-Q1 ─┼── P2-P2,3,5
     P3-F1  │   P3-F6
     P3-P1  │
            │
Low Impact  └──────────────────────▶
         Low Effort    High Effort
```

---

## Quick Reference: What to Do When

### "I have 1 day"
→ Do P0-1 through P0-15 (critical bugs + basic setup)

### "I have 1 week"
→ Complete Phase 1 (all P0 items)

### "I have 2 weeks"
→ Complete Phases 1-2 (P0 + testing)

### "I have 1 month"
→ Complete Phases 1-4 (P0, P1, P2)

### "I want production-ready"
→ Complete Phases 1-4, select from Phase 5

---

## Dependencies

### Must Complete Before Others

```
P0-10 (pytest) → All test items
P0-11 (CI) → P1-I1 (coverage)
P0-12 (TextSegment tests) → P2-R3 (refactor)
P1-I2,3 (ruff, mypy) → P2-Q1 (type hints)
P1-D3,4,5 (docstrings) → P3-P1 (Sphinx)
All P0 items → Safe to refactor
```

### Can Be Done In Parallel

- Bug fixes (P0-1 to P0-9)
- Test creation (P0-12, P0-13, P0-14)
- Documentation (P1-D items)
- Infrastructure (P1-I items)

---

## Tracking Progress

### Checklist Format

Copy to your project management tool:

```markdown
## Week 1: Stabilization
- [ ] P0-1: Fix text.py:191 IndexError
- [ ] P0-2: Fix text_line.py:153 missing return
- [ ] P0-3: Fix input_box.py:100 getter side effect
- [ ] P0-4: Fix text_box.py:188 type error
- [ ] P0-5: Fix input_output_workspace.py:222 strip
- [ ] P0-6: Fix window.py:144 state validation
- [ ] P0-7: Fix curses_utils.py:71 assignment
- [ ] P0-8: Fix color_code.py Enum + typo
- [ ] P0-9: Fix __init__.py:78 type hint
- [ ] P0-10: Create pytest configuration
- [ ] P0-11: Create GitHub Actions CI
- [ ] P0-12: Add TextSegment tests
- [ ] P0-13: Add App tests
- [ ] P0-14: Add InputBox tests
- [ ] P0-15: Enhance README.md

## Week 2: Testing
[Continue with P1-T items...]
```

---

## Success Metrics by Phase

### After Phase 1:
- ✅ 0 critical bugs
- ✅ CI running
- ✅ 50%+ coverage
- ✅ Professional README

### After Phase 2:
- ✅ 70%+ coverage
- ✅ Integration tests
- ✅ All critical components tested

### After Phase 3:
- ✅ Type hints complete
- ✅ Linting automated
- ✅ Documentation complete

### After Phase 4:
- ✅ 80%+ coverage
- ✅ Code refactored
- ✅ Performance optimized
- ✅ Production-ready

---

## Final Notes

**Remember:**
- P0 items are non-negotiable
- P1 items make it maintainable
- P2 items make it excellent
- P3 items make it exceptional

**Start with P0, add P1, then decide on P2/P3 based on goals.**

Good luck! 🚀
