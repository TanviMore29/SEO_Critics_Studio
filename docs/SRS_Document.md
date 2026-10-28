# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

---

## 1. COVER PAGE

<div align="center">

# SEO CRITICS STUDIO

### A Web-Based SEO Analysis Platform

**Software Requirements Specification Document**

---

**Submitted in partial fulfilment of the requirements for the award of the degree of**

**Bachelor of Science in Computer Science**

---

**Submitted By:**
[Student Name]
[Roll Number / Enrollment Number]

**Under the Guidance of:**
[Guide Name]
[Designation]

---

**Department of Computer Science**
[College / University Name]
[Academic Year]

</div>

---

## 2. CERTIFICATE

This is to certify that the Mini Project titled **"SEO Critics Studio – A Web-Based SEO Analysis Platform"** has been carried out by **[Student Name]**, Roll Number **[Roll Number]**, as a part of the requirements for the Degree of Bachelor of Science in Computer Science during the academic year **[Academic Year]**.

This project work has been carried out under my supervision and is a record of bona fide work done by the student.

| Role | Name | Signature |
|---|---|---|
| Project Guide | [Guide Name] | __________________ |
| Head of Department | [HOD Name] | __________________ |
| External Examiner | [Examiner Name] | __________________ |

**Date:** [Submission Date]
**Place:** [College Location]

---

## 3. ACKNOWLEDGEMENT

I would like to express my sincere gratitude to my project guide, **[Guide Name]**, for their invaluable guidance, encouragement, and support throughout the development of this project.

I am also thankful to the Head of the Department, **[HOD Name]**, and all faculty members of the Department of Computer Science for providing the necessary resources and a conducive environment for learning.

I extend my thanks to my classmates and family members for their continuous support and motivation during the course of this project.

**[Student Name]**

---

## 4. ABSTRACT

Search Engine Optimization (SEO) plays a critical role in determining the visibility and ranking of websites on search engines. Manually auditing a website for SEO issues is a time-consuming and error-prone process, especially as the number of pages increases.

**SEO Critics Studio** is a desktop-accessible, web-based SEO analysis platform designed to automate the process of crawling a website and evaluating its technical and on-page SEO health. The system accepts a website URL as input, crawls multiple internal pages, and analyzes various SEO parameters such as page titles, meta descriptions, heading structures, image alt attributes, broken links, HTTPS usage, sitemap and robots.txt validity, and page performance metrics.

Based on the analysis, the system computes an SEO score out of 100, categorizes the website's health into one of five levels (Excellent, Good, Average, Poor, Critical), and generates a downloadable report in HTML, CSV, and Excel formats.

The platform is built using **Python (FastAPI)** for the backend, **HTML5, CSS3, and JavaScript** for the frontend, and **SQLite** for data persistence. Libraries such as **Requests**, **BeautifulSoup4**, **lxml**, **openpyxl**, and **ReportLab** are used for crawling, parsing, and report generation.

This project demonstrates the practical application of web crawling, HTML parsing, and data analysis techniques to solve a real-world problem faced by website owners, students, and small businesses who cannot afford expensive commercial SEO tools.

---

## 5. TABLE OF CONTENTS

| Chapter No. | Title |
|---|---|
| 1 | Cover Page |
| 2 | Certificate |
| 3 | Acknowledgement |
| 4 | Abstract |
| 5 | Table of Contents |
| 6 | Introduction |
| 7 | Existing System |
| 8 | Proposed System |
| 9 | Feasibility Study |
| 10 | Overall Description |
| 11 | Functional Requirements |
| 12 | Non-Functional Requirements |
| 13 | Technology Stack |
| 14 | Project Structure |
| 15 | Database Design |
| 16 | System Architecture |
| 17 | Data Flow Diagram |
| 18 | Use Case Diagram |
| 19 | Activity Diagram |
| 20 | Sequence Diagram |
| 21 | Module Description |
| 22 | SEO Score Distribution |
| 23 | SEO Health Levels |
| 24 | Advantages |
| 25 | Limitations |
| 26 | Future Scope |
| 27 | Testing |
| 28 | Conclusion |
| 29 | References |

---

## 6. INTRODUCTION

### 6.1 Purpose

The purpose of this document is to provide a detailed description of the requirements for the **SEO Critics Studio** system. It describes the functional and non-functional requirements, system architecture, database design, and overall scope of the project. This document is intended to serve as a reference for the development, testing, and evaluation of the mini project.

