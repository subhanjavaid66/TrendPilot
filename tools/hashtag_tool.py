
import re


PLATFORM_LIMITS = {
    "Instagram": 6,
    "Facebook": 3,
    "LinkedIn": 4,
    "X (Twitter)": 2,
    "YouTube Shorts": 5,
    "TikTok": 5,
}

STOP_WORDS = {
    "a", "about", "and", "are", "as", "at", "be", "before", "behind",
    "biggest", "by", "can", "do", "for", "from", "how", "i", "in",
    "is", "it", "make", "me", "of", "on", "or", "the", "this", "to",
    "vs", "what", "when", "with", "wish", "you",
}

# Related concepts for common topics.
# These are suggestions, not claims about popularity.
TOPIC_RULES = [
    {
        "keywords": {"startup", "startups"},
        "hashtags": [
            "StartupGrowth",
            "StartupCompetition",
            "Entrepreneurship",
            "BusinessStrategy",
            "StartupFounders",
            "Innovation",
            "CompetitiveAdvantage",
        ],
    },
    {
        "keywords": {"internship", "internships"},
        "hashtags": [
            "StudentInternships",
            "CareerDevelopment",
            "ProfessionalGrowth",
            "WorkExperience",
            "CareerReadiness",
            "InternshipExperience",
            "SkillDevelopment",
        ],
    },
    {
        "keywords": {"student", "students"},
        "hashtags": [
            "StudentSuccess",
            "StudentDevelopment",
            "FutureProfessionals",
        ],
    },
    {
        "keywords": {"electric", "ev", "vehicle", "vehicles"},
        "hashtags": [
            "ElectricVehicles",
            "ElectricCars",
            "EVTechnology",
            "SustainableTransport",
            "AutomotiveTechnology",
        ],
    },
    {
        "keywords": {"petrol", "gasoline"},
        "hashtags": [
            "PetrolCars",
            "EVvsPetrol",
            "AutomotiveIndustry",
        ],
    },
    {
        "keywords": {"education", "learning"},
        "hashtags": [
            "Education",
            "FutureOfLearning",
            "DigitalEducation",
            "LearningAndDevelopment",
        ],
    },
    {
        "keywords": {"artificial", "intelligence", "ai"},
        "hashtags": [
            "ArtificialIntelligence",
            "AIInnovation",
            "MachineLearning",
            "FutureOfAI",
        ],
    },
    {
        "keywords": {"cybersecurity", "cyber", "security"},
        "hashtags": [
            "Cybersecurity",
            "DataProtection",
            "InformationSecurity",
            "DigitalSafety",
        ],
    },
]

# Platform-specific selection preferences.
PLATFORM_PREFERENCES = {
    "Instagram": ["audience", "topic", "industry", "trend"],
    "Facebook": ["topic", "audience", "industry", "trend"],
    "LinkedIn": ["industry", "topic", "audience", "trend"],
    "X (Twitter)": ["topic", "industry", "trend", "audience"],
    "YouTube Shorts": ["topic", "industry", "audience", "trend"],
    "TikTok": ["topic", "audience", "trend", "industry"],
}


def _words(text):
    """Extract normalized words from text."""
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def _clean(tag):
    """Convert a phrase into a valid hashtag."""
    if not isinstance(tag, str):
        return None

    words = re.findall(r"[a-zA-Z0-9]+", tag)

    if not words:
        return None

    # Remove filler words from the beginning and end.
    while words and words[0].lower() in STOP_WORDS:
        words.pop(0)

    while words and words[-1].lower() in STOP_WORDS:
        words.pop()

    if not words:
        return None

    hashtag = "#" + "".join(
        word[0].upper() + word[1:] for word in words
    )

    # Avoid extremely short or long hashtags.
    if len(hashtag) < 4 or len(hashtag) > 30:
        return None

    # Avoid hashtags made entirely from numbers.
    if not any(char.isalpha() for char in hashtag):
        return None

    return hashtag


