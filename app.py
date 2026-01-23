import streamlit as st
from itertools import combinations
import os

# Load API key from Streamlit secrets or environment
try:
    api_key = st.secrets.get("GOOGLE_GEMINI_API_KEY")  # Raises if secrets missing
    if api_key:
        os.environ["GOOGLE_GEMINI_API_KEY"] = api_key
    else:
        from dotenv import load_dotenv
        load_dotenv()
except Exception:
    # No secrets available locally; fall back to .env
    from dotenv import load_dotenv
    load_dotenv()

from ai_engine.text_processing import preprocess_text, split_into_sentences
from ai_engine.web_search import search_web
from ai_engine.similarity import compute_similarity
from ai_engine.scoring import calculate_plagiarism
from ai_engine.gemini_integration import (
    is_gemini_available, 
    generate_search_queries, 
    analyze_plagiarism_risk,
    validate_paraphrasing
)

st.set_page_config(page_title="AI Plagiarism Detection", layout="wide")

st.title("🔍 AI Plagiarism Detection System")

# Initialize variables
gemini_available = is_gemini_available()
use_google_search = False
similarity_threshold = st.slider("Similarity Threshold", 0.5, 1.0, 0.8, 0.05, key="threshold")

st.markdown("---")

# Input text area
text = st.text_area("Paste your text here", height=200, placeholder="Enter text to check for plagiarism...")

