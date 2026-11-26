
import re


# ==================================================
# 1. TEXT PROCESSING HELPERS
# ==================================================

def _stem(word):
    """Apply light stemming to match related word forms."""

    for suffix in ("ing", "ed", "es", "s", "e"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[:-len(suffix)]

    return word


def _stems(text):
    """Extract simplified word stems."""

    return {
        _stem(word)
        for word in re.findall(r"[a-z0-9]+", text.lower())
        if len(word) > 2
    }


def _split_hashtag(hashtag):
    """Split CamelCase hashtags into meaningful words."""

    hashtag = hashtag.lstrip("#")

    # Handle AI-prefixed hashtags such as AIpedagogy.
    if hashtag.lower().startswith("ai") and len(hashtag) > 2:
        hashtag = "AI " + hashtag[2:]

    # Split lowercase-to-uppercase transitions.
    hashtag = re.sub(
        r"([a-z])([A-Z])",
        r"\1 \2",
        hashtag,
    )

    # Split acronym-to-word transitions.
    hashtag = re.sub(
        r"([A-Z]+)([A-Z][a-z])",
        r"\1 \2",
        hashtag,
    )

    return hashtag

# ==================================================
# 2. REGEX PATTERNS
# ==================================================


CTA_PATTERN = re.compile(
    r"\b(?:"
    # Direct engagement
    r"comment|tag|share|follow|subscribe|"
    r"save this|drop a|"
    
    # Asking for opinions
    r"let us know|let me know|tell us|tell me|"
    r"show us|share your|"
    r"what's your|what is your|"
    r"what do you think|what are your thoughts|"
    r"how do you think|"
    r"would you|which one|"
    r"do you agree|"
    
    # Broader engagement questions
    r"what questions should we|"
    r"what should we|"
    r"how can we|"
    r"how should we|"
    r"what would you|"
    r"how would you|"
    r"have you ever|"
    r"have you tried|"
    r"what role do you|"
    r"what do you|"
    r"what are your|"
    
    # Discussion and action
    r"let's discuss|lets discuss|"
    r"let's talk|lets talk|"
    r"join|explore how|learn more|get started|"
    r"try it|link in bio"
    r")\b",
    re.IGNORECASE,
)


HASHTAG_PATTERN = re.compile(
    r"(?<!\w)#[A-Za-z0-9_]+"
)

PLACEHOLDER_PATTERN = re.compile(
    r"\[[^\]]{1,100}\]"
    r"|<[^>]{1,100}>"
    r"|\b(?:insert|replace with|add|mention)"
    r"\s+(?:your|a|the)\s+"
    r"(?:example|topic|text|name|concept|detail)\b",
    re.IGNORECASE,
)


# ==================================================
# 3. TOPIC ALIASES
# ==================================================

AI_EDUCATION_ALIASES = [
    "ai",
    "artificial intelligence",
    "education",
    "educational",
    "edtech",
    "learning",
    "analytics",
    "teaching",
    "teacher",
    "teachers",
    "pedagogy",
    "classroom",
    "student",
    "students",
]


TOPIC_ALIASES = {
    "artificial intelligence": ["ai"],
    "machine learning": ["ml"],
    "natural language processing": ["nlp"],
    "large language models": ["llm", "llms"],
    "ai education": AI_EDUCATION_ALIASES,
    "ai in education": AI_EDUCATION_ALIASES,
}


# ==================================================
# 4. TOPIC RELEVANCE
# ==================================================

def _check_topic_relevance(topic, content):
    """Check whether the caption discusses the requested topic."""

    topic_lower = topic.lower().strip()
    content_lower = content.lower()

    topic_words = _stems(topic_lower)
    content_words = _stems(content_lower)

    if not topic_words:
        return 0, "Include the main topic more clearly."

    if topic_lower in content_lower:
        return 25, None

    aliases = TOPIC_ALIASES.get(topic_lower, [])

    for alias in aliases:
        if re.search(
            rf"\b{re.escape(alias)}\b",
            content_lower,
        ):
            return 25, None

    matched_words = topic_words & content_words

    match_ratio = len(matched_words) / len(topic_words)

    if match_ratio >= 0.75:
        return 25, None

    if match_ratio >= 0.5:
        return 20, (
            "Make the connection to the requested topic clearer."
        )

    if match_ratio > 0:
        return 12, (
            "Mention more important words from the requested topic."
        )

    return 0, (
        "Include the main topic naturally in the caption body."
    )


# ==================================================
# 5. HASHTAG RELEVANCE
# ==================================================

def _check_hashtag_relevance(topic, hashtags):
    """Check hashtag relevance using topic keywords and aliases."""

    topic_lower = topic.lower().strip()

    topic_words = set(
        re.findall(r"[a-z0-9]+", topic_lower)
    )

    aliases = TOPIC_ALIASES.get(topic_lower, [])

    for alias in aliases:
        topic_words.update(
            re.findall(r"[a-z0-9]+", alias.lower())
        )

    relevant_count = 0

    for hashtag in hashtags:

        split_text = _split_hashtag(hashtag)

        hashtag_words = set(
            re.findall(r"[a-z0-9]+", split_text.lower())
        )

        if topic_words.intersection(hashtag_words):
            relevant_count += 1

    return relevant_count


# ==================================================
# 6. FORMATTING CHECKS
# ==================================================

def _check_formatting(content):
    """Detect common formatting problems."""

    issues = []

    # Missing spaces after punctuation.
    if re.search(r"[.!?][A-Za-z]", content):
        issues.append(
            "Add missing spaces after sentence-ending punctuation."
        )

    # Common accidentally joined words.
    if re.search(
        r"\b(?:with|and|the|to|of|for|what|they|can|will|"
        r"your|their|our|is|are|in|on|at|from|by)"
        r"[A-Z][a-z]{2,}\b",
        content,
    ):
        issues.append(
            "Check for accidentally joined words."
        )

    # Missing spaces between lowercase and uppercase words.
    if re.search(r"[a-z][A-Z][a-z]", content):
        issues.append(
            "Check for missing spaces between words."
        )

    # Spaces before punctuation.
    if re.search(r"\s+[,.;!?]", content):
        issues.append(
            "Remove unnecessary spaces before punctuation."
        )

    # Repeated spaces.
    if re.search(r" {2,}", content):
        issues.append(
            "Remove unnecessary repeated spaces."
        )

    # Excessive blank lines.
    if re.search(r"\n{4,}", content):
        issues.append(
            "Reduce excessive blank lines."
        )

    # Unfinished placeholders.
    if PLACEHOLDER_PATTERN.search(content):
        issues.append(
            "Remove unfinished placeholders and write complete text."
        )

    return list(dict.fromkeys(issues))


# ==================================================
# 7. MAIN CONTENT ANALYZER
# ==================================================

def analyze_content(
    content,
    topic,
    hashtags=None,
    platform="Instagram",
):
    """
    Analyze social media content using rule-based checks.

    Maximum score: 100.

    Categories:
        Relevance: 25
        Length: 20
        Hashtags: 15
        CTA: 10
        Readability: 15
        Originality: 15
    """

    if not isinstance(content, str) or not content.strip():
        raise ValueError("Content cannot be empty.")

    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Topic cannot be empty.")

    # ==================================================
    # PLATFORM RULES
    # ==================================================

    platform_rules = {
        "Instagram": {
            "min_words": 30,
            "max_words": 150,
            "min_hashtags": 3,
            "max_hashtags": 8,
        },
        "Facebook": {
            "min_words": 30,
            "max_words": 200,
            "min_hashtags": 1,
            "max_hashtags": 3,
        },
        "LinkedIn": {
            "min_words": 50,
            "max_words": 250,
            "min_hashtags": 3,
            "max_hashtags": 5,
        },
        "X (Twitter)": {
            "min_words": 10,
            "max_words": 50,
            "min_hashtags": 1,
            "max_hashtags": 2,
        },
        "TikTok": {
            "min_words": 5,
            "max_words": 60,
            "min_hashtags": 3,
            "max_hashtags": 5,
        },
        "YouTube Shorts": {
            "min_words": 10,
            "max_words": 80,
            "min_hashtags": 3,
            "max_hashtags": 5,
        },
    }

    rules = platform_rules.get(
        platform,
        platform_rules["Instagram"],
    )

    suggestions = []

    # ==================================================
    # REMOVE HASHTAGS BEFORE TEXT ANALYSIS
    # ==================================================

    text_without_tags = HASHTAG_PATTERN.sub(
        "",
        content,
    ).strip()

    words = re.findall(
        r"\b[\w'-]+\b",
        text_without_tags,
    )

    word_count = len(words)

    # ==================================================
    # 1. TOPIC RELEVANCE: 25 POINTS
    # ==================================================

    relevance_score, relevance_suggestion = (
        _check_topic_relevance(
            topic,
            text_without_tags,
        )
    )

    if relevance_suggestion:
        suggestions.append(relevance_suggestion)

    # ==================================================
    # 2. CONTENT LENGTH: 20 POINTS
    # ==================================================

    minimum = rules["min_words"]
    maximum = rules["max_words"]

    if minimum <= word_count <= maximum:
        length_score = 20

    elif word_count < minimum:

        length_score = (
            10 if word_count >= minimum * 0.5 else 0
        )

        suggestions.append(
            f"Increase content length to at least "
            f"{minimum} words for {platform}."
        )

    else:

        length_score = (
            0 if word_count > maximum * 2 else 10
        )

        suggestions.append(
            f"Reduce content length to around "
            f"{maximum} words for {platform}."
        )

    # ==================================================
    # 3. HASHTAGS: 15 POINTS
    # ==================================================

    embedded_hashtags = HASHTAG_PATTERN.findall(content)

    if hashtags is not None:

        if isinstance(hashtags, str):
            hashtag_source = hashtags

        else:
            hashtag_source = " ".join(
                str(tag) for tag in hashtags
            )

        content_hashtags = HASHTAG_PATTERN.findall(
            hashtag_source
        )

    else:
        content_hashtags = embedded_hashtags

    unique_hashtags = {}

    for tag in content_hashtags:
        unique_hashtags.setdefault(tag.lower(), tag)

    content_hashtags = list(unique_hashtags.values())

    hashtag_count = len(content_hashtags)

    inline_hashtag_count = len(embedded_hashtags)

    if (
        rules["min_hashtags"]
        <= hashtag_count
        <= rules["max_hashtags"]
    ):
        hashtag_points = 15

    elif hashtag_count == 0:
        hashtag_points = 0

        suggestions.append(
            "Add relevant hashtags to improve discoverability."
        )

    elif hashtag_count < rules["min_hashtags"]:
        hashtag_points = 8

        suggestions.append(
            f"Add more hashtags. Recommended minimum: "
            f"{rules['min_hashtags']}."
        )

    else:
        hashtag_points = 5

        suggestions.append(
            f"Reduce hashtags. Recommended maximum: "
            f"{rules['max_hashtags']}."
        )

    relevant_hashtags = _check_hashtag_relevance(
        topic,
        content_hashtags,
    )

    hashtag_relevance_ratio = (
        relevant_hashtags / hashtag_count
        if hashtag_count else 0
    )

    if hashtag_count and hashtag_relevance_ratio < 0.5:

        hashtag_points = max(
            0,
            hashtag_points - 5,
        )

        suggestions.append(
            "Use hashtags that are more closely related to the topic."
        )

    # ==================================================
    # 4. CALL TO ACTION: 10 POINTS
    # ==================================================

    if CTA_PATTERN.search(text_without_tags):
        cta_score = 10

    else:
        cta_score = 0

        suggestions.append(
            "Add a call to action to encourage engagement."
        )

    # ==================================================
    # 5. READABILITY AND FORMATTING: 15 POINTS
    # ==================================================

    sentences = [
        sentence.strip()
        for sentence in re.split(
            r"[.!?]+",
            text_without_tags,
        )
        if sentence.strip()
    ]

    if sentences:

        average_sentence_length = (
            word_count / len(sentences)
        )

        if average_sentence_length <= 25:
            readability_score = 15

        elif average_sentence_length <= 35:
            readability_score = 10

            suggestions.append(
                "Use shorter sentences to improve readability."
            )

        else:
            readability_score = 5

            suggestions.append(
                "Break long sentences into shorter sentences."
            )

    else:
        readability_score = 0

        suggestions.append(
            "Use complete sentences to improve readability."
        )

    formatting_issues = _check_formatting(text_without_tags)

    if formatting_issues:

        formatting_deduction = min(
            len(formatting_issues) * 3,
            9,
        )

        readability_score = max(
            0,
            readability_score - formatting_deduction,
        )

        suggestions.extend(formatting_issues)

    # ==================================================
    # 6. REPETITION AND ORIGINALITY: 15 POINTS
    # ==================================================

    words_lower = re.findall(
        r"\b[a-zA-Z]+\b",
        text_without_tags.lower(),
    )

    if words_lower:

        repetition_ratio = (
            len(set(words_lower)) / len(words_lower)
        )

        if word_count < 10:

            originality_score = 5

            suggestions.append(
                "Add more meaningful information to improve content depth."
            )

        elif repetition_ratio >= 0.65:
            originality_score = 15

        elif repetition_ratio >= 0.45:
            originality_score = 12

        elif repetition_ratio >= 0.30:

            originality_score = 8

            suggestions.append(
                "Avoid repeating the same words too frequently."
            )

        else:

            originality_score = 5

            suggestions.append(
                "Improve vocabulary variety and reduce repetition."
            )

    else:

        originality_score = 0
        repetition_ratio = 0

        suggestions.append(
            "Add meaningful text to your content."
        )

    # ==================================================
    # FINAL QUALITY SCORE
    # ==================================================

    quality_score = (
        relevance_score
        + length_score
        + hashtag_points
        + cta_score
        + readability_score
        + originality_score
    )

    suggestions = list(dict.fromkeys(suggestions))

    # ==================================================
    # RETURN ANALYSIS
    # ==================================================

    return {
        "platform": platform,
        "word_count": word_count,

        "hashtag_count": hashtag_count,
        "inline_hashtag_count": inline_hashtag_count,
        "total_hashtag_mentions": len(embedded_hashtags),
        "relevant_hashtag_count": relevant_hashtags,

        "relevance_score": relevance_score,

        "relevance_percent": round(
            relevance_score / 25 * 100
        ),

        "quality_score": quality_score,

        "checks": {
            "relevance": relevance_score,
            "length": length_score,
            "hashtags": hashtag_points,
            "call_to_action": cta_score,
            "readability": readability_score,
            "originality": originality_score,
        },

        "max_scores": {
            "relevance": 25,
            "length": 20,
            "hashtags": 15,
            "call_to_action": 10,
            "readability": 15,
            "originality": 15,
        },

        "formatting_issues": formatting_issues,

        "suggestions": suggestions,
    }
