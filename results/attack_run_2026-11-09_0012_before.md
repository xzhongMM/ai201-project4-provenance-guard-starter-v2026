# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 12 attacks · 2026-11-09 00:12
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **12**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| A01 | false_positive | flag-human | 200 | `8b13cb6f-b639-4d1d-bd28-6f789c91be06` | unsure | 0.503 |  |
| A02 | plain_ai | flag-ai | 200 | `9fcb9eaf-9988-49eb-a713-8f2970ec6149` | unsure | 0.478 |  |
| A03 | prompt_injection | model-evasion | 200 | `51567c88-4fca-442c-ac16-4420a7462bd9` | unsure | 0.419 |  |
| A04 | style_evasion | shape-evasion | 200 | `26dde914-67be-409e-ab3b-9eaf93cb8918` | human | 0.152 |  |
| A05 | whitespace_noise | shape-evasion | 200 | `28e64ab4-97e7-4a30-88d0-3cc30a2a6d04` | ai | 0.876 |  |
| F01 | flood_same_creator | rate-limit | 200 | `d02bb2eb-a7c4-4cb0-90d0-e65816066283` | human | 0.260 |  |
| F02 | flood_same_creator | rate-limit | 200 | `17f884eb-1cc8-4901-a5b0-64de5227753f` | human | 0.260 |  |
| F03 | flood_same_creator | rate-limit | 200 | `c7e0281b-b0cc-4979-bf9b-ed4b490e6ca8` | human | 0.260 |  |
| F04 | flood_same_creator | rate-limit | 200 | `f874421b-71ec-470e-8c4e-5506979714b7` | human | 0.260 |  |
| F05 | flood_same_creator | rate-limit | 200 | `d8f2098f-0d65-4ef5-9418-6d7255935802` | human | 0.260 |  |
| M01 | bad_json | malformed-request | 400 | `—` | — | — |  |
| M02 | missing_text | malformed-request | 400 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `bad_json` | 1 | 0 | 1 |
| `false_positive` | 1 | 0 | 1 |
| `flood_same_creator` | 5 | 0 | 5 |
| `missing_text` | 1 | 0 | 1 |
| `plain_ai` | 1 | 0 | 1 |
| `prompt_injection` | 1 | 0 | 1 |
| `style_evasion` | 1 | 0 | 1 |
| `whitespace_noise` | 1 | 0 | 1 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### A01 — `false_positive`

*Targeting:* flag-human

```json
{
  "id": "A01",
  "status": 200,
  "content_id": "8b13cb6f-b639-4d1d-bd28-6f789c91be06",
  "creator_id": "attacker_A01",
  "guess": "unsure",
  "confidence": 0.5033,
  "model_score": 0.4413,
  "style_score": 0.5962,
  "label": "We are not confident either way; this may have been written by a person or by AI.",
  "error": null,
  "verdict": ""
}
```

### A02 — `plain_ai`

*Targeting:* flag-ai

```json
{
  "id": "A02",
  "status": 200,
  "content_id": "9fcb9eaf-9988-49eb-a713-8f2970ec6149",
  "creator_id": "attacker_A02",
  "guess": "unsure",
  "confidence": 0.478,
  "model_score": 0.443,
  "style_score": 0.5304,
  "label": "We are not confident either way; this may have been written by a person or by AI.",
  "error": null,
  "verdict": ""
}
```

### A03 — `prompt_injection`

*Targeting:* model-evasion

```json
{
  "id": "A03",
  "status": 200,
  "content_id": "51567c88-4fca-442c-ac16-4420a7462bd9",
  "creator_id": "attacker_A03",
  "guess": "unsure",
  "confidence": 0.4194,
  "model_score": 0.2908,
  "style_score": 0.6122,
  "label": "We are not confident either way; this may have been written by a person or by AI.",
  "error": null,
  "verdict": ""
}
```

### A04 — `style_evasion`

*Targeting:* shape-evasion

```json
{
  "id": "A04",
  "status": 200,
  "content_id": "26dde914-67be-409e-ab3b-9eaf93cb8918",
  "creator_id": "attacker_A04",
  "guess": "human",
  "confidence": 0.1524,
  "model_score": 0.0525,
  "style_score": 0.3023,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### A05 — `whitespace_noise`

*Targeting:* shape-evasion

```json
{
  "id": "A05",
  "status": 200,
  "content_id": "28e64ab4-97e7-4a30-88d0-3cc30a2a6d04",
  "creator_id": "attacker_A05",
  "guess": "ai",
  "confidence": 0.876,
  "model_score": 0.9214,
  "style_score": 0.8079,
  "label": "We think this was probably written by AI.",
  "error": null,
  "verdict": ""
}
```

### F01 — `flood_same_creator`

*Targeting:* rate-limit

```json
{
  "id": "F01",
  "status": 200,
  "content_id": "d02bb2eb-a7c4-4cb0-90d0-e65816066283",
  "creator_id": "shared_flood",
  "guess": "human",
  "confidence": 0.26,
  "model_score": 0.0,
  "style_score": 0.65,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### F02 — `flood_same_creator`

*Targeting:* rate-limit

```json
{
  "id": "F02",
  "status": 200,
  "content_id": "17f884eb-1cc8-4901-a5b0-64de5227753f",
  "creator_id": "shared_flood",
  "guess": "human",
  "confidence": 0.26,
  "model_score": 0.0,
  "style_score": 0.65,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### F03 — `flood_same_creator`

*Targeting:* rate-limit

```json
{
  "id": "F03",
  "status": 200,
  "content_id": "c7e0281b-b0cc-4979-bf9b-ed4b490e6ca8",
  "creator_id": "shared_flood",
  "guess": "human",
  "confidence": 0.26,
  "model_score": 0.0,
  "style_score": 0.65,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### F04 — `flood_same_creator`

*Targeting:* rate-limit

```json
{
  "id": "F04",
  "status": 200,
  "content_id": "f874421b-71ec-470e-8c4e-5506979714b7",
  "creator_id": "shared_flood",
  "guess": "human",
  "confidence": 0.26,
  "model_score": 0.0,
  "style_score": 0.65,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### F05 — `flood_same_creator`

*Targeting:* rate-limit

```json
{
  "id": "F05",
  "status": 200,
  "content_id": "d8f2098f-0d65-4ef5-9418-6d7255935802",
  "creator_id": "shared_flood",
  "guess": "human",
  "confidence": 0.26,
  "model_score": 0.0,
  "style_score": 0.65,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### M01 — `bad_json`

*Targeting:* malformed-request

```json
{
  "id": "M01",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### M02 — `missing_text`

*Targeting:* malformed-request

```json
{
  "id": "M02",
  "status": 400,
  "content_id": null,
  "creator_id": "missing-text",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
