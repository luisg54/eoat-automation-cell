# EOAT Automation Cell — Test Plan

**Written:** YYYY-MM-DD
**Tests requirements from:** `requirements.md`

Every performance requirement needs a test that produces a number. A project without this
file is a project that stops at CAD.

## Test setup

**Equipment:**
- Measurement instrument, resolution, and how it is zeroed

**Fixturing:** <how the part and the measurement are held so results are repeatable>

**Sources of measurement error:** <what could make these numbers wrong>

## Tests

### T-01 — <Test name>

| | |
|---|---|
| **Verifies** | P-01 |
| **Method** | <exact procedure, repeatable by someone else> |
| **Sample size** | n = |
| **Pass criterion** | |

**Raw data:** `<datafile>`

**Result:**

**Pass / Fail:**

**Observations:** <anything unexpected — this is often where the real finding is>

---

### T-02 — <Test name>

<repeat>

---

## Results summary

| Test | Requirement | Target | Measured | Pass |
|---|---|---|---|---|
| T-01 | P-01 | | | |

## Failure analysis

For every failure: what happened, root cause, fix, and re-test result. Do not delete failed
runs — they are the strongest interview material and the honest record of the design.

| Run | Failure mode | Root cause | Fix | Re-test result |
|---|---|---|---|---|
| | | | | |

## Conclusions

<What the data actually supports. State it no more strongly than the measurement allows.>

## Log to Engineering OS

Record each validation event with its measured metric and validation status. Status
vocabulary: *proposed → designed → machined → installed → field-tested → validated*. Never
overstate it.
