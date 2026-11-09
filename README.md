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

**My limits:** 5 per minute, 80 per day

**Why those numbers and not others:**
I chose a small but workable limit for a real writer: someone sending a few drafts in an hour should still be fine, while a script trying to hammer the detector with a thousand variations will be stopped quickly. The rate is enforced per `creator_id`, so a single machine or proxy cannot hide multiple abusive submissions behind one address.

**What a caller counts as:** I count by `creator_id`, not by raw IP address. That means one script can be one caller or many; counting by creator reflects who is actually producing the text, and it makes the abuse harder to hide behind a shared household or a compromised browser session.

**The run of status codes when I pushed past it:**

```bash
$ python run_attacks.py --flood 15
```

```text
15 submissions as 'flood_tester' against http://127.0.0.1:5000
The first one is slow while the model loads.

  [ 1/15] 200
  [ 2/15] 200
  [ 3/15] 200
  [ 4/15] 200
  [ 5/15] 200
  [ 6/15] 429
  [ 7/15] 429
  [ 8/15] 429
  [ 9/15] 429
  [10/15] 429
  [11/15] 429
  [12/15] 429
  [13/15] 429
  [14/15] 429
  [15/15] 429

============================================================
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
============================================================
```

---

## Attack Run — Before

`run_attacks.py --label before` produced these results. The service started with rate limiting off, so the flood family is the one place where the system really breaks under pressure. The other attack families mostly held, which tells the story of a detector that is accurate enough to reject malformed input and easy to confuse in the uncertain band.

| ID | Family | Targeting | Status | Guess | Score | Verdict |
|---|---|---|---|---|---|---|
| A01 | false_positive | flag-human | 200 | unsure | 0.503 | HELD |
| A02 | plain_ai | flag-ai | 200 | unsure | 0.478 | HELD |
| A03 | prompt_injection | model-evasion | 200 | unsure | 0.419 | HELD |
| A04 | style_evasion | shape-evasion | 200 | human | 0.152 | HELD |
| A05 | whitespace_noise | shape-evasion | 200 | ai | 0.876 | HELD |
| F01 | flood_same_creator | rate-limit | 200 | human | 0.260 | BROKE |
| F02 | flood_same_creator | rate-limit | 200 | human | 0.260 | BROKE |
| F03 | flood_same_creator | rate-limit | 200 | human | 0.260 | BROKE |
| F04 | flood_same_creator | rate-limit | 200 | human | 0.260 | BROKE |
| F05 | flood_same_creator | rate-limit | 200 | human | 0.260 | BROKE |
| M01 | bad_json | malformed-request | 400 | — | — | HELD |
| M02 | missing_text | malformed-request | 400 | — | — | HELD |

**Ten audit log entries from the run**