### 6.2 Objectives

The key objectives of the project are:

- To design a web-based tool that automatically crawls a given website.
- To analyze technical and on-page SEO parameters of the crawled pages.
- To compute a quantitative SEO score for the website.
- To identify common SEO issues such as missing meta tags, broken links, and missing alt attributes.
- To generate downloadable reports in multiple formats (HTML, CSV, Excel).
- To provide a simple, dashboard-driven interface that requires no login or account setup.

### 6.3 Scope

**SEO Critics Studio** is intended for:

- Students who wish to understand SEO auditing concepts practically.
- Website owners who want a quick technical SEO health check.
- Small businesses without the budget for enterprise-grade SEO tools.

The scope of the system is limited to:

- Single-user, single-session operation (no login/registration).
- Analysis of publicly accessible pages of a website.
- Static HTML content analysis (JavaScript-rendered content is out of scope).
- Local deployment on a single machine (not a hosted cloud SaaS product).

---

## 7. EXISTING SYSTEM

Currently, SEO analysis for most students, freelancers, and small website owners is carried out **manually** or through fragmented tools. The limitations of the existing manual approach are:

- **Time-Consuming:** Manually checking every page for title tags, meta descriptions, and headings is impractical for websites with many pages.
- **Human Error:** Manual review is prone to oversight, especially for issues like duplicate titles or missing alt attributes.
- **No Centralized Report:** Manual analysis does not produce a structured, shareable report.
- **No Scoring Mechanism:** There is no standard way to quantify how "SEO-healthy" a website is.
- **Lack of Automation:** Checking hundreds of internal links, images, and broken URLs manually is nearly impossible.
- **Fragmented Tools:** Existing browser extensions or online checkers usually analyze a single page at a time rather than crawling an entire website.
- **Cost:** Many existing commercial-grade crawling tools are paid, licensed, or require complex installation, making them inaccessible for academic use.

---

## 8. PROPOSED SYSTEM

**SEO Critics Studio** addresses the above limitations by providing an automated, self-contained SEO auditing platform.

Key features of the proposed system:

- Accepts a single website URL as input and automatically crawls internal pages up to a configurable depth/limit.
- Analyzes each crawled page against a defined set of technical and on-page SEO parameters.
- Detects issues such as broken links, redirects, missing metadata, and missing alt attributes.
- Validates the presence and correctness of `sitemap.xml` and `robots.txt`.
- Computes a **cumulative SEO score out of 100**, broken down by category.
- Classifies the website into one of five health levels.
- Generates professional reports in **HTML, CSV, and Excel** formats for offline reference.
- Requires **no login, no registration, and no cloud dependency** — the application opens directly to the dashboard.

The proposed system focuses purely on **technical and on-page SEO auditing** and deliberately excludes authentication, multi-user support, AI-based recommendations, and cybersecurity scanning to keep the scope realistic for a mini project.

---

## 9. FEASIBILITY STUDY

### 9.1 Technical Feasibility

- The technology stack (Python, FastAPI, SQLite, BeautifulSoup4) is open-source, well-documented, and suitable for academic development.
- All required libraries are freely available via `pip` and do not require paid licenses.
- The system can run on a standard personal computer without specialized hardware.

### 9.2 Operational Feasibility

- The application starts directly at the dashboard, requiring no training for basic use.
- The interface is designed to be intuitive: enter a URL, start a scan, view the report.
- No server administration or complex configuration is required from the end user.

### 9.3 Economic Feasibility

- All tools, frameworks, and libraries used are free and open-source.
- No cloud hosting, server rental, or subscription costs are incurred since the system runs locally.
- Development and deployment costs are limited to the time invested by the student developer.

---

## 10. OVERALL DESCRIPTION

### 10.1 Product Perspective

SEO Critics Studio is a **standalone, locally-run web application**. It is not part of a larger product family and does not depend on any external cloud service. The application consists of a browser-based frontend communicating with a local FastAPI backend, which in turn interacts with a local SQLite database.

### 10.2 Product Functions

- Accept a website URL from the user via the dashboard.
- Crawl the website's internal pages.
- Analyze each page for technical and on-page SEO parameters.
- Store crawl and analysis results in the database.
- Compute an overall SEO score and category-wise breakdown.
- Generate and export reports in HTML, CSV, and Excel formats.

### 10.3 User Characteristics

