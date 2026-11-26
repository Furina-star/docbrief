"""Counts keywords locally with a simple bag-of-words model and ranks them by frequency."""

from collections import Counter
import re

TOP_N = 15
MIN_WORD_LENGTH = 3

STOPWORDS = frozenset(
    """
    a about above after again against all also am an and any are aren't as at be
    because been before being below between both but by can can't cannot could
    couldn't did didn't do does doesn't doing don't down during each either else
    etc even ever every few for from further get gets got had hadn't has hasn't
    have haven't having he he'd he'll he's her here here's hers herself him
    himself his how how's however i i'd i'll i'm i've if in into is isn't it it's
    its itself just let's like made make many may me might more most much must
    mustn't my myself neither no nor not now of off often on once one only or
    other others ought our ours ourselves out over own per rather really said
    same say says see seen shall shan't she she'd she'll she's should shouldn't
    since so some such than that that's the their theirs them themselves then
    there there's therefore these they they'd they'll they're they've thing
    things this those though through thus to too two under until up upon us use
    used uses using very via was wasn't way we we'd we'll we're we've well were
    weren't what what's when when's where where's whether which while who who's
    whom whose why why's will with within without won't would wouldn't yet you
    you'd you'll you're you've your yours yourself yourselves
    """.split()
)

_TOKEN_RE = re.compile(r"[a-z]+(?:['’-][a-z]+)*")


# Split text into lowercase word tokens, normalizing curly apostrophes and possessives.
def tokenize(text: str) -> list[str]:
    tokens = []
    for token in _TOKEN_RE.findall(text.lower()):
        token = token.replace("’", "'")
        if token.endswith("'s"):
            token = token[:-2]
        tokens.append(token)
    return tokens


# Build the bag of words: counts of every meaningful (non-stopword) token in the text.
def bag_of_words(text: str) -> Counter[str]:
    return Counter(
        token
        for token in tokenize(text)
        if len(token) >= MIN_WORD_LENGTH and token not in STOPWORDS
    )


# Return the top keywords as (rank, word, count) tuples, ties broken alphabetically.
def rank_keywords(bag: Counter[str], top_n: int = TOP_N) -> list[tuple[int, str, int]]:
    ordered = sorted(bag.items(), key=lambda item: (-item[1], item[0]))[:top_n]
    return [(rank, word, count) for rank, (word, count) in enumerate(ordered, start=1)]


# Render the keyword ranking as a Markdown section for display and .md export.
def keywords_markdown(text: str, top_n: int = TOP_N) -> str:
    bag = bag_of_words(text)
    if not bag:
        return ""
    total = sum(bag.values())
    lines = [
        "## Keyword Frequency",
        "",
        f"{len(bag):,} unique keywords · {total:,} counted (stopwords removed)",
        "",
        "| Rank | Keyword | Count | Share |",
        "|---:|:---|---:|---:|",
    ]
    for rank, word, count in rank_keywords(bag, top_n):
        lines.append(f"| {rank} | {word} | {count:,} | {count / total:.1%} |")
    return "\n".join(lines)


# Format the full bag of words as plain text lines, most frequent first.
def bag_of_words_text(text: str) -> str:
    bag = bag_of_words(text)
    return "\n".join(f"{word}: {count}" for _, word, count in rank_keywords(bag, len(bag)))
