"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        "texts": [
            "I went to the grocery store this morning because the week felt long and the air outside was warm enough to make the walk pleasant. I bought coffee, fruit, and a loaf of bread, and I stood in the aisle thinking about how small errands still change the rhythm of a day.",
            "I kept the notebook open while I worked because the ideas kept changing shape. A few sentences became a heading, then a paragraph, then a more serious version of the same thought, and the revision kept improving the way the argument felt.",
            "The train was late and everyone in the station seemed tired in different ways. I watched the platform fill and empty again while I waited, then I realized the delay had made the whole morning feel more human than it had any right to be.",
            "I made tea before I started writing because I wanted a quieter room and a slower beginning. The first draft was stiff, but the second one sounded like me again, and that matters more than any one sentence.",
            "The meeting ended with a vague sense of progress and a few clearer actions. I wrote them down before I forgot them, and the list was enough to turn an ordinary afternoon into something I could act on.",
            "I missed the first bus and waited beside the library until the next one came. The delay was annoying, but it gave me time to finish a chapter I had been carrying around all week.",
            "The kitchen was noisy while everyone made dinner, so I took my book to the back room. I read for twenty minutes, then came back when the food was ready and the conversation had settled down.",
            "I started the garden late this year and planted only a few things. The tomatoes are taking their time, but the herbs have already filled the small pots by the window.",
            "After work I walked the longer route home because the short one felt too crowded. I noticed a new mural on the brick wall and sent a picture to my sister when I got inside.",
            "My old notebook is full of lists that no longer matter. I kept it anyway, because a few pages still remind me what I was trying to figure out at the time.",
        ],
    },
    {
        "name": "label coverage",
        "criterion": 3,
        "texts": [
            "The system is designed to improve efficiency and reduce friction across the workflow. It manages the core tasks, supports consistent output, and helps maintain a clear operational process while preserving quality and reliability.",
            "I walked past the bakery on the corner and noticed the window was fogged up from the early heat. The pastries looked too fresh to resist, so I bought one and stood outside for a minute just to let the morning settle.",
            "This is a borderline paragraph that is ordinary enough to feel human but also structured enough to look polished. It sits in the middle of the range where the detector has to choose whether it trusts the rhythm more than the meaning.",
        ],
    },
    {
        "name": "score separation",
        "criterion": 2,
        "texts": [
            "The weekend was quiet and the streets felt slow in the best way. I walked home with my hands in my pockets and noticed the light had changed without me noticing it. The small shift in the afternoon made everything seem easier to understand.",
            "The framework is optimized for scalability, transparency, and operational continuity across multiple deployment scenarios. It synthesizes the most relevant signals into a consistent, adaptive model for reliable results and measurable performance improvements.",
        ],
    },
    {
        "name": "bad input",
        "criterion": 5,
        "bodies": [
            {"text": "", "creator_id": "eval_bad_empty"},
            {"creator_id": "eval_bad_missing"},
            {"text": "word " * 50000, "creator_id": "eval_bad_huge"},
            {"text": None, "creator_id": "eval_bad_null"},
        ],
    },
    {
        "name": "appeal path",
        "criterion": 4,
        "appeal": True,
        "appeal_reasoning": "This was my own writing; please review the decision.",
        "texts": [
            "A short writer-facing example for the appeal flow. This text is deliberately ordinary so the endpoint can be exercised without the score itself becoming the story.",
        ],
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
