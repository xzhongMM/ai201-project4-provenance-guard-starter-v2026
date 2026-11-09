# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 12 attacks · 2026-11-08 23:38
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
| A01 | false_positive | flag-human | 200 | `32075f84-6b29-42e8-a6ca-0d614a4be62c` | unsure | 0.503 |  |
| A02 | plain_ai | flag-ai | 200 | `a28b1226-06b8-4ed3-b625-cb43146a1d3d` | unsure | 0.478 |  |
| A03 | prompt_injection | model-evasion | 200 | `2d372ea1-fde1-47e0-87c4-4d672418e70c` | human | 0.419 |  |
| A04 | style_evasion | shape-evasion | 200 | `b486adf6-18d8-4d9f-a522-2902500ba0ef` | human | 0.152 |  |
| A05 | whitespace_noise | shape-evasion | 200 | `47398966-f206-4d9b-b4f1-4882ceef2b42` | ai | 0.876 |  |
| F01 | flood_same_creator | rate-limit | 200 | `b2d4cd5b-9329-4714-b9be-a6f91952b41f` | human | 0.260 |  |
| F02 | flood_same_creator | rate-limit | 200 | `05969ea2-8629-48a0-a69c-76133b01b7ef` | human | 0.260 |  |
| F03 | flood_same_creator | rate-limit | 200 | `a26ffda5-b125-4c31-a18d-913336b54f76` | human | 0.260 |  |
| F04 | flood_same_creator | rate-limit | 200 | `b3e10751-994c-46a7-b4cc-085ff1a97c77` | human | 0.260 |  |
| F05 | flood_same_creator | rate-limit | 200 | `5566455d-af30-47ec-bab6-129033de48a8` | human | 0.260 |  |
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
  "content_id": "32075f84-6b29-42e8-a6ca-0d614a4be62c",
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
  "content_id": "a28b1226-06b8-4ed3-b625-cb43146a1d3d",
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
  "content_id": "2d372ea1-fde1-47e0-87c4-4d672418e70c",
  "creator_id": "attacker_A03",
  "guess": "human",
  "confidence": 0.4194,
  "model_score": 0.2908,
  "style_score": 0.6122,
  "label": "We think this was probably written by a person.",
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
  "content_id": "b486adf6-18d8-4d9f-a522-2902500ba0ef",
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
  "content_id": "47398966-f206-4d9b-b4f1-4882ceef2b42",
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
  "content_id": "b2d4cd5b-9329-4714-b9be-a6f91952b41f",
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
  "content_id": "05969ea2-8629-48a0-a69c-76133b01b7ef",
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
  "content_id": "a26ffda5-b125-4c31-a18d-913336b54f76",
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
  "content_id": "b3e10751-994c-46a7-b4cc-085ff1a97c77",
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
  "content_id": "5566455d-af30-47ec-bab6-129033de48a8",
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
