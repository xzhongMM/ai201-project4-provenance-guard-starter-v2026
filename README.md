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
| high-confidence human | 0.00 – 0.35 | We think this was probably written by a person. |
| unsure | 0.35 – 0.65 | We are not confident either way; this may have been written by a person or by AI. |
| high-confidence AI | 0.65 – 1.00 | We think this was probably written by AI. |

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

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



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
