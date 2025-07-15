
# AI Address Verifier

This Streamlit app allows you to upload a list of company addresses and website URLs in Excel or CSV format. It scrapes the website's "Contact Us" page, extracts addresses, and compares them using OpenAI.

## How to Deploy

1. Upload all files to a GitHub repo
2. Deploy the repo on [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Add your OpenAI API key as a secret:

```
OPENAI_API_KEY = "sk-..."
```

4. Use the app by uploading an Excel with columns: Company Name, Website URL, and Address
