"""Unit tests for local keyword counting, ranking, and bag-of-words output."""

import math

import pytest

from keywords import (
    bag_of_words,
    bag_of_words_text,
    keywords_markdown,
    rank_keywords,
    split_passages,
    tfidf_markdown,
    tfidf_scores,
    tokenize,
)


# Verify tokens are lowercased and possessives / curly apostrophes are normalized.
def test_tokenize_lowercases_and_strips_possessives():
    assert tokenize("Model's output, the MODEL’s Self-Attention!") == [
        "model",
        "output",
        "the",
        "model",
        "self-attention",
    ]


# Verify stopwords, numbers, and very short tokens are excluded from the bag.
def test_bag_of_words_drops_stopwords_numbers_and_short_tokens():
    bag = bag_of_words("The model and the data, 2024, AI ok. Data data model.")

    assert bag == {"model": 2, "data": 3}


# Verify ranking sorts by count descending, then alphabetically on ties.
def test_rank_keywords_orders_by_count_then_alphabetically():
    bag = bag_of_words("beta alpha gamma gamma beta gamma delta")

    assert rank_keywords(bag) == [(1, "gamma", 3), (2, "beta", 2), (3, "alpha", 1), (4, "delta", 1)]
    assert rank_keywords(bag, top_n=1) == [(1, "gamma", 3)]


# Verify the Markdown section contains a heading, totals, and ranked rows.
def test_keywords_markdown_renders_ranked_table():
    md = keywords_markdown("attention attention attention token token vector")

    assert md.startswith("## Keyword Frequency")
    assert "3 unique keywords · 6 counted" in md
    assert "| 1 | attention | 3 | 50.0% |" in md
    assert "| 2 | token | 2 | 33.3% |" in md
    assert "| 3 | vector | 1 | 16.7% |" in md


# Verify text with no meaningful words yields no section.
def test_keywords_markdown_empty_when_only_stopwords():
    assert keywords_markdown("the and of to 123") == ""


# Verify the full bag of words lists every term, most frequent first.
def test_bag_of_words_text_lists_all_terms():
    assert bag_of_words_text("zeta alpha zeta") == "zeta: 2\nalpha: 1"


# Verify paragraphs are used as passages, falling back to sentences when too few.
def test_split_passages_paragraphs_then_sentences():
    assert split_passages("One.\n\nTwo.\n\nThree.") == ["One.", "Two.", "Three."]
    assert split_passages("First idea. Second idea! Third?") == [
        "First idea.",
        "Second idea!",
        "Third?",
    ]


# Verify a word concentrated in one passage outranks an equally frequent word spread everywhere.
def test_tfidf_favors_concentrated_terms():
    text = "gradient gradient alpha\n\nmodel beta\n\nmodel gamma"
    scores = tfidf_scores(text)

    assert scores["gradient"] > scores["model"]
    assert scores["gradient"] == pytest.approx(2 / 7 * (math.log(4 / 2) + 1))
    assert scores["model"] == pytest.approx(2 / 7 * (math.log(4 / 3) + 1))


# Verify the TF-IDF Markdown section renders a ranked table with scores and counts.
def test_tfidf_markdown_renders_ranked_table():
    md = tfidf_markdown("gradient gradient alpha\n\nmodel beta\n\nmodel gamma")

    assert md.startswith("## TF-IDF Keywords")
    assert "Scored across 3 passages" in md
    assert "| 1 | gradient | 0.4838 | 2 |" in md
    assert "| 2 | model | 0.3679 | 2 |" in md


# Verify text with no meaningful words yields no TF-IDF section.
def test_tfidf_markdown_empty_when_only_stopwords():
    assert tfidf_markdown("the and of to") == ""
