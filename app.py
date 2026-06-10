import streamlit as st
import google.generativeai as genai
from firecrawl import FirecrawlApp
from duckduckgo_search import DDGS
import time

# --- 1. UI SETUP ---
st.set_page_config(page_title="Keras-Jala", layout="wide", page_icon="🌐")
st.title("Keras-Jala: Global Autonomous Intelligence")
st.markdown("Enter your query below. The system will bypass firewalls, scrape the internet, and synthesize the truth.")

# --- 2. SECURE API KEY SIDEBAR ---
with st.sidebar:
    st.header("🔑 System Credentials")
    st.write("Enter your keys to power the engines. They are not saved when you close the browser.")
    gemini_key = st.text_input("Gemini Pro API Key", type="password")
    firecrawl_key = st.text_input("Firecrawl API Key", type="password")

# --- 3. MAIN INTERFACE ---
user_query = st.text_area("What do you want to deep dive into?", placeholder="e.g., Commercial HVAC maintenance pricing trends in Australia 2026")

if st.button("🚀 Initialize Keras-Jala"):
    # Safety Checks
    if not gemini_key or not firecrawl_key:
        st.error("Please enter both API keys in the sidebar menu first.")
        st.stop()
    if not user_query:
        st.error("Please enter a research query.")
        st.stop()

    # Initialize AI and Scraper
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    app = FirecrawlApp(api_key=firecrawl_key)

    # Visual UI Tabs
    tab1, tab2, tab3 = st.tabs(["🕵️ Search Phase", "🔥 Extraction Phase", "🧠 Final Intelligence"])

    urls = []
    
    # --- AGENT 1: SEARCH ---
    with tab1:
        st.write("Analysing request and generating smart search parameters...")
        search_prompt = f'Generate a single, highly-targeted Google search query to find objective data for: "{user_query}". Output ONLY the raw query string, no quotes.'
        
        try:
            smart_query = model.generate_content(search_prompt).text.strip()
            st.info(f"**Executing Search:** {smart_query}")
            
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(smart_query, max_results=3)]
                urls = [r['link'] for r in results]
                
            if not urls: # Fallback if smart query yields nothing
                st.warning("Refining search parameters...")
                with DDGS() as ddgs:
                    results = [r for r in ddgs.text(user_query, max_results=3)]
                    urls = [r['link'] for r in results]

            for u in urls:
                st.write(f"🎯 Target Acquired: {u}")
                
        except Exception as e:
            st.error(f"Search Network Error: {e}")
            st.stop()

    if not urls:
        st.error("Search engine blocked the request. Please modify your phrasing and try again.")
        st.stop()

    # --- AGENT 2: SCRAPE ---
    with tab2:
        st.write(f"Breaking through sandboxes and scraping {len(urls)} target sites...")
        raw_data_blocks = []
        progress_bar = st.progress(0)
        
        for i, url in enumerate(urls):
            try:
                st.write(f"Extracting: {url}")
                result = app.scrape_url(url, params={'pageOptions': {'onlyMainContent': True}})
                raw_data_blocks.append(f"SOURCE URL: {url}\n\nDATA:\n{result}")
                time.sleep(1.5) # Polite delay to prevent IP bans
            except Exception as e:
                st.warning(f"Connection blocked by site security: {url}")
            progress_bar.progress((i + 1) / len(urls))

        combined_data = "\n\n---\n\n".join(raw_data_blocks)
        
        if not raw_data_blocks:
            st.error("Failed to extract data from the target URLs. Firewalls may be too strict.")
            st.stop()
            
        with st.expander("Click to view raw extracted text"):
            st.text(combined_data[:3000] + "\n...[truncated for display]")

    # --- AGENT 3: ANALYZE ---
    with tab3:
        st.write("Synthesizing global report from raw data...")
        analysis_prompt = f"""
        You are the Global Intelligence Analyst for Keras-Jala.
        Synthesize the absolute truth for the user's request: "{user_query}"
        
        You MUST base your answer ONLY on the following scraped data.
        You MUST explicitly cite the Source URLs provided in the data.
        Provide a professional, executive-level report formatted with markdown headings and bullet points.

        RAW DATA:
        {combined_data}
        """
        try:
            final_report = model.generate_content(analysis_prompt).text
            st.success("Analysis Complete!")
            st.markdown("### 🏆 Final Intelligence Report")
            st.markdown(final_report)
        except Exception as e:
            st.error(f"Analysis Generation Error: {e}")