| User Type | Description |
|---|---|
| Student / Evaluator | Uses the tool to understand SEO auditing and evaluate the mini project. |
| Website Owner | Uses the tool to identify and fix SEO issues on their own website. |
| General User | Any individual with basic web browsing knowledge and no technical SEO background. |

### 10.4 Assumptions

- The target website is publicly accessible over the internet.
- The target website primarily uses static/server-rendered HTML content.
- The user has a working internet connection to allow the crawler to fetch pages.
- The system is used by a single user at a time on a local machine.

### 10.5 Dependencies

- Availability of Python 3.x runtime environment.
- Internet connectivity for crawling external websites.
- Target website must not block automated requests via robots.txt restrictions that the crawler is configured to respect.

---

## 11. FUNCTIONAL REQUIREMENTS

### 11.1 Home Dashboard

| Attribute | Description |
|---|---|
| **Purpose** | Serves as the landing page where the user initiates a new SEO scan. |
| **Inputs** | Website URL, optional crawl depth/page limit. |
| **Outputs** | Navigation to scan progress view; list of recent scan history. |
| **Processing** | Validates the entered URL format, checks reachability, and triggers the crawler module upon submission. |

### 11.2 Website Crawler

| Attribute | Description |
|---|---|
| **Purpose** | Discovers and fetches internal pages of the target website. |
| **Inputs** | Root URL, crawl depth, maximum page limit. |
| **Outputs** | List of discovered page URLs with raw HTML content. |
| **Processing** | Starts from the root URL, extracts internal links using BeautifulSoup4/lxml, queues unvisited links, and fetches each page using the Requests library while respecting robots.txt rules. |

### 11.3 URL Analyzer

| Attribute | Description |
|---|---|
| **Purpose** | Evaluates each crawled URL for structural and response-level health. |
| **Inputs** | Crawled page URL. |
| **Outputs** | HTTP status code, response time, page size, redirect chain, HTTPS status. |
| **Processing** | Sends an HTTP request to the URL, records response headers, status code, timing, and checks whether the connection uses HTTPS. |

### 11.4 Metadata Analyzer

| Attribute | Description |
|---|---|
| **Purpose** | Analyzes title tags, meta descriptions, and meta robots directives. |
| **Inputs** | Parsed HTML `<head>` content of a page. |
| **Outputs** | Title text/length, meta description text/length, meta robots value, duplicate title/description flags. |
| **Processing** | Extracts `<title>` and `<meta>` tags using BeautifulSoup4, checks length against recommended limits, and compares against other pages to detect duplicates. |

### 11.5 Technical SEO Analyzer

| Attribute | Description |
|---|---|
| **Purpose** | Checks core technical SEO elements of a page. |
| **Inputs** | Parsed HTML content, canonical tag, heading tags. |
| **Outputs** | Canonical URL validity, H1/H2 presence and count, word count. |
| **Processing** | Parses `<link rel="canonical">`, counts `<h1>` and `<h2>` tags, and calculates visible text word count. |

### 11.6 Internal Link Analyzer

| Attribute | Description |
|---|---|
| **Purpose** | Evaluates the internal and external linking structure of a page. |
| **Inputs** | All `<a>` tags on the page. |
| **Outputs** | Internal link count, external link count, broken link list. |
| **Processing** | Classifies links as internal or external based on domain matching, and verifies link reachability to detect broken links (4xx/5xx responses). |

### 11.7 Image SEO Analyzer

| Attribute | Description |
|---|---|
| **Purpose** | Checks images on a page for SEO best practices. |
| **Inputs** | All `<img>` tags on the page. |
| **Outputs** | Total image count, count of images missing ALT attributes. |
| **Processing** | Iterates through image tags, checks for the presence and non-emptiness of the `alt` attribute, and records results. |

### 11.8 Sitemap Analyzer

| Attribute | Description |
|---|---|
| **Purpose** | Validates the presence and structure of the website's sitemap. |
| **Inputs** | `sitemap.xml` URL (derived from root domain). |
| **Outputs** | Sitemap existence flag, number of URLs listed, validity status. |
| **Processing** | Fetches `sitemap.xml`, parses it using lxml, and checks whether it is well-formed and lists valid URLs. |

### 11.9 robots.txt Analyzer