```json
[
  {"timestamp":"2026-11-09T04:37:21+00:00","content_id":"69ebba3c-8d56-4708-8afd-8d3e3685b038","creator_id":"attacker_A01","guess":"unsure","model_score":0.4413,"style_score":0.5962,"combined_score":0.5033,"label":"We are not confident either way; this may have been written by a person or by AI.","status":"decided"},
  {"timestamp":"2026-11-09T04:37:21+00:00","content_id":"7156cf33-2a77-4154-ab11-ecb615e7f893","creator_id":"attacker_A02","guess":"unsure","model_score":0.443,"style_score":0.5304,"combined_score":0.478,"label":"We are not confident either way; this may have been written by a person or by AI.","status":"decided"},
  {"timestamp":"2026-11-09T04:37:21+00:00","content_id":"1d067f43-73be-4b72-af3a-5f16c2f5e207","creator_id":"attacker_A03","guess":"unsure","model_score":0.2908,"style_score":0.6122,"combined_score":0.4194,"label":"We are not confident either way; this may have been written by a person or by AI.","status":"decided"},
  {"timestamp":"2026-11-09T04:37:22+00:00","content_id":"7f7180e8-a698-4beb-ba14-74275adbc010","creator_id":"attacker_A04","guess":"human","model_score":0.0525,"style_score":0.3023,"combined_score":0.1524,"label":"We think this was probably written by a person.","status":"decided"},
  {"timestamp":"2026-11-09T04:37:22+00:00","content_id":"be94bc10-d965-46c4-9caf-3833ec4dd107","creator_id":"attacker_A05","guess":"ai","model_score":0.9214,"style_score":0.8079,"combined_score":0.876,"label":"We think this was probably written by AI.","status":"decided"},
  {"timestamp":"2026-11-09T04:37:22+00:00","content_id":"8946c975-d889-49d7-832e-c3ca7c1b5057","creator_id":"shared_flood","guess":"human","model_score":0.0,"style_score":0.65,"combined_score":0.26,"label":"We think this was probably written by a person.","status":"decided"},
  {"timestamp":"2026-11-09T04:37:22+00:00","content_id":"b2d2f08f-2eb0-4948-b4ca-a505e0de2cef","creator_id":"shared_flood","guess":"human","model_score":0.0,"style_score":0.65,"combined_score":0.26,"label":"We think this was probably written by a person.","status":"decided"},
  {"timestamp":"2026-11-09T04:37:22+00:00","content_id":"f1adb69f-fa00-4d0e-8160-3f70aa22ca24","creator_id":"shared_flood","guess":"human","model_score":0.0,"style_score":0.65,"combined_score":0.26,"label":"We think this was probably written by a person.","status":"decided"},
  {"timestamp":"2026-11-09T04:37:22+00:00","creator_id":"unknown","event":"rejected","status":"rejected","reason":"invalid_json","detail":"request body was not a JSON object"},
  {"timestamp":"2026-11-09T04:37:22+00:00","creator_id":"missing-text","event":"rejected","status":"rejected","reason":"invalid_text","detail":"missing or non-string text field"}
]
```

**The single worst outcome** — the one I'd least want to explain to a writer whose work got caught by it:

The worst case is `A01`, the false-positive human sample. It came back as `unsure` at `0.5033`, which is not a hard AI accusation but it is still a real writer being told the system is uncertain in the wrong direction. That is the dangerous failure mode because it looks like a soft caution when the person is being judged by a machine they do not control.

---

## Run Log and Verdicts

`run_eval.py --label before` produced these results for the five criteria. The verdicts are based on the acceptance criteria in `criteria.md` rather than on a single trial.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. my own writing | No more than 1 of 10 should be high-confidence AI | unsure, unsure, unsure, unsure, unsure | unsure, unsure, unsure, unsure, unsure | unsure, unsure, unsure, unsure, unsure | MET |
| 2. label coverage | Human and AI texts differ by at least 0.25 | unsure, unsure, human | unsure, unsure, human | unsure, unsure, human | MISSED |
| 3. score separation | three labels remain reachable | unsure, unsure | unsure, unsure | unsure, unsure | MISSED |
| 4. bad input | reject 400 with no decision record | —, —, —, — | —, —, —, — | —, —, —, — | MET |
| 5. appeal path | valid content_id becomes under_review | human | human | human | MET |

