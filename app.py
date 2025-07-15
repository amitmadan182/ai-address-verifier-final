
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import openai
import re
from urllib.parse import urljoin

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🔎 AI-Based Address Verifier")

uploaded_file = st.file_uploader("Upload Excel/CSV", type=["xlsx", "csv"])

def extract_contact_address(website):
    try:
        response = requests.get(website, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        contact_link = None
        for a in soup.find_all('a', href=True):
            if "contact" in a['href'].lower():
                contact_link = urljoin(website, a['href'])
                break
        if not contact_link:
            return "⚠️ Contact page not found"
        contact_page = requests.get(contact_link, timeout=10)
        soup_contact = BeautifulSoup(contact_page.text, 'html.parser')
        address_text = ""
        for tag in soup_contact.find_all(['p','div','address']):
            text = tag.get_text(separator=" ", strip=True)
            if re.search(r'\d{6}|\b[A-Za-z]{2,}\b', text):
                address_text += text + "\n"
        return address_text.strip() or "⚠️ No address found"
    except Exception as e:
        return f"❌ Error: {e}"

def compare_with_openai(addr1, addr2):
    prompt = f"""
Compare the two company addresses below. Are they the same location?

Address from Excel:
{addr1}

Address from Website:
{addr2}

Reply with one of: Match, Mismatch, Unclear. Include a short explanation.
"""
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role":"user","content":prompt}],
            temperature=0
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI Error: {e}"

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith("xlsx") else pd.read_csv(uploaded_file)
    address_col = st.selectbox("Select address column", df.columns)
    if st.button("Verify Addresses"):
        results = []
        for _, row in df.iterrows():
            company = row.get("Company Name", "")
            website = row.get("Website URL", "")
            given = row.get(address_col, "")
            st.info(f"Processing {company}")
            extracted = extract_contact_address(website)
            verdict = compare_with_openai(given, extracted)
            results.append({
                "Company Name": company,
                "Website": website,
                "Given Address": given,
                "Extracted Address": extracted,
                "Verdict": verdict
            })
        res_df = pd.DataFrame(results)
        st.dataframe(res_df)
        csv = res_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Results", csv, "results.csv", "text/csv")