| Attribute | Description |
|---|---|
| **Purpose** | Validates the presence and rules defined in `robots.txt`. |
| **Inputs** | `robots.txt` URL (derived from root domain). |
| **Outputs** | robots.txt existence flag, disallowed paths list, sitemap reference (if present). |
| **Processing** | Fetches and parses `robots.txt` content to extract `User-agent`, `Disallow`, and `Sitemap` directives. |

### 11.10 Report Generator

| Attribute | Description |
|---|---|
| **Purpose** | Compiles all analysis results into a downloadable report. |
| **Inputs** | Aggregated scan data from all analyzer modules. |
| **Outputs** | HTML report, CSV report, Excel (.xlsx) report. |
| **Processing** | Uses ReportLab/HTML templating for the HTML report, openpyxl for the Excel report, and Python's built-in CSV module for the CSV report. |

---

## 12. NON-FUNCTIONAL REQUIREMENTS

| Requirement | Description |
|---|---|
| **Performance** | The system should crawl and analyze a website of up to 50 pages within a reasonable time (a few minutes), depending on network conditions. |
| **Reliability** | The system should handle unreachable pages or timeouts gracefully without crashing the scan. |
| **Availability** | The application should be available whenever the local server is running; no external uptime dependency. |
| **Maintainability** | The codebase should be modular, with each analyzer implemented as an independent, testable component. |
| **Scalability** | The system should be designed so that additional SEO checks can be added as new modules without major redesign. |
| **Compatibility** | The frontend should work on modern browsers (Chrome, Firefox, Edge). |
| **Usability** | The dashboard should be simple enough for a first-time user to start a scan without documentation. |

---

## 13. TECHNOLOGY STACK

### 13.1 Frontend

| Technology | Purpose |
|---|---|
| HTML5 | Structure of the web pages |
| CSS3 | Styling and layout |
| JavaScript | Client-side interactivity and dynamic updates |

### 13.2 Backend

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend web framework and REST API |

### 13.3 Database

| Technology | Purpose |
|---|---|
| SQLite | Lightweight, file-based relational database |

### 13.4 Python Libraries

| Library | Purpose |
|---|---|
| requests | Fetching HTML content over HTTP/HTTPS |
| BeautifulSoup4 | Parsing and extracting data from HTML |
| lxml | Fast XML/HTML parsing (used with sitemap parsing) |
| openpyxl | Generating Excel (.xlsx) reports |
| ReportLab | Generating formatted HTML/PDF-style report content |

### 13.5 Development Tools

| Tool | Purpose |
|---|---|
| Visual Studio Code | Source code editor |
| Git | Version control |
| GitHub | Remote repository hosting |

---

## 14. PROJECT STRUCTURE

```
seo-critics-studio/
│
├── backend/
│   ├── main.py                     # FastAPI application entry point
│   ├── crawler/
│   │   ├── website_crawler.py
│   │   └── link_extractor.py
│   ├── analyzers/
│   │   ├── url_analyzer.py
│   │   ├── metadata_analyzer.py
│   │   ├── technical_seo_analyzer.py
│   │   ├── internal_link_analyzer.py
│   │   ├── image_seo_analyzer.py
│   │   ├── sitemap_analyzer.py
│   │   └── robots_analyzer.py
│   ├── scoring/
│   │   └── score_calculator.py
│   ├── reports/
│   │   ├── html_report_generator.py
│   │   ├── csv_report_generator.py
│   │   └── excel_report_generator.py
│   ├── database/
│   │   ├── models.py
│   │   ├── db_connection.py
│   │   └── seo_critics.db
│   └── requirements.txt
│
├── frontend/
│   ├── index.html                  # Home Dashboard
│   ├── scan.html                   # Scan progress page
│   ├── report.html                 # Report view page
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── dashboard.js
│       └── report.js
│
├── reports_output/
│   ├── html/
│   ├── csv/
│   └── excel/
│
├── docs/
│   └── SRS_Document.md
│
└── README.md
```

---

## 15. DATABASE DESIGN

### 15.1 Websites Table

| Field | Type | Constraint |
|---|---|---|
| website_id | INTEGER | Primary Key, Auto Increment |
| root_url | TEXT | Not Null |
| domain_name | TEXT | Not Null |
| date_added | DATETIME | Default Current Timestamp |

### 15.2 Pages Table

| Field | Type | Constraint |
|---|---|---|
| page_id | INTEGER | Primary Key, Auto Increment |
| website_id | INTEGER | Foreign Key → Websites(website_id) |
| page_url | TEXT | Not Null |
| status_code | INTEGER | — |
| title | TEXT | — |
| meta_description | TEXT | — |
| h1_count | INTEGER | — |
| word_count | INTEGER | — |
| response_time_ms | INTEGER | — |

