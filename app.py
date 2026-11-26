
import streamlit as st
from pathlib import Path

from main import run_trendpilot
from memory.history import get_history


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="TrendPilot | AI Content Studio",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# CUSTOM DESIGN
# =====================================================

st.markdown("""
<style>

/* Overall application */
.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, rgba(91, 75, 220, 0.13), transparent 35%),
        radial-gradient(ellipse at 95% 10%, rgba(0, 190, 220, 0.08), transparent 30%),
        #0B1020;
}

.block-container {
    max-width: 1450px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #10172A;
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

/* Brand */
.brand {
    font-size: 29px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #FFFFFF;
}

.brand-icon {
    color: #A78BFA;
}

.brand-caption {
    color: #94A3B8;
    font-size: 13px;
    margin-top: 3px;
}

/* Hero section */
.hero {
    padding: 28px 30px;
    border-radius: 18px;
    background: linear-gradient(
        115deg,
        rgba(91, 75, 220, 0.24),
        rgba(20, 184, 166, 0.10),
        rgba(30, 41, 59, 0.35)
    );
    border: 1px solid rgba(167, 139, 250, 0.22);
    margin-bottom: 28px;
}

.hero-title {
    font-size: 36px;
    font-weight: 800;
    letter-spacing: -1.4px;
    color: #F8FAFC;
    margin-bottom: 7px;
}

.hero-description {
    color: #A5B4CC;
    font-size: 15px;
}

.hero-badge {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 30px;
    background: rgba(16, 185, 129, 0.13);
    border: 1px solid rgba(16, 185, 129, 0.25);
    color: #6EE7B7;
    font-size: 12px;
    font-weight: 700;
}

/* Section headings */
.section-heading {
    color: #F8FAFC;
    font-size: 23px;
    font-weight: 750;
    margin-bottom: 4px;
}

.section-description {
    color: #94A3B8;
    font-size: 14px;
    margin-bottom: 18px;
}

/* Panels */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(20, 29, 49, 0.72);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 16px;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        rgba(30, 41, 70, 0.95),
        rgba(19, 28, 48, 0.95)
    );
    border: 1px solid rgba(148, 163, 184, 0.16);
    padding: 18px 20px;
    border-radius: 14px;
}

div[data-testid="stMetricLabel"] {
    color: #A5B4CC;
}

div[data-testid="stMetricValue"] {
    color: #F8FAFC;
    font-weight: 750;
}

/* Inputs */
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #151F35;
    border-color: rgba(148, 163, 184, 0.22);
    border-radius: 10px;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    border-radius: 10px;
    min-height: 44px;
    font-weight: 700;
    transition: 0.2s ease;
}

.stFormSubmitButton > button {
    background: linear-gradient(90deg, #6D5DFB, #4776E6);
    border: none;
    color: white;
}

.stFormSubmitButton > button:hover {
    background: linear-gradient(90deg, #806FFF, #5687F5);
    border: none;
    color: white;
    transform: translateY(-1px);
}

/* Tabs */
button[data-baseweb="tab"] {
    font-weight: 650;
    color: #94A3B8;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #A78BFA;
}

/* Dividers */
hr {
    border-color: rgba(148, 163, 184, 0.14);
}

/* Small text */
.muted {
    color: #94A3B8;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# SESSION STATE
# =====================================================

if "latest_result" not in st.session_state:
    st.session_state["latest_result"] = None


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown(
        '<div class="brand"><span class="brand-icon">✦</span> TrendPilot</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="brand-caption">YOUR AI CONTENT CREATION STUDIO</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### Workspace")

    st.markdown("✦  Content Generator")
    st.markdown("◷  Generation History")

    st.divider()

    st.markdown("### About TrendPilot")

    st.caption(
        "Your AI-powered social media assistant. "
        "Research trends, generate engaging content, "
        "analyze quality and improve your strategy."
    )

    st.divider()

    st.markdown("### Recent Generations")

    try:
        history = get_history()

        if history:

            st.caption(
                f"{len(history)} saved generations"
            )

            for record in reversed(history[-8:]):

                topic_name = record.get(
                    "topic", "Untitled"
                )

                timestamp = record.get(
                    "timestamp", ""
                )

                with st.expander(
                    f"✦ {topic_name}"
                ):

                    st.caption(timestamp)

                    st.write(
                        record.get(
                            "content",
                            "No content available."
                        )
                    )

        else:
            st.info("Your history is currently empty.")

    except Exception as error:
        st.warning(f"History unavailable: {error}")

    st.divider()

    st.caption("TrendPilot AI · Content Studio")


# =====================================================
# HERO HEADER
# =====================================================

header_left, header_right = st.columns([4, 1])

with header_left:

    st.markdown("""
    <div class="hero">
        <div style="margin-bottom:14px;">
            <span class="hero-badge">✦ AI POWERED CONTENT STUDIO</span>
        </div>
        <div class="hero-title">
            Create Content That<br>Gets Attention.
        </div>
        <div class="hero-description">
            Discover trends, generate powerful content and build
            a stronger social media presence with AI.
        </div>
    </div>
    """, unsafe_allow_html=True)

with header_right:
    st.write("")
    st.write("")
    st.metric("AI Assistant", "Active", "Ready to create")


# =====================================================
# CONTENT GENERATION
# =====================================================

st.markdown(
    '<div class="section-heading">Create New Content</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Tell TrendPilot what you want to create. '
    'Choose your platform and preferred writing style.'
    '</div>',
    unsafe_allow_html=True
)

with st.container(border=True):

    st.markdown("#### 01 · Your Content Topic")

    with st.form("content_form"):

        topic = st.text_input(
            "What do you want to talk about?",
            placeholder="Example: Artificial Intelligence in Education"
        )

        st.write("")

        st.markdown("#### 02 · Customize Your Content")

        col1, col2, col3 = st.columns(3)

        with col1:

            platform = st.selectbox(
                "Social Media Platform",
                [
                    "Instagram",
                    "Facebook",
                    "LinkedIn",
                    "X (Twitter)",
                    "YouTube Shorts",
                    "TikTok"
                ]
            )

        with col2:

            tone = st.selectbox(
                "Writing Tone",
                [
                    "Professional",
                    "Funny",
                    "Motivational",
                    "Casual",
                    "Exciting"
                ]
            )

        with col3:

            output_type = st.selectbox(
                "Content Type",
                [
                    "Post",
                    "Post + Reel Script",
                    "Reel Script"
                ]
            )

        st.write("")

        generate_button = st.form_submit_button(
            "✦  Generate My Content",
            use_container_width=True,
            type="primary"
        )


# =====================================================
# GENERATION PROCESS
# =====================================================

if generate_button:

    if not topic.strip():

        st.warning(
            "Please enter a topic before generating content."
        )

    else:

        try:

            with st.spinner(
                "TrendPilot is researching, creating and reviewing your content..."
            ):

                results = run_trendpilot(
                    topic=topic.strip(),
                    platform=platform,
                    tone=tone,
                    output_type=output_type
                )

                st.session_state["latest_result"] = results

            st.success(
                "Your content has been generated successfully!"
            )

            st.rerun()

        except Exception as error:

            st.error(
                f"Something went wrong: {error}"
            )


# =====================================================
# GENERATED RESULTS
# =====================================================

results = st.session_state["latest_result"]

if results:

    st.divider()

    st.markdown(
        '<div class="section-heading">Your Content Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Your generated content and performance insights are ready.'
        '</div>',
        unsafe_allow_html=True
    )

    analysis = results.get("analysis", {})

    # -------------------------------
    # PERFORMANCE METRICS
    # -------------------------------

    st.markdown("#### Content Performance")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Quality Score",
        f"{analysis.get('quality_score', 0)}/100"
    )

    m2.metric(
        "Word Count",
        analysis.get("word_count", 0)
    )

    m3.metric(
        "Hashtags",
        analysis.get("hashtag_count", 0)
    )

    m4.metric(
    "Topic Relevance",
    f"{analysis.get('relevance_percent', 0)}%"
    )

    st.write("")

    # -------------------------------
    # RESULT TABS
    # -------------------------------

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "✦ Generated Content",
        "▤ Quality Analysis",
        "⌁ Trend Research",
        "# Hashtags",
        "✧ AI Review"
    ])

    # TAB 1: CONTENT

    with tab1:

        st.markdown("### Your Generated Post")

        content = results.get(
            "content",
            "No content available."
        )

        with st.container(border=True):
            st.markdown(content)

        st.download_button(
            "⬇ Download Content",
            data=content,
            file_name="trendpilot_content.txt",
            mime="text/plain",
            use_container_width=True
        )

    # TAB 2: ANALYSIS

    with tab2:

        st.markdown("### Quality Analysis")

        quality_score = analysis.get(
            "quality_score", 0
        )

        st.write("Overall Content Quality")

        st.progress(
            max(0, min(100, int(quality_score))) / 100
        )

        st.caption(
            f"Quality score: {quality_score}/100"
        )

        st.markdown("#### Analysis Details")

        st.write(
            f"**Topic Relevance:** "
            f"{analysis.get('relevance_score', 0)}"
        )

        suggestions = analysis.get("suggestions", [])

        if suggestions:

            st.markdown("#### Improvement Suggestions")

            for suggestion in suggestions:
                st.warning(suggestion)

        else:
            st.success("No improvement suggestions available.")

    # TAB 3: TREND RESEARCH

    with tab3:

        st.markdown("### Research Insights")

        research = results.get("research", {})

        trends = research.get("trends", [])

        if trends:

            for index, trend in enumerate(trends, start=1):

                with st.container(border=True):
                    st.markdown(f"**Trend {index}**")
                    st.write(trend)

        else:
            st.info("No trend research results available.")

    # TAB 4: HASHTAGS

    with tab4:

        st.markdown("### Your Hashtag Collection")

        hashtag_data = results.get("hashtags", {})

        hashtags = hashtag_data.get("hashtags", [])

        if hashtags:

            with st.container(border=True):
                st.markdown(" ".join(hashtags))

            st.download_button(
                "⬇ Download Hashtags",
                data=" ".join(hashtags),
                file_name="trendpilot_hashtags.txt",
                mime="text/plain",
                use_container_width=True
            )

        else:
            st.info("No hashtags available.")

    # TAB 5: AI REVIEW

    with tab5:

        st.markdown("### AI Content Review")

        review = results.get(
            "review",
            "No AI review available."
        )

        with st.container(border=True):
            st.markdown(review)

    # -------------------------------
    # ADDITIONAL OUTPUTS
    # -------------------------------

    reel_result = results.get("reel_script")

    if reel_result:

        st.divider()

        st.markdown("### Reel Script")

        if isinstance(reel_result, dict):
            reel_text = reel_result.get(
                "script", str(reel_result)
            )
        else:
            reel_text = str(reel_result)

        with st.container(border=True):
            st.markdown(reel_text)

        st.download_button(
            "⬇ Download Reel Script",
            data=reel_text,
            file_name="trendpilot_reel_script.txt",
            mime="text/plain"
        )

    st.divider()

    st.markdown("### Title & Thumbnail Ideas")

    title_col, thumbnail_col = st.columns(2)

    with title_col:
        st.markdown("#### Suggested Title")
        st.info(results.get("title", "No title available."))

    with thumbnail_col:
        st.markdown("#### Thumbnail Text")
        st.info(results.get("thumbnail_text", "No thumbnail text available."))

    st.divider()

    saved_file = results.get("saved_file")

    if saved_file:
        saved_path = Path(saved_file)

        if saved_path.is_file():
            st.download_button(
                "Save Full Result",
                data=saved_path.read_text(encoding="utf-8"),
                file_name=saved_path.name,
                mime="text/markdown",
                use_container_width=True,
            )
            st.caption(f"Project copy saved at: {saved_path}")
        else:
            st.error(f"Generated result file is missing: {saved_path}")

else:

    # -------------------------------
    # EMPTY STATE
    # -------------------------------

    st.write("")

    with st.container(border=True):

        st.markdown(
            """
            <div style="text-align:center; padding:35px 10px;">
                <div style="font-size:55px; margin-bottom:12px;">
                    ✦
                </div>
                <div style="
                    font-size:25px;
                    font-weight:750;
                    color:#F8FAFC;
                    margin-bottom:10px;
                ">
                    Your Next Big Idea Starts Here
                </div>
                <div style="
                    color:#94A3B8;
                    font-size:14px;
                ">
                    Enter a topic above and let TrendPilot
                    turn your idea into engaging social media content.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

