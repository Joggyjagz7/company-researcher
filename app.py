import streamlit as st
import requests
import openai
import os

# Set up page configuration
st.set_page_config(
    page_title="Company Improvement Analyzer",
    page_icon="🚀",
    layout="centered"
)

# Title and description
st.title("🏢 Company Improvement Analyzer")
st.markdown("Enter a company URL to receive actionable improvement suggestions based on their website content.")

# Input section
url = st.text_input(
    "Enter company URL:",
    placeholder="https://example.com",
    help="Please include http:// or https://"
)

# API key handling
firecrawl_api_key = st.secrets.get("FIRECRAWL_API_KEY", os.getenv("FIRECRAWL_API_KEY"))
openai_api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

if not firecrawl_api_key or not openai_api_key:
    st.error("API keys not configured. Please set FIRECRAWL_API_KEY and OPENAI_API_KEY.")
    st.stop()

def scrape_website(url):
    """Scrape website content using Firecrawl"""
    headers = {"Authorization": f"Bearer {firecrawl_api_key}"}
    endpoint = "https://api.firecrawl.dev/v0/scrape"
    
    try:
        response = requests.get(
            endpoint,
            headers=headers,
            params={"url": url}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error scraping website: {str(e)}")
        return None

def generate_improvements(content):
    """Generate improvements using OpenAI"""
    prompt = f"""
    Analyze the following website content and provide specific, actionable recommendations to improve the company.
    Focus on these key areas:
    1. SEO optimization
    2. User experience improvements
    3. Content strategy enhancements
    4. Technical improvements
    5. Conversion rate optimization
    6. Accessibility compliance
    7. Mobile responsiveness
    
    Structure your response with clear headings for each category and bullet points for recommendations.
    Include brief explanations and practical implementation tips.
    
    Website Content:
    {content}
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a business development expert specializing in digital strategy."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating improvements: {str(e)}")
        return None

if url:
    if not url.startswith(('http://', 'https://')):
        st.warning("Please include http:// or https:// in the URL")
        st.stop()
    
    with st.spinner("Analyzing website..."):
        # Scrape website content
        scraped_data = scrape_website(url)
        
        if scraped_data and scraped_data.get('data'):
            content = scraped_data['data'].get('markdown') or scraped_data['data'].get('text', '')
            
            if not content:
                st.error("No content found on the website")
                st.stop()
            
            # Generate improvements
            with st.spinner("Generating recommendations..."):
                improvements = generate_improvements(content[:12000])  # Truncate to 12k chars for token limit
                
            if improvements:
                st.success("Analysis Complete!")
                st.markdown("## Actionable Recommendations")
                st.markdown(improvements)
                
                # Download button
                st.download_button(
                    label="Download Recommendations",
                    data=improvements,
                    file_name="company_improvements.md",
                    mime="text/markdown"
                )
            else:
                st.error("Failed to generate improvements")
        else:
            st.error("Could not retrieve website content. Please check the URL and try again.")