### 15.3 Images Table

| Field | Type | Constraint |
|---|---|---|
| image_id | INTEGER | Primary Key, Auto Increment |
| page_id | INTEGER | Foreign Key → Pages(page_id) |
| image_url | TEXT | — |
| alt_text | TEXT | — |
| has_alt | BOOLEAN | Default False |

### 15.4 Reports Table

| Field | Type | Constraint |
|---|---|---|
| report_id | INTEGER | Primary Key, Auto Increment |
| website_id | INTEGER | Foreign Key → Websites(website_id) |
| overall_score | INTEGER | — |
| health_level | TEXT | — |
| generated_on | DATETIME | Default Current Timestamp |
| report_path | TEXT | — |

### 15.5 ScanHistory Table

| Field | Type | Constraint |
|---|---|---|
| scan_id | INTEGER | Primary Key, Auto Increment |
| website_id | INTEGER | Foreign Key → Websites(website_id) |
| scan_date | DATETIME | Default Current Timestamp |
| pages_scanned | INTEGER | — |
| status | TEXT | e.g., Completed, Failed, In Progress |

### 15.6 Entity Relationships

- One **Website** has many **Pages** (1 : N)
- One **Page** has many **Images** (1 : N)
- One **Website** has many **Reports** (1 : N)
- One **Website** has many **ScanHistory** records (1 : N)

---

## 16. SYSTEM ARCHITECTURE

```
                     ┌───────────────────────────┐
                     │        FRONTEND            │
                     │  (HTML5, CSS3, JavaScript) │
                     │   Dashboard / Report View   │
                     └──────────────┬──────────────┘
                                    │  HTTP Requests (REST API)
                                    ▼
                     ┌───────────────────────────┐
                     │         BACKEND             │
                     │      (Python + FastAPI)     │
                     │  ┌───────────────────────┐  │
                     │  │  Website Crawler       │  │
                     │  ├───────────────────────┤  │
                     │  │  SEO Analyzer Modules  │  │
                     │  ├───────────────────────┤  │
                     │  │  Score Calculator      │  │
                     │  ├───────────────────────┤  │
                     │  │  Report Generator      │  │
                     │  └───────────────────────┘  │
                     └──────────────┬──────────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     ▼                              ▼
          ┌─────────────────────┐       ┌───────────────────────┐
          │   SQLite Database    │       │   External Websites     │
          │ (Websites, Pages,    │       │ (Crawled via Requests   │
          │  Images, Reports,    │       │   + BeautifulSoup4)      │
          │  ScanHistory)         │       └───────────────────────┘
          └─────────────────────┘
```

**Component Description:**

- **Frontend:** Provides the dashboard UI, sends scan requests to the backend, and displays reports.
- **Backend:** Hosts the FastAPI REST endpoints, orchestrates crawling, analysis, scoring, and report generation.
- **Crawler:** Fetches pages from the target website using `requests` and extracts links using `BeautifulSoup4`/`lxml`.
- **Database:** Stores crawl data, analysis results, and generated report metadata using SQLite.

---

## 17. DATA FLOW DIAGRAM

### 17.1 Level 0 DFD (Context Diagram)

```
        ┌────────┐         Website URL          ┌─────────────────────┐
        │        │ ─────────────────────────────▶│                     │
        │  User   │                                │  SEO Critics Studio │
        │        │ ◀───────────────────────────── │                     │
        └────────┘        SEO Report               └─────────────────────┘
```

### 17.2 Level 1 DFD

```
 User
  │
  │ (1) Enter URL
  ▼
┌─────────────────┐
│ Home Dashboard    │
└────────┬──────────┘
         │ (2) Trigger Crawl
         ▼
┌─────────────────┐        (3) Store Pages        ┌─────────────────┐
│ Website Crawler   │ ─────────────────────────────▶│   Database        │
└────────┬──────────┘                                └─────────────────┘
         │ (4) Pass HTML                                     ▲
         ▼                                                    │
┌─────────────────┐        (5) Store Results                 │
│  SEO Analyzers    │ ───────────────────────────────────────┘
└────────┬──────────┘
         │ (6) Aggregated Data
         ▼
┌─────────────────┐
│ Score Calculator   │
└────────┬──────────┘
         │ (7) Final Score
         ▼
┌─────────────────┐        (8) Save Report        ┌─────────────────┐
│ Report Generator   │ ─────────────────────────────▶│   Database        │
└────────┬──────────┘                                └─────────────────┘
         │ (9) Display/Download
         ▼
       User
```

