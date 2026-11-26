# TrendPilot Error Analysis

The examples below are historical saved runs in `outputs/saved_results/`. They show actual analyzer findings from earlier generations, not fabricated failures from the current test suite.

| Historical run | Evidence | Problem and likely cause | Fix / current handling |
|---|---|---|---|
| [Bike riding, TikTok](../outputs/saved_results/bike_riding_tiktok_20261123_122532.json) | 65/100; relevance 0/25 and CTA 0/10 | The caption did not clearly name the requested topic and lacked a detected engagement prompt. | The writer prompt now requires naming the requested topic in its first two sentences and ending with a relevant CTA. The analyzer continues to expose missing topic/CTA feedback. |
| [Shooting, YouTube Shorts](../outputs/saved_results/shooting_youtube_shorts_20261123_163509.json) | 65/100; relevance 0/25 and length 10/20 | The generated copy was too long for the selected platform and failed to connect clearly to the topic. | Platform instructions specify a concise Shorts length; analyzer feedback is sent to the reviewer/revision loop. The generator prompt now asks for an explicit topic connection. |
| [Elon Musk achievements, X](../outputs/saved_results/elon_musk_achivements_x_twitter_20261125_122217.json) | 66/100; relevance 12/25, hashtags 10/15, CTA 0/10 | The topic was misspelled in the input, the text did not repeat enough topic terms, and the CTA was missing. | The caption prompt now names the requested topic early; the analyzer accepts CamelCase topic hashtags without discarding their capitalization. Review feedback requests the missing elements. |
| [AI Education, LinkedIn](../outputs/saved_results/ai_education_linkedin_20261124_151326.json) | 69/100; relevance 0/25; formatting warnings | The analyzer recognized â€œAI in Educationâ€ but not the equivalent â€œAI Educationâ€ topic form; formatting regexes also flagged ordinary words and hashtags. | Added the `AI Education` alias; formatting checks now exclude hashtags and only flag a likely joined-word pattern. Regression tests cover both cases. |
| [iPhone 18 Pro Max, Instagram](../outputs/saved_results/iphone_18_pro_max_instagram_20261124_155514.json) | 76/100; length 10/20, hashtags 10/15, and false formatting warnings | The draft exceeded the platformâ€™s target length, and some generated hashtags did not share the topicâ€™s keywords. | Platform-specific length feedback is included in the rewrite loop; false formatting warnings are fixed. Hashtag relevance remains a heuristic and should be checked when a generated tag is a valid synonym rather than a literal topic-word match. |

## Additional regression fixed during this audit

The assignment uses labels such as â€œReel scriptâ€ and â€œVideo script,â€ while the app uses canonical labels such as â€œReel Script.â€ The workflow previously compared these labels literally, which could skip the requested script. The entry point now normalizes assignment labels, and the test runner fails a case when a requested caption/script or saved result is missing.

The live LinkedIn Post + Reel Script run also exposed a scoring issue: the caption writer returned a reel script in its response, and the separate script tool generated another one. The analyzer counted the embedded script as caption text (296 words) and did not recognize the valid â€œExplore how...â€ CTA. The workflow now extracts the post before analysis, preserves appended hashtags, and recognizes â€œexploreâ€ as a CTA. The saved run re-scores at 134 post words, 100% topic relevance, and 100/100 under the current rubric.

## Remaining limitations

- Trend research is local-model ideation, not verified live trend data.
- The analyzer is a transparent heuristic, not a guarantee of virality or factual accuracy.
- The project is publicly available at https://github.com/subhanjavaid66/TrendPilot.

