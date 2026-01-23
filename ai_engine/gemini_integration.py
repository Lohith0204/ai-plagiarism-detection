"""
Google Gemini API Integration for Enhanced Plagiarism Detection
Uses Google's Generative AI for semantic analysis and content validation
"""

import os
import json
import google.generativeai as genai
from typing import Dict, List, Optional

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GOOGLE_GEMINI_API_KEY')

model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
    except Exception as e:
        print(f"Gemini configuration error: {e}")
        model = None

def generate_search_queries(text: str, num_queries: int = 3) -> List[str]:
    """
    Generate optimal search queries from input text using Gemini
    Returns list of search queries for better web search results
    """
    if not model:
        # Fallback: use simple extraction
        words = text.split()
        return [' '.join(words[i:i+5]) for i in range(0, len(words), 5)][:num_queries]
    
    try:
        prompt = f"""Given this text, generate {num_queries} concise search queries that would help find if this text has been plagiarized. 
        The queries should be specific key phrases from the text that would likely appear in original sources.
        
        Text: "{text}"
        
        Return ONLY a JSON array of strings, like: ["query1", "query2", "query3"]
        Do not include any other text or explanation."""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Try to parse JSON response
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        if start != -1 and end > start:
            queries = json.loads(response_text[start:end])
            return queries[:num_queries]
    except Exception as e:
        print(f"Gemini query generation error: {e}")
    
    return []

def analyze_plagiarism_risk(sentence: str, sources: List[str]) -> Dict:
    """
    Use Gemini to analyze plagiarism risk with semantic understanding
    Returns risk assessment and explanation
    """
    if not model:
        return {
            "risk_level": "unknown",
            "confidence": 0,
            "explanation": "Gemini API not configured"
        }
    
    try:
        sources_text = "\n".join([f"- {source}" for source in sources[:3]])
        
        prompt = f"""Analyze if this sentence could be plagiarized based on these potential sources. 
        Consider semantic similarity, paraphrasing, and conceptual overlap.
        
        Sentence: "{sentence}"
        
        Potential sources found online:
        {sources_text}
        
        Respond with a JSON object: {{"risk_level": "high|medium|low", "confidence": 0-1, "explanation": "brief reason"}}"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Parse JSON response
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end > start:
            result = json.loads(response_text[start:end])
            return result
    except Exception as e:
        print(f"Gemini analysis error: {e}")
    
    return {
        "risk_level": "unknown",
        "confidence": 0,
        "explanation": "Analysis failed"
    }

def validate_paraphrasing(original: str, suspected_paraphrase: str) -> Dict:
    """
    Detect if text is a paraphrase of original content
    Uses Gemini to understand semantic equivalence
    """
    if not model:
        return {
            "is_paraphrase": False,
            "paraphrase_probability": 0,
            "explanation": "Gemini API not configured"
        }
    
    try:
        prompt = f"""Determine if these two texts are paraphrases of each other. 
        Consider if they convey the same meaning, ideas, or information, even if worded differently.
        
        Original text: "{original}"
        Suspected paraphrase: "{suspected_paraphrase}"
        
        Respond with JSON: {{"is_paraphrase": true|false, "paraphrase_probability": 0-1, "explanation": "reason"}}"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Parse JSON response
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end > start:
            result = json.loads(response_text[start:end])
            return result
    except Exception as e:
        print(f"Gemini paraphrase detection error: {e}")
    
    return {
        "is_paraphrase": False,
        "paraphrase_probability": 0,
        "explanation": "Analysis failed"
    }

def generate_report_summary(results: List[Dict]) -> str:
    """
    Generate a detailed plagiarism report summary using Gemini
    """
    if not model:
        return "Unable to generate detailed summary - Gemini API not configured"
    
    try:
        plagiarized_count = len([r for r in results if r.get('max_similarity', 0) >= 0.8])
        total_count = len(results)
        
        plagiarized_sentences = [r['sentence'] for r in results if r.get('max_similarity', 0) >= 0.8][:5]
        
        prompt = f"""Generate a professional plagiarism report summary based on this analysis:
        
        Total sentences analyzed: {total_count}
        Plagiarized sentences found: {plagiarized_count}
        Plagiarism percentage: {(plagiarized_count/total_count*100) if total_count > 0 else 0:.1f}%
        
        Sample plagiarized content:
        {chr(10).join([f'- {s[:80]}...' for s in plagiarized_sentences])}
        
        Provide a concise, professional summary suitable for a plagiarism report."""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini report generation error: {e}")
        return "Unable to generate report summary"

def is_gemini_available() -> bool:
    """Check if Gemini API is properly configured"""
    return model is not None and GEMINI_API_KEY is not None