def _as_list(trends):
    """Normalize trend input into a list of strings."""
    if isinstance(trends, str):
        return [trends] if trends.strip() else []

    if isinstance(trends, (list, tuple)):
        return [
            item.strip()
            for item in trends
            if isinstance(item, str) and item.strip()
        ]

    return []


def _topic_candidates(topic):
    """Extract meaningful topic-specific hashtag candidates."""
    tokens = _words(topic)
    candidates = []

    # Keep the complete topic only when it is reasonably short.
    full_topic = _clean(topic)

    if full_topic:
        candidates.append(full_topic)

    # Add meaningful two-word phrases, excluding filler words.
    useful = [
        word for word in tokens
        if word not in STOP_WORDS
    ]

    for index in range(len(useful) - 1):
        first = useful[index]
        second = useful[index + 1]

        phrase = f"{first} {second}"

        # Avoid generic combinations and fragments.
        if len(first) >= 3 and len(second) >= 3:
            candidates.append(phrase)

    return candidates


def _related_candidates(topic):
    """Find industry and audience concepts related to the topic."""
    topic_tokens = set(_words(topic))
    candidates = []

    for rule in TOPIC_RULES:
        if topic_tokens.intersection(rule["keywords"]):
            candidates.extend(rule["hashtags"])

    return candidates


def _trend_candidates(topic, trends):
    """Extract trend hashtags only when the trend relates to the topic."""
    topic_tokens = set(_words(topic))
    candidates = []

    for trend in _as_list(trends):
        trend_tokens = set(_words(trend))

        # Ignore trends with no shared topic keywords.
        if not topic_tokens.intersection(trend_tokens):
            continue

        useful_words = [
            word for word in _words(trend)
            if word not in STOP_WORDS and len(word) >= 3
        ]

        if len(useful_words) >= 2:
            candidates.append(" ".join(useful_words[:3]))

    return candidates


def generate_hashtags(topic, trends=None, platform="Instagram"):
    """
    Generate relevant, diverse and platform-specific hashtags.

    Preserves the original function signature and return structure.
    """

    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Topic cannot be empty.")

    topic = topic.strip()

    limit = PLATFORM_LIMITS.get(platform, 5)

    # Build separate candidate groups.
    topic_candidates = _topic_candidates(topic)
    related_candidates = _related_candidates(topic)
    trend_candidates = _trend_candidates(topic, trends)

    candidates = {
        "topic": topic_candidates,
        "industry": related_candidates,
        "audience": [],
        "trend": trend_candidates,
    }

    # Identify audience-related concepts.
    topic_tokens = set(_words(topic))

    if topic_tokens.intersection({"student", "students"}):
        candidates["audience"].extend([
            "StudentLife",
            "FutureProfessionals",
            "StudentSuccess",
        ])

    if topic_tokens.intersection({"startup", "startups", "founder", "founders"}):
        candidates["audience"].extend([
            "StartupFounders",
            "Entrepreneurs",
        ])

    if topic_tokens.intersection({"career", "internship", "internships"}):
        candidates["audience"].extend([
            "CareerGrowth",
            "YoungProfessionals",
        ])

    # Arrange categories according to platform.
    preferences = PLATFORM_PREFERENCES.get(
        platform,
        ["topic", "industry", "audience", "trend"]
    )

    hashtags = []
    seen = set()

    for category in preferences:
        for candidate in candidates.get(category, []):
            tag = _clean(candidate)

            if not tag:
                continue

            normalized = tag.lower()

            if normalized in seen:
                continue

            seen.add(normalized)
            hashtags.append(tag)

            if len(hashtags) >= limit:
                break

        if len(hashtags) >= limit:
            break

    return {
        "topic": topic,
        "platform": platform,
        "hashtags": hashtags,
        "total_hashtags": len(hashtags),
    }

