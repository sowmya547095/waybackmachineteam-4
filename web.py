import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

# File to store all snapshots
ARCHIVE_FILE = "web_archive.json"

# Load existing archive or initialize
if os.path.exists(ARCHIVE_FILE):
    with open(ARCHIVE_FILE, "r") as file:
        archive_data = json.load(file)
else:
    archive_data = {}

# Function to scrape page content
def scrape_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch the URL: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract content
    title = soup.title.string.strip() if soup.title else "No Title"
    headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": title,
        "headings": headings,
        "paragraphs": paragraphs
    }

# Streamlit UI
st.title("🌐 Mini Web Archive Viewer")

url = st.text_input("Enter a URL to capture its current state", placeholder="https://example.com")

if st.button("📸 Capture Snapshot"):
    if url:
        snapshot = scrape_url(url)
        if snapshot:
            archive_data.setdefault(url, []).append(snapshot)

            # Save to file
            with open(ARCHIVE_FILE, "w") as file:
                json.dump(archive_data, file, indent=2)

            st.success("Snapshot captured and saved successfully!")
    else:
        st.warning("Please enter a valid URL.")

# Show archived snapshots
st.subheader("📂 View Archived Snapshots")

selected_url = st.selectbox("Select a URL from archive", options=list(archive_data.keys()))

if selected_url:
    snapshots = archive_data[selected_url]
    snapshot_times = [s["timestamp"] for s in snapshots]
    selected_time = st.selectbox("Choose a timestamp", options=snapshot_times)

    selected_snapshot = next(s for s in snapshots if s["timestamp"] == selected_time)

    st.markdown(f"### 📝 Title: {selected_snapshot['title']}")
    st.markdown("#### 🔹 Headings:")
    for h in selected_snapshot["headings"]:
        st.write(f"- {h}")
    st.markdown("#### 📄 Paragraphs:")
    for p in selected_snapshot["paragraphs"]:
        st.write(p)

    # Download snapshot JSON
    snapshot_json = json.dumps(selected_snapshot, indent=2)
    st.download_button("⬇ Download this snapshot", snapshot_json, file_name=f"snapshot_{selected_time}.json", mime="application/json")