---

## 18. USE CASE DIAGRAM

```
                     SEO Critics Studio
        ┌─────────────────────────────────────────┐
        │                                           │
        │     (Enter Website URL)                   │
        │            │                               │
        │     (Start Crawl)                          │
        │            │                               │
        │     (View Scan Progress)                   │
        │            │                               │
   User ●────────(View SEO Report)                    │
        │            │                               │
        │     (Download HTML Report)                 │
        │            │                               │
        │     (Download CSV Report)                  │
        │            │                               │
        │     (Download Excel Report)                │
        │            │                               │
        │     (View Scan History)                    │
        │                                           │
        └─────────────────────────────────────────┘
```

---

## 19. ACTIVITY DIAGRAM

```
        ┌───────────────┐
        │     Start        │
        └────────┬──────────┘
                 ▼
        ┌───────────────────┐
        │ Enter Website URL   │
        └────────┬──────────────┘
                 ▼
        ┌───────────────────┐
        │  Validate URL        │
        └────────┬──────────────┘
                 ▼
              ◇ Valid? ◇──── No ───▶ [Show Error] ──▶ End
                 │ Yes
                 ▼
        ┌───────────────────┐
        │  Crawl Website       │
        └────────┬──────────────┘
                 ▼
        ┌───────────────────┐
        │ Run SEO Analyzers    │
        └────────┬──────────────┘
                 ▼
        ┌───────────────────┐
        │ Calculate SEO Score  │
        └────────┬──────────────┘
                 ▼
        ┌───────────────────┐
        │ Generate Report(s)   │
        └────────┬──────────────┘
                 ▼
        ┌───────────────────┐
        │ Display Report to    │
        │       User             │
        └────────┬──────────────┘
                 ▼
              ┌────────┐
              │  End     │
              └────────┘
```

---

## 20. SEQUENCE DIAGRAM

```
User        Dashboard        Crawler        Analyzers        Database       ReportGen
 │               │                │                │                │              │
 │──Enter URL───▶│                │                │                │              │
 │               │──Start Crawl──▶│                │                │              │
 │               │                │──Fetch Pages──▶│                │              │
 │               │                │                │──Analyze Data─▶│              │
 │               │                │                │                │──Save────────▶│
 │               │                │                │                │◀────Stored────│
 │               │                │                │◀───Results─────│              │
 │               │◀───Score/Data──────────────────│                │              │
 │               │───────────────────────Generate Report──────────────────────────▶│
 │               │◀───────────────────────Report Ready───────────────────────────────│
 │◀──View/Download Report─────────│                │                │              │
```

---

## 21. MODULE DESCRIPTION

| Module | Description |
|---|---|
| **Home Dashboard** | Entry point of the application where the user submits a website URL and configures scan parameters. |
| **Website Crawler** | Traverses the target website starting from the root URL, discovering and queuing internal pages for analysis. |
| **URL Analyzer** | Checks each page's HTTP response — status codes, response time, redirects, and HTTPS usage. |
| **Metadata Analyzer** | Extracts and evaluates title tags and meta descriptions, flagging missing or duplicate values. |
| **Technical SEO Analyzer** | Validates canonical tags, heading structure (H1/H2), and page content length. |
| **Internal Link Analyzer** | Maps the internal linking structure and identifies broken or dead links. |
| **Image SEO Analyzer** | Reviews all images on a page and flags those missing descriptive ALT attributes. |
| **Sitemap Analyzer** | Confirms the existence and validity of `sitemap.xml` and counts listed URLs. |
| **robots.txt Analyzer** | Confirms the existence of `robots.txt` and extracts crawl directives. |
| **Report Generator** | Consolidates all findings into a single scored report, exportable in HTML, CSV, and Excel formats. |

---

## 22. SEO SCORE DISTRIBUTION

The overall SEO score is calculated out of **100 points**, distributed across the following categories:

| Category | Maximum Points |
|---|---|
| Metadata (Title, Meta Description, Meta Robots) | 20 |
| Technical SEO (Canonical, H1/H2, Word Count) | 20 |
| Images (ALT Tag Coverage) | 15 |
| Links (Internal/External/Broken Links) | 15 |
| Sitemap (sitemap.xml Validity) | 10 |
| robots.txt (Validity and Rules) | 10 |
| Performance (Response Time, Page Size, HTTPS) | 10 |
| **Total** | **100** |

---

## 23. SEO HEALTH LEVELS

| Score Range | Health Level | Description |
|---|---|---|
| 90 – 100 | Excellent | Website follows nearly all SEO best practices. |
| 75 – 89 | Good | Minor SEO issues present; overall healthy site. |
| 55 – 74 | Average | Moderate issues that should be addressed. |
| 35 – 54 | Poor | Significant SEO gaps affecting visibility. |
| 0 – 34 | Critical | Major SEO deficiencies requiring immediate attention. |

---

## 24. ADVANTAGES

- Provides an automated, structured approach to SEO auditing instead of manual checks.
- No login or account setup required — immediate access to functionality.
- Generates multiple report formats suitable for different use cases (viewing, sharing, spreadsheet analysis).
- Lightweight and runs locally without cloud hosting costs.
- Modular design allows easy extension with additional SEO checks in the future.
- Provides a clear, quantifiable score that is easy for non-technical users to interpret.

---

## 25. LIMITATIONS

- Does not render or analyze JavaScript-heavy, client-side rendered pages.
- Limited to a single user and single machine; not designed for concurrent multi-user access.
- Does not provide AI-based or predictive SEO recommendations.
- Crawl depth and page limits may restrict analysis of very large websites.
- Does not perform cybersecurity or vulnerability assessments.
- Report accuracy depends on the target website allowing automated access (via robots.txt).

---

## 26. FUTURE SCOPE

- Support for JavaScript-rendered page analysis using headless browser rendering.
- Export of reports in PDF format in addition to HTML, CSV, and Excel.
- Addition of more granular SEO metrics (e.g., structured data/schema validation).
- Dark Mode support for the dashboard interface.
- Website comparison feature to benchmark two websites side-by-side.
- Batch URL scanning to analyze multiple independent websites in one session.

---

## 27. TESTING

### 27.1 Unit Testing

Each analyzer module (Metadata Analyzer, Image SEO Analyzer, etc.) is tested independently with sample HTML inputs to verify correct extraction and evaluation logic.

### 27.2 Integration Testing

Verifies that the Crawler, Analyzers, Score Calculator, and Report Generator work correctly together, ensuring data flows accurately from crawling to final report generation.

### 27.3 System Testing

The complete application is tested end-to-end: entering a URL on the dashboard, running a full scan, and validating that the generated report is complete and accurate.

### 27.4 Performance Testing

Measures the time taken to crawl and analyze websites of varying sizes (e.g., 10 pages vs. 50 pages) to ensure acceptable response times.

### 27.5 Browser Testing

The dashboard and report pages are tested across major browsers (Chrome, Firefox, Edge) to confirm consistent rendering and functionality.

---

## 28. CONCLUSION

**SEO Critics Studio** successfully demonstrates the design and implementation of an automated SEO analysis platform suitable for an undergraduate mini project. By combining web crawling, HTML parsing, scoring logic, and multi-format report generation, the system provides a practical and educational tool for understanding technical and on-page SEO principles.

The project fulfils its stated objectives of automating SEO audits, generating quantifiable scores, and producing actionable reports — all without the complexity of user authentication, cloud infrastructure, or AI-driven components, keeping it well-suited to the scope of a B.Sc. Computer Science mini project.

---

## 29. REFERENCES

1. FastAPI Official Documentation — https://fastapi.tiangolo.com/
2. BeautifulSoup4 Documentation — https://www.crummy.com/software/BeautifulSoup/bs4/doc/
3. Python Requests Library Documentation — https://requests.readthedocs.io/
4. lxml Documentation — https://lxml.de/
5. openpyxl Documentation — https://openpyxl.readthedocs.io/
6. ReportLab Documentation — https://www.reportlab.com/docs/reportlab-userguide.pdf
7. SQLite Documentation — https://www.sqlite.org/docs.html
8. Google Search Central — SEO Starter Guide — https://developers.google.com/search/docs
9. IEEE Recommended Practice for Software Requirements Specifications (IEEE Std 830-1998)
10. Sommerville, I., *Software Engineering*, 10th Edition, Pearson Education.

---

*End of Document*
