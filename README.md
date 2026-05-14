**Site Broken Link & Image Checker**
====================================

A Streamlit app that crawls a website and reports **broken links and images** in real time.

Demo Link available here: https://linkcrawler.streamlit.app

**Features**
------------

*   Crawls all pages within the same domain
    
*   Checks both  links and  sources
    
*   Ignores SSL, timeout, and connection errors
    
*   Live table of broken items during scan
    
*   Downloadable CSV report
    

**Install**
-----------

(in your command line/terminal)

\*\*Please ensure that you have both Python and Git downloaded first

1. Clone this current repository + navigate into the folder

```
git clone https://github.com/vishanab/linkcrawler.git

cd linkcrawler
```

2. Download necessary packages

```
pip install -r requirements.txt
```

3. Run the app

```
streamlit run app.py
```
**Usage**
---------

1.  Enter a starting website URL
    
2.  Click **Start Scan**
    
3.  View broken links/images live
    
4.  Download the CSV report at the end
    

**Notes**
---------

*   Only HTTP status codes **≥ 400** are treated as broken
    
*   Designed for large sites using multithreading for speed
    
*   Stays within the original domain while crawling
