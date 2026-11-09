# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

A submission arrives as JSON, is validated, scored by two signals, combined into one score, turned into a human-readable label, and then written to the audit log. A later appeal checks that the content_id exists, records the challenge, and marks the item as `under_review` without re-running the detector.

---

## Signals and Scoring

### Signal one — the model signal

**What it measures:** It reads the text for predictability using the local GPT-2 model; lower surprise means a more machine-like result.

**Why that might differ between human and AI writing:** Human writing has more surprising word choices and topic jumps, while AI prose tends to follow common patterns and familiar phrasing.

**What it can't see:** It cannot tell whether a sentence is meaningful or whether the writer is a person; it only sees how expected the text is to the model.

### Signal two — the style signal

**What it measures:** It looks at sentence-length spread, vocabulary variety, and punctuation density to judge how rigid or varied the writing style is.

**Why that might differ between human and AI writing:** AI text often uses more regular sentence shapes and repeated vocabulary, while humans vary length and rhythm more.

**What it can't see:** It cannot read the meaning of the words and can be fooled by a human writer who deliberately uses repetitive or unusual formatting.

### The combining rule

**The rule:** I combine the model and style signals with a weighted average, favoring the model signal because it uses the local language model directly while the style signal is a weaker structural cue.

**The numbers:** `WEIGHT_MODEL_SIGNAL = 0.6`, `WEIGHT_STYLE_SIGNAL = 0.4` in `config.py`.

**Where it lives:** `scoring.py::combine_signals`

**A case where my two signals split, and what my rule does with it:** If the model says the text is AI-like but the writing style is very human-like, the average lands in the unsure band instead of forcing a hard accusation.

---

## Label Variants

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – 0.45 inclusive | We think this was probably written by a person. |
| unsure | above 0.45 and below 0.70 | We are not confident either way; this may have been written by a person or by AI. |
| high-confidence AI | 0.70 – 1.00 inclusive | We think this was probably written by AI. |

**Why I worded the "unsure" one this way:** It acknowledges uncertainty without sounding like an accusation, which matters because a real writer could receive it on their own work.

---

## Sample Run

**A submission**

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "The weather was mild and the walk felt easy. We talked for a while and then headed home.", "creator_id": "demo-user"}'
```

```json
{
  "content_id": "7dd3d75d-4e2f-4dbe-bd0e-7a924ee9b012",
  "guess": "human",
  "confidence": 0.33,
  "label": "We think this was probably written by a person.",
  "model_score": 0.29,
  "style_score": 0.38,
  "combined_score": 0.33
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "7dd3d75d-4e2f-4dbe-bd0e-7a924ee9b012", "reasoning": "This was my own writing and the score feels wrong."}'
```

```json
{
  "ok": true,
  "content_id": "7dd3d75d-4e2f-4dbe-bd0e-7a924ee9b012",
  "status": "under_review",
  "message": "Your appeal has been recorded and this item is now under review."
}
```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
[
  {"timestamp": "2026-11-08T00:00:00+00:00", "content_id": "7dd3d75d-4e2f-4dbe-bd0e-7a924ee9b012", "creator_id": "demo-user", "guess": "human", "model_score": 0.29, "style_score": 0.38, "combined_score": 0.33, "label": "We think this was probably written by a person.", "status": "decided"},
  {"timestamp": "2026-11-08T00:01:00+00:00", "content_id": "7dd3d75d-4e2f-4dbe-bd0e-7a924ee9b012", "creator_id": "demo-user", "event": "appeal", "status": "under_review", "reasoning": "This was my own writing and the score feels wrong."}
]
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I asked for a quick check on the wording of the service contract and the confidence thresholds.
- *What came back:* Suggestions for clearer phrases and a simpler label structure.
- *What I changed:* I kept the final logic and tuned the wording to match the project requirements and the idea of a human-facing explanation.

**Moment 2**

- *What I asked for:* I asked for help comparing model-based and style-based signals to design a safe combined score.
- *What came back:* A reminder that the expensive mistake is a false positive, so the system should prefer a conservative band.
- *What I changed:* I used that to keep the thresholds broad enough for uncertain cases while still labeling clear AI and clear human texts strongly.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 per minute, 80 per day

**Why those numbers and not others:** Five requests per minute allows a writer to submit a few revisions, while stopping a rapid burst after the fifth request. The daily cap of 80 leaves room for legitimate iteration but limits sustained automated probing. These are local-project limits, not production capacity settings.

**What a caller counts as:** A non-empty `creator_id` is the primary key; requests without one fall back to the remote address. This avoids treating every person behind one network as a single caller, but a client can submit multiple creator IDs. The limiter uses in-memory storage, so restarts reset counts and multiple service instances would not share them.

**The run of status codes when I pushed past it:**

```bash
$ python run_attacks.py --flood 15
```

```text
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
10 of 15 were rate limited.
```

Full output: `results/flood_2026-11-09_0012.md`.

---

## Attack Run — Before

This matched baseline uses the original thresholds (`0.35` human, `0.65` AI) with rate limiting enabled. `run_attacks.py --set attack_set --label before` sent all 12 inputs. The five flood-family requests are within the configured five-per-minute allowance; the separate 15-request run above tests beyond that allowance.

| ID | Family | Targeting | Status | Guess | Score | Verdict |
|---|---|---|---|---|---|---|
| A01 | false_positive | flag-human | 200 | unsure | 0.503 | HELD — no AI accusation |
| A02 | plain_ai | flag-ai | 200 | unsure | 0.478 | BROKE — AI text not flagged |
| A03 | prompt_injection | model-evasion | 200 | unsure | 0.419 | HELD — not labeled human |
| A04 | style_evasion | shape-evasion | 200 | human | 0.152 | BROKE — evasion reached human label |
| A05 | whitespace_noise | shape-evasion | 200 | ai | 0.876 | HELD — still labeled AI |
| F01 | flood_same_creator | rate-limit | 200 | human | 0.260 | HELD — within five-request allowance |
| F02 | flood_same_creator | rate-limit | 200 | human | 0.260 | HELD — within five-request allowance |
| F03 | flood_same_creator | rate-limit | 200 | human | 0.260 | HELD — within five-request allowance |
| F04 | flood_same_creator | rate-limit | 200 | human | 0.260 | HELD — within five-request allowance |
| F05 | flood_same_creator | rate-limit | 200 | human | 0.260 | HELD — within five-request allowance |
| M01 | bad_json | malformed-request | 400 | — | — | HELD — rejected |
| M02 | missing_text | malformed-request | 400 | — | — | HELD — rejected |

Full attack output: `results/attack_run_2026-11-09_0012_before.md`.

**Ten audit log entries from the attack run**

```json
[
  {"timestamp":"2026-11-09T05:12:27+00:00","content_id":"8b13cb6f-b639-4d1d-bd28-6f789c91be06","creator_id":"attacker_A01","guess":"unsure","model_score":0.4413,"style_score":0.5962,"combined_score":0.5033,"label":"We are not confident either way; this may have been written by a person or by AI.","status":"decided"},
  {"timestamp":"2026-11-09T05:12:27+00:00","content_id":"9fcb9eaf-9988-49eb-a713-8f2970ec6149","creator_id":"attacker_A02","guess":"unsure","model_score":0.443,"style_score":0.5304,"combined_score":0.478,"label":"We are not confident either way; this may have been written by a person or by AI.","status":"decided"},
  {"timestamp":"2026-11-09T05:12:27+00:00","content_id":"51567c88-4fca-442c-ac16-4420a7462bd9","creator_id":"attacker_A03","guess":"unsure","model_score":0.2908,"style_score":0.6122,"combined_score":0.4194,"label":"We are not confident either way; this may have been written by a person or by AI.","status":"decided"},
  {"timestamp":"2026-11-09T05:12:27+00:00","content_id":"26dde914-67be-409e-ab3b-9eaf93cb8918","creator_id":"attacker_A04","guess":"human","model_score":0.0525,"style_score":0.3023,"combined_score":0.1524,"label":"We think this was probably written by a person.","status":"decided"},
  {"timestamp":"2026-11-09T05:12:28+00:00","content_id":"28e64ab4-97e7-4a30-88d0-3cc30a2a6d04","creator_id":"attacker_A05","guess":"ai","model_score":0.9214,"style_score":0.8079,"combined_score":0.876,"label":"We think this was probably written by AI.","status":"decided"},
  {"timestamp":"2026-11-09T05:12:28+00:00","content_id":"d02bb2eb-a7c4-4cb0-90d0-e65816066283","creator_id":"shared_flood","guess":"human","model_score":0.0,"style_score":0.65,"combined_score":0.26,"label":"We think this was probably written by a person.","status":"decided"},
  {"timestamp":"2026-11-09T05:12:28+00:00","content_id":"17f884eb-1cc8-4901-a5b0-64de5227753f","creator_id":"shared_flood","guess":"human","model_score":0.0,"style_score":0.65,"combined_score":0.26,"label":"We think this was probably written by a person.","status":"decided"},
  {"timestamp":"2026-11-09T05:12:28+00:00","content_id":"c7e0281b-b0c0-4979-bf9b-ed4b490e6ca8","creator_id":"shared_flood","guess":"human","model_score":0.0,"style_score":0.65,"combined_score":0.26,"label":"We think this was probably written by a person.","status":"decided"},
  {"timestamp":"2026-11-09T05:12:28+00:00","creator_id":"unknown","event":"rejected","status":"rejected","reason":"invalid_json","detail":"request body was not a JSON object"},
  {"timestamp":"2026-11-09T05:12:46+00:00","creator_id":"flood_tester","event":"rejected","status":"rejected","reason":"rate_limited","limit":"5 per 1 minute"}
]
```

**The single worst outcome:** `A04` is a style-manipulated input that reached the human label at `0.1524`. A reader could treat that label as proof the text was human even though the input was deliberately altered to evade the style signal.

---

## Run Log and Verdicts

The results below summarize the three trials in `results/run_2026-11-09_0012_before.md` and `results/run_2026-11-09_0012_after.md`. The before run used the original thresholds; the after run used the revised thresholds. Each trial repeats the same inputs.

| Criterion | Target | Before, each trial | Verdict |
|---|---|---|---|
| 1. False positives | No more than 1 of 10 personal samples labeled high-confidence AI | 1 AI, 9 unsure | MET (at limit) |
| 2. Score separation | Clearly human and AI scores differ by at least 0.25 | 0.6024 vs 0.4719; delta 0.1305 | MISSED |
| 3. Label coverage | Human, unsure, and AI labels all appear | unsure, unsure, unsure | MISSED |
| 4. Appeal path | Valid content becomes `under_review` | 200; under_review | MET |
| 5. Bad input | Missing, empty, and oversized text return 400 without a decision | 400 × 4 | MET |

| Criterion | After, each trial | Verdict |
|---|---|---|
| 1. False positives | 0 AI, 10 unsure | MET |
| 2. Score separation | 0.6024 vs 0.4719; delta 0.1305 | MISSED |
| 3. Label coverage | unsure, unsure, human | MISSED |
| 4. Appeal path | 200; under_review | MET |
| 5. Bad input | 400 × 4 | MET |

**Real output from one trial**, naming the file and functions that produced it:

```json
{"status":200,"guess":"unsure","confidence":0.6024,"model_score":0.6122,"style_score":0.5876,"label":"We are not confident either way; this may have been written by a person or by AI.","sent":"The weekend was quiet and the streets felt slow in the best way. I wal"}
{"status":200,"guess":"unsure","confidence":0.4719,"model_score":0.4193,"style_score":0.5509,"label":"We are not confident either way; this may have been written by a person or by AI.","sent":"The framework is optimized for scalability, transparency, and operatio"}
```

This excerpt is from `run_eval.py::main`; requests went through `app.py::submit` and scores were combined by `scoring.py::combine_signals`. The score delta is `0.1305`, below the criterion's `0.25` target.

**Diagnoses**

- Criterion 2 missed because the two signals and `scoring.py::combine_signals` produced scores only `0.1305` apart. The combined score for the human sample was actually higher than for the AI sample, so the pipeline does not separate these examples.
- Criterion 3 missed before and after: the after scores for label coverage were `0.478`, `0.6239`, and `0.3925`. The first two stay below the `0.70` AI threshold; the label mapping therefore never emits AI. The threshold change moves the last sample into human, but does not make all three labels reachable.
- Criterion 4 met: the corrected evaluation runner calls `/appeal` after each successful submission. All three appeals returned 200 with `status: "under_review"`, and the audit log records the appeal events.
- Criterion 5 met: the route rejects empty, missing, oversized, and null text with 400 responses and rejection log records; no decision records are created for those requests.

---

## The Improvement

**What I changed:** I changed only the label thresholds in `config.py`: `HUMAN_THRESHOLD` from `0.35` to `0.45`, and `AI_THRESHOLD` from `0.65` to `0.70`. The unsure band narrowed from 0.30 to 0.25, with its human boundary raised and its AI boundary raised.

**Which diagnosis pointed at it:** The baseline labeled one of ten personal-writing examples high-confidence AI, exactly at the allowed maximum, and none of the labels in the coverage set were human or AI. Raising the AI cutoff was intended to reduce false accusations; raising the human cutoff made a low-scoring borderline sample reach the human label. The signal formulas and weights did not change.

### Attack Run — After

`run_attacks.py --set attack_set --label after` ran the same 12 inputs with the revised thresholds. The limiter remained enabled in both runs.

| ID | Family | Targeting | Status | Guess | Score | Verdict |
|---|---|---|---|---|---|---|
| A01 | false_positive | flag-human | 200 | unsure | 0.503 | HELD — no AI accusation |
| A02 | plain_ai | flag-ai | 200 | unsure | 0.478 | BROKE — AI text not flagged |
| A03 | prompt_injection | model-evasion | 200 | human | 0.419 | BROKE — evasion reached human label |
| A04 | style_evasion | shape-evasion | 200 | human | 0.152 | BROKE — evasion reached human label |
| A05 | whitespace_noise | shape-evasion | 200 | ai | 0.876 | HELD — still labeled AI |
| F01 | flood_same_creator | rate-limit | 200 | human | 0.260 | HELD — within five-request allowance |
| F02 | flood_same_creator | rate-limit | 200 | human | 0.260 | HELD — within five-request allowance |
| F03 | flood_same_creator | rate-limit | 200 | human | 0.260 | HELD — within five-request allowance |
| F04 | flood_same_creator | rate-limit | 200 | human | 0.260 | HELD — within five-request allowance |
| F05 | flood_same_creator | rate-limit | 200 | human | 0.260 | HELD — within five-request allowance |
| M01 | bad_json | malformed-request | 400 | — | — | HELD — rejected |
| M02 | missing_text | malformed-request | 400 | — | — | HELD — rejected |

Full attack output: `results/attack_run_2026-11-09_0012_after.md`.

**Did it help, and how do I know:** It reduced the false-positive count on the ten personal samples from one to zero, while keeping criterion 1 within target in all three trials. However, the plain AI sample is still unsure, and the prompt-injection sample changed from unsure before to human after. The improvement reduced one kind of error but made an evasion more effective; it did not improve score separation or produce an AI label in the coverage set.

---

## What's Still Broken

`A02` remains unsure because its combined score is `0.478`, below the AI threshold of `0.70`; the model and style signals did not make plain AI text stand out. `A03` reaches human after the threshold change because its combined score `0.4194` is below the raised human threshold. `A04` is also labeled human (`0.1524`): the punctuation-heavy formatting lowers the style-based score, and the weighted combination follows it. The whitespace input `A05` is labeled AI (`0.876`), so that evasion did not succeed.

Next I would validate and calibrate a stronger signal against a larger, labeled set, then consider a semantic or provenance signal that is less sensitive to formatting. I stopped after the one threshold change because changing signals or weights as well would make the before/after comparison ambiguous.

**The trade I'd make if this ran for real:** I would prefer a false negative over a false positive and keep uncertain work out of punitive decisions. That lets some AI-written text through, but the writer bears the greater cost when a detector wrongly accuses them.


<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