if st.button("🔎 Check Plagiarism", use_container_width=True, type="primary"):
    if not text.strip():
        st.warning("Please enter some text.")
        st.stop()

    clean_text = preprocess_text(text)
    sentences = split_into_sentences(clean_text)

    if not sentences:
        st.warning("Text is too short for plagiarism analysis.")
        st.stop()

    results = []
    
    # Create tabs for different analysis stages
    tab1, tab2, tab3 = st.tabs(["📊 Analysis", "🤖 Gemini Insights", "📋 Report"])
    
    with tab1:
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Fast web search without Gemini query generation (for speed)
        # Check each sentence against web sources
        for idx, sentence in enumerate(sentences):
            # Skip very short sentences to save time
            if len(sentence) < 30:
                results.append({
                    "sentence": sentence,
                    "web_similarity": 0.0,
                    "internal_similarity": 0.0,
                    "max_similarity": 0.0,
                    "source": "Not Found",
                    "source_type": "original",
                    "snippet_sources": []
                })
                continue
            
            status_text.text(f"🔍 Analyzing sentence {idx + 1} of {len(sentences)}...")
            progress_bar.progress((idx + 1) / len(sentences))
            
            # Fast web search with reduced results
            sources = search_web(sentence, max_results=3, use_google=use_google_search)
            max_web_score = 0
            best_url = None
            best_source_type = "original"
            snippet_sources = []

            for src in sources:
                snippet = src.get("snippet", "")
                if not snippet:
                    continue
                
                snippet_sources.append(snippet)
                score = compute_similarity(sentence, snippet)
                if score > max_web_score:
                    max_web_score = score
                    best_url = src.get("url", "Not Found")

            results.append({
                "sentence": sentence,
                "web_similarity": round(max_web_score, 2),
                "internal_similarity": 0.0,
                "max_similarity": round(max_web_score, 2),
                "source": best_url if best_url else "Not Found",
                "source_type": "web" if max_web_score >= similarity_threshold else "original",
                "snippet_sources": snippet_sources
            })
        
        # Check for internal duplicates
        status_text.text("🔄 Checking for internal duplicates...")
        for s1, s2 in combinations(sentences, 2):
            score = compute_similarity(s1, s2)
            if score >= 0.85:  # High similarity threshold for internal duplicates
                for item in results:
                    if item["sentence"] == s1:
                        item["internal_similarity"] = max(item["internal_similarity"], round(score, 2))
                        # Only update max if we don't have a web result already
                        if item["web_similarity"] == 0.0 and score > item["max_similarity"]:
                            item["max_similarity"] = round(score, 2)
                            item["source"] = "Internal duplication"
                            item["source_type"] = "internal"
                    elif item["sentence"] == s2:
                        item["internal_similarity"] = max(item["internal_similarity"], round(score, 2))
                        # Only update max if we don't have a web result already
                        if item["web_similarity"] == 0.0 and score > item["max_similarity"]:
                            item["max_similarity"] = round(score, 2)
                            item["source"] = "Internal duplication"
                            item["source_type"] = "internal"
        
        progress_bar.empty()
        status_text.empty()

        report = calculate_plagiarism(results, threshold=similarity_threshold)

        # Display results
        st.subheader(f"📊 Plagiarism Score: {report['plagiarism_percentage']}%")
        
        # Determine acceptability based on plagiarism score
        plagiarism_pct = report['plagiarism_percentage']
        
        if plagiarism_pct <= 15:
            status = "✅ EXCELLENT - Safe to Submit"
            color = "green"
            recommendation = "Your assignment has minimal plagiarism. It's safe to submit as is. No revision needed."
        elif plagiarism_pct <= 25:
            status = "✅ GOOD - Safe to Submit"
            color = "green"
            recommendation = "Your plagiarism score is acceptable for most universities (typically allow 15-25%). You can submit with confidence."
        elif plagiarism_pct <= 40:
            status = "⚠️ MODERATE - Review Needed"
            color = "orange"
            recommendation = "Your plagiarism score is getting close to the limit. Review flagged sentences and consider paraphrasing or adding citations to reduce the score below 25%."
        elif plagiarism_pct <= 60:
            status = "🔴 HIGH - Revision Required"
            color = "red"
            recommendation = "Your plagiarism score is too high for submission. You need to significantly revise your work. Paraphrase or rewrite flagged sentences to reduce plagiarism below 25%."
        else:
            status = "🛑 CRITICAL - Major Revision Required"
            color = "darkred"
            recommendation = "Your plagiarism score is critically high. Most of your content appears to be plagiarized. You must rewrite substantial portions of the assignment before submission."
        
        # Display status with color
        st.markdown(f"### {status}")
        st.info(recommendation)
        
        st.markdown("---")
        
        # Display guidance ranges
        st.markdown("### 📋 Plagiarism Score Ranges & Guidelines")
        
        guidance_col1, guidance_col2 = st.columns(2)
        
        with guidance_col1:
            st.markdown("""
            **Most Universities Accept:**
            - **0-15%**: ✅ Excellent (No action needed)
            - **15-25%**: ✅ Good (Acceptable, may need citations)
            - **25-40%**: ⚠️ Moderate (Review & paraphrase)
            - **40-60%**: 🔴 High (Significant revision needed)
            - **60%+**: 🛑 Critical (Rewrite required)
            """)
        
        with guidance_col2:
            st.markdown(f"""
            **Your Score: {plagiarism_pct}%**
            
            **Current Status:**
            - Plagiarized Sentences: {len(report["plagiarized_sentences"])}
            - Original Sentences: {len(report["clean_sentences"])}
            - Total Sentences: {len(sentences)}
            
            **Next Steps:**
            1. Review plagiarized sentences in detail
            2. Paraphrase or add proper citations
            3. Recheck score after revisions
            """)
        
        st.markdown("---")
        
        # Display summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📝 Total Sentences", len(sentences))
        with col2:
            st.metric("🚩 Plagiarized", len(report["plagiarized_sentences"]))
        with col3:
            st.metric("✅ Original", len(report["clean_sentences"]))

        st.markdown("---")
        st.write("### 🔍 Detailed Analysis")
        
        # Tabs for different views
        analysis_tab1, analysis_tab2, analysis_tab3 = st.tabs(["Plagiarized Content", "Original Content", "All Sentences"])
        
        with analysis_tab1:
            if not report["plagiarized_sentences"]:
                st.success("✅ No significant plagiarism detected!")
            else:
                for item in report["plagiarized_sentences"]:
                    with st.expander(f"🚩 {item['sentence'][:60]}...", expanded=False):
                        st.write(f"**Full Sentence:** {item['sentence']}")
                        st.write(f"**Similarity Score:** {item['max_similarity']} | **Source:** {item['source']}")
        
        with analysis_tab2:
            if report["clean_sentences"]:
                st.success(f"✅ Found {len(report['clean_sentences'])} original sentences")
                for item in report["clean_sentences"]:
                    st.write(f"- {item['sentence']}")
            else:
                st.warning("⚠️ No original content found")
        
        with analysis_tab3:
            for item in results:
                color = "🔴" if item['max_similarity'] >= similarity_threshold else "🟢"
                status = "Plagiarized" if item['max_similarity'] >= similarity_threshold else "Acceptable"
                st.write(f"{color} {item['max_similarity']} | {status} | {item['sentence'][:70]}...")
    
    # Gemini Insights Tab
    with tab2:
        if gemini_available:
            st.subheader("🤖 AI-Powered Insights")
            
            # Paraphrase detection for top plagiarized sentences
            st.markdown("#### 🔄 Paraphrase Detection")
            plagiarized = [r for r in results if r['max_similarity'] >= similarity_threshold][:3]
            
            if plagiarized:
                for item in plagiarized:
                    if item['snippet_sources']:
                        with st.expander(f"Check paraphrase: {item['sentence'][:50]}..."):
                            for idx, snippet in enumerate(item['snippet_sources'][:2]):
                                paraphrase_result = validate_paraphrasing(snippet, item['sentence'])
                                
                                prob = paraphrase_result.get('paraphrase_probability', 0)
                                is_paraphrase = paraphrase_result.get('is_paraphrase', False)
                                
                                status = "⚠️ Likely Paraphrase" if is_paraphrase else "✅ Not a paraphrase"
                                st.write(f"{status} (Confidence: {prob:.0%})")
                                st.write(f"*{paraphrase_result.get('explanation', '')}*")
            else:
                st.info("No plagiarized sentences to analyze for paraphrasing")
        else:
            st.warning("Gemini API not configured. Cannot provide AI insights.")
    
    # Report Tab
    with tab3:
        st.subheader("📋 Plagiarism Report")
        
        st.markdown("#### 📊 Statistical Summary")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Analysis Date", "Today")
            st.metric("Total Sentences", len(sentences))
            st.metric("Plagiarism Percentage", f"{report['plagiarism_percentage']}%")
        
        with col2:
            st.metric("Plagiarized Sentences", len(report["plagiarized_sentences"]))
            st.metric("Original Sentences", len(report["clean_sentences"]))
            st.metric("Threshold Used", f"{similarity_threshold:.2f}")
