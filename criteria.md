# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service.

---

## 1. False positives stay below 10%

Across 10 personal writing samples, no more than 1 item may be labeled high-confidence AI.

**Why this target:** A wrong accusation against a real writer is the expensive mistake, so I am setting a conservative false-positive limit and accepting that some AI text may slip through.

---

## 2. Human and AI text must separate cleanly

For a clearly AI text and a clearly human text, the combined score must differ by at least 0.25.

**Why this target:** A detector that cannot push obvious cases apart does not provide a usable decision boundary, and the whole system becomes too noisy to trust.

---

## 3. All three labels remain reachable

The service must produce high-confidence human, unsure, and high-confidence AI labels across the test inputs I select.

**Why this target:** A label that can never appear is not helpful to a person reading the result, and it leaves the service with a blind spot instead of a decision.

---

## 4. Appeals are recorded and changed to under review

If a valid content_id is submitted to `/appeal`, the request must succeed, the audit log must record an appeal event, and the item must show `under_review` in the log.

**Why this target:** A writer who challenges a label should see proof that the system took them seriously, and the log needs that trace for later diagnosis.

---

## 5. Bad input is rejected cleanly

For missing, empty, or extremely large text values, the service must return an HTTP 400 and must not create a decision record.

**Why this target:** Malformed input is a routine real-world failure mode, and a crash or silent acceptance would be worse than a clear rejection.