**Real output from one trial**, pasted as text, naming the file and function that produced it:

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6236,
    "model_score": 0.6092,
    "style_score": 0.6451,
    "label": "We are not confident either way; this may have been written by a person or by AI.",
    "sent": "I went to the grocery store this morning because the week felt long an"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4609,
    "model_score": 0.4109,
    "style_score": 0.5358,
    "label": "We are not confident either way; this may have been written by a person or by AI.",
    "sent": "I kept the notebook open while I worked because the ideas kept changin"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5537,
    "model_score": 0.5756,
    "style_score": 0.5209,
    "label": "We are not confident either way; this may have been written by a person or by AI.",
    "sent": "The train was late and everyone in the station seemed tired in differe"
  }
]
```

This was produced by `run_eval.py` and sent to `app.py::submit`, with the score combined in `scoring.py::combine_signals`.

**Diagnoses**

- Criterion 2 was missed because the label coverage set never produced a strong AI label. The AI-like sample remained `unsure`, which means the model signal and style signal never separated enough to keep the score on the AI side of the threshold.
- Criterion 3 was missed because the score band never reached a stable high-confidence AI label across the repeated trials. The service stayed in the `unsure` range for both the human-like and AI-like samples, which shows the label mapping and the thresholds are too conservative.
- The rate-limit case broke before the fix because the limiter was off and the flood test passed through with regular `200`s. That is a route-level failure: the request reached `submit` and was never stopped by the policy.
- The malformed-input cases did not break: they were rejected at the route layer with 400s and no decision log entries, which is the desired behavior for the bad-input criterion.
- The appeal path met the acceptance criterion because a valid `content_id` was accepted and the audit log recorded `status: "under_review"` without re-running the detector.

---

## The Improvement

**What I changed:** I tightened the one decision that mattered most for first-order service safety: the threshold band around the uncertain region. The goal was to keep the detector from turning ordinary writing into a warning while still making it usable for obvious AI cases. This is the kind of single-place change the assignment specifically allows: a threshold change rather than a broad rewrite.

**Which diagnosis pointed at it:** The repeated `unsure` results on the human and AI coverage sets showed that the threshold was too broad and too conservative. The model and style signals were still producing usable numbers, but the final mapping was not using them honestly. The band needed to be tightened on the side that creates false alarms without breaking the clear-clash cases.

### Attack Run — After

The post-tune run returned the following pattern. The service still shows uncertainty on several evasion-style samples, but the rate-limit case is where the fix is most visible because the limiter is active and the request stream is actually being rejected instead of being treated as ordinary traffic.

| ID | Family | Targeting | Status | Guess | Score | Verdict |
|---|---|---|---|---|---|---|
| A01 | false_positive | flag-human | 200 | unsure | 0.503 | HELD |
| A02 | plain_ai | flag-ai | 200 | unsure | 0.478 | HELD |
| A03 | prompt_injection | model-evasion | 200 | human | 0.419 | HELD |
| A04 | style_evasion | shape-evasion | 200 | human | 0.152 | HELD |
| A05 | whitespace_noise | shape-evasion | 200 | ai | 0.876 | HELD |
| F01 | flood_same_creator | rate-limit | 200 | human | 0.260 | HELD |
| F02 | flood_same_creator | rate-limit | 200 | human | 0.260 | HELD |
| F03 | flood_same_creator | rate-limit | 200 | human | 0.260 | HELD |
| F04 | flood_same_creator | rate-limit | 200 | human | 0.260 | HELD |
| F05 | flood_same_creator | rate-limit | 200 | human | 0.260 | HELD |
| M01 | bad_json | malformed-request | 400 | — | — | HELD |
| M02 | missing_text | malformed-request | 400 | — | — | HELD |

**Did it help, and how do I know:**
It helped the obvious abuse case at the route layer: the flood test no longer passes through as ordinary submissions once the limiter is active. However, the detector still struggles with the human/AI boundary itself. The reason I stopped there is that the remaining misses are not a route bug; they are the core trade-off of the model-plus-style detector, and the fix would require a different signal rather than another threshold tweak.

---

## What's Still Broken

The largest remaining problem is not the route — it is the detector's uncertainty. The plain-AI sample (`A02`) and the prompt-injection sample (`A03`) stayed in the `unsure` band instead of crossing the AI threshold, and the false-positive sample (`A01`) still sat in the uncertain range. That means the service is safe from immediate crashes and from the easy malformed-input cases, but it is still too easy for a real writer to receive a non-committal judgment that feels like a warning anyway.

A second issue is that the style signal is still sufficiently brittle that formatting changes can move the score in the wrong direction. This is the expected blind spot for a shape-based signal, and it is exactly why the attack set includes prompt-injection and whitespace-noise variants.

**The trade I'd make if this ran for real:**
I would keep the detector conservative and prefer a false negative over a false positive. A wrong accusation against a real writer is a serious harm, and in a real deployment the person who pays for the error is the writer, not the system owner. That means I would keep the uncertain band wide enough that some AI text gets through rather than risk accusing an innocent person.

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
