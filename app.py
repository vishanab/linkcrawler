import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
import pandas as pd
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import SSLError, ConnectTimeout, ReadTimeout, ConnectionError

TIMEOUT = 6
MAX_WORKERS = 30

st.set_page_config(page_title="Site Broken Link Checker", layout="wide")
st.title("Website Broken Link & Image Checker")

start_url = st.text_input("Enter a website URL to crawl:")

def same_domain(url, base):
    return urlparse(url).netloc == urlparse(base).netloc

def clean_url(url):
    url, _ = urldefrag(url)
    return url

def check_url(session, parent, url, kind):
    try:
        r = session.head(url, timeout=TIMEOUT, allow_redirects=True)
        status = r.status_code
        # Only treat REAL HTTP failures as broken
        if status >= 400:
            return {
                "parent_page": parent,
                "broken_url": url,
                "type": kind,
                "status": status
            }
    except (SSLError, ConnectTimeout, ReadTimeout, ConnectionError):
        return None
    except Exception:
        return None
    return None

def extract_links_and_images(session, page_url):
    try:
        r = session.get(page_url, timeout=TIMEOUT)
        soup = BeautifulSoup(r.text, "html.parser")
    except:
        return [], []

    links = []
    images = []

    for a in soup.find_all("a", href=True):
        link = clean_url(urljoin(page_url, a["href"]))
        if link.startswith("http"):
            links.append(link)

    for img in soup.find_all("img", src=True):
        img_url = clean_url(urljoin(page_url, img["src"]))
        images.append(img_url)

    return links, images


def crawl_site(start_url):
    visited_pages = set()
    queue = deque([start_url])
    results = []

    session = requests.Session()
    session.headers.update({"User-Agent": "SiteCheckerBot/1.0"})

    # UI placeholders
    progress = st.progress(0)
    status_text = st.empty()
    counter_text = st.empty()
    table_placeholder = st.empty()

    count = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while queue:
            current = clean_url(queue.popleft())

            if current in visited_pages:
                continue

            visited_pages.add(current)
            count += 1

            status_text.markdown(f"**Crawling:** {current}")
            progress.progress(min(count / 100, 1.0))

            links, images = extract_links_and_images(session, current)

            for link in links:
                if same_domain(link, start_url) and link not in visited_pages:
                    queue.append(link)

            futures = []
            for link in links:
                futures.append(executor.submit(check_url, session, current, link, "link"))
            for img in images:
                futures.append(executor.submit(check_url, session, current, img, "image"))

            for future in as_completed(futures):
                res = future.result()
                if res:
                    results.append(res)

                    #update table live
                    df_live = pd.DataFrame(results)
                    counter_text.markdown(f"### Broken items found: {len(df_live)}")
                    table_placeholder.dataframe(df_live, use_container_width=True)

    return pd.DataFrame(results)


if st.button("Start Scan") and start_url:
    st.info("Scanning website...")
    df = crawl_site(start_url)

    if df.empty:
        st.success("No broken links or images found 🎉")
    else:
        st.success("Scan complete!")

        st.subheader("Summary")
        st.bar_chart(df["type"].value_counts())

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV Report",
            csv,
            "broken_report.csv",
            "text/csv"
        )