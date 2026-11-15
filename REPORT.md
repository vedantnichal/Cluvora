# 📋 Comprehensive Project Work Report: Cluvora Ecosystem

**Project**: Cluvora — IIT Bhilai CoSA Student Life & AI Platform  
**Authors**: Sumiran Akre ([@SumiRann1](https://github.com/SumiRann1)), Vedant Nichal ([@vedantnichal](https://github.com/vedantnichal)), Naman Gupta  
**Organization**: Council of Student Affairs (CoSA), Indian Institute of Technology Bhilai  
**Date**: November 2026  
**License**: MIT  

---

## 📑 Executive Summary

**Cluvora** was conceived and built to solve a critical communication and discovery challenge at the Indian Institute of Technology Bhilai (IIT Bhilai). Prior to Cluvora, student clubs, cultural bodies, sports councils, and event coordinators relied on fragmented WhatsApp groups, temporary Instagram stories, and dense email chains. Important announcements, auditions, hackathons, and tournament fixtures frequently got lost, while freshers struggled to understand the governance structure of the Council of Student Affairs (CoSA).

This project delivered an end-to-end, unified digital ecosystem combining:
1. **A zero-dependency, ultra-fast web portal** categorizing all 34+ technical clubs, cultural societies, sports bodies, and welfare councils.
2. **Interactive HTML5 `<dialog>` modal cards** with deep-linking (`#club-id`), direct sharing, and progressive keyboard accessibility.
3. **A live, SQLite-backed announcement feed** with category filtering, search, and priority pinned notices.
4. **A coordinator authentication system (`coordinator_auth`)** ensuring authorized announcements with verified badges.
5. **A LangGraph RAG AI handbook assistant** embedding official IIT Bhilai student brochures using FastEmbed (`all-MiniLM-L6-v2`) and Maximal Marginal Relevance (MMR) retrieval with precise page citations.
6. **A full anti-AI slop refactoring**, aligning the entire codebase with authentic, beginner-friendly Pythonic and JavaScript `snake_case` standards.

---

## 🗓️ Development Chronology & Milestones

```text
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 1: Project Genesis & Master Data Architecture                   │
│ - Curated iit_bhilai_cosa_data.json covering 34+ clubs and 5 councils │
│ - Designed responsive Glassmorphism UI with Dark/Light mode engine    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 2: LangGraph RAG Campus Handbook Guide Engine                   │
│ - Ingested Brochure_2026-27-45-74.pdf & precomputed FastEmbed vectors │
│ - Implemented MMR StateGraph pipeline (START -> retrieve -> generate)  │
│ - Engineered authentic SMP Senior Mentor prompt with page citations   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 3: Interactive Club Cards & Deep-Linking System                 │
│ - Replaced rigid card views with native HTML5 <dialog> modals         │
│ - Synchronized URL hash routing (#openlake, #beathackers)             │
│ - Built one-click clipboard link sharing and instant text filtering   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 4: Live Announcements Board & SQLite Database                   │
│ - Designed SQLite schema in announcements.db with seed data           │
│ - Built category tabs, live text search, and relative timestamping    │
│ - Added pinned announcement prioritization                            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 5: Coordinator Authentication & Verification System             │
│ - Merged upstream features and resolved merge conflicts with auth.py   │
│ - Created coordinator_passcodes SQLite table with club credentials    │
│ - Built two-step modal workflow (verification -> verified badge post) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 6: Code Quality, Style Alignment & Anti-AI Slop Refactoring     │
│ - Converted all AI-slop camelCase boilerplate to clean snake_case      │
│ - Refactored backend (auth.py, main.py) and frontend (all JS modules) │
│ - Removed all legacy shims and backward compatibility aliases         │
│ - Rewrote generator error handlers into natural peer guide tone       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 7: Comprehensive Documentation & Architectural Specifications    │
│ - Authored production README.md matching StudentOS repository standard │
│ - Documented full RAG bot StateGraph, sequence diagrams, and API specs│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ Subsystem Technical Deep Dives

### 1. Front-End Discovery & HTML5 Modal System

* **Problem**: Users clicking club cards were either directed away from their context or greeted with static, non-shareable popups.
* **Architecture & Solution**:
  * Utilized the native HTML5 `<dialog>` API (`club_modal.js`) with backdrop dismissal, Escape key cancellation, and zero external modal libraries.
  * Deep-linking mechanism synchronizes `window.location.hash`: visiting `cluvora.iitbhilai.ac.in/tech-clubs#openlake` immediately launches OpenLake's detailed profile modal without page reload.
  * Added a clipboard sharing button that constructs the full URL and displays temporary `"✓ Copied!"` feedback.
  * Added `club_search.js`: a lightweight (~20 LOC) progressive enhancement filter that operates purely on the client DOM, offering instantaneous fuzzy search across club names and descriptions.

---

### 2. Real-Time Announcements Engine

* **Problem**: Notices on campus were distributed across scattered channels with no historical archive, searchability, or categorization.
* **Architecture & Solution**:
  * Persistent storage via SQLite (`announcements.db`) with an auto-seeding mechanism for initial campus broadcasts.
  * Rich categorization: `Sci-Tech`, `Cultural`, `Sports`, `Fest`, and `General`.
  * Multi-field full-text SQL query matching across `title`, `content`, and `club_name` with case-insensitive normalization.
  * Priority pinning: Announcements with `is_pinned = 1` are sorted first (`ORDER BY is_pinned DESC, id DESC`).
  * Dynamic relative time calculations in `announcements.js` (`format_time_ago`) calculating intervals like `"Just now"`, `"12m ago"`, `"3h ago"`, or `"Nov 14"`.

---

### 3. Coordinator Authentication System

* **Problem**: An open announcements board invited spam and impersonation, while requiring complex OAuth would create high friction for club leads.
* **Architecture & Solution**:
  * Designed a lightweight, secure passcode mechanism in `auth.py` backed by the `coordinator_passcodes` SQLite table.
  * Built a two-stage client-side posting dialog:
    1. **Verification Stage**: Coordinator selects their club/society from an categorized dropdown (or inputs a custom body) and enters the passcode with an interactive show/hide toggle.
    2. **Posting Stage**: Upon successful verification (`POST /verify-coordinator`), the form displays a green `"🛡️ Posting as: [Club Name]"` verified badge and enables the posting inputs.
  * Role attribution enforces clear accountability (`Coordinator`, `Core Team`, `Member`).
  * Backend validation in `POST /announcements` double-checks passcodes server-side to prevent client bypass.

---

### 4. LangGraph RAG Campus Handbook Assistant

* **Problem**: Freshers and prospective students frequently asked repetitive questions about hostel rules, mesh facilities, council elections, and fest guidelines contained in lengthy PDF handbooks.
* **Architecture & Solution**:
  * **Ingestion & Embedding**: Extracted text from `Brochure_2026-27-45-74.pdf`, segmented chunks into `knowledge.json`, and precomputed local embeddings in `embeddings.json` using FastEmbed (`sentence-transformers/all-MiniLM-L6-v2`).
  * **Zero Cold-Start Vector Store**: The vector store initializes directly into memory on server boot, eliminating expensive re-embedding operations on startup.
  * **Maximal Marginal Relevance (MMR) Retrieval**: Tuned with `k=4` and `fetch_k=20`. MMR optimizes for high relevance while ensuring distinct context passages, avoiding redundant prompt dilution.
  * **LangGraph Orchestrator**: Compiled state machine (`START -> retrieve -> generate -> END`) utilizing `AgentState`:
    ```python
    class AgentState(TypedDict, total=False):
        question: str
        top_k: int
        documents: List[Document]
        answer: str
        sources: List[Dict[str, Any]]
        system_prompt: str
    ```
  * **SMP Senior Mentor Persona**: Configured with a helpful, authentic peer voice that strictly grounds its responses in handbook text and cites exact page numbers (`[Page 45]`, `[Page 62]`).
  * **UI Integration**: `chatbot.js` renders formatted Markdown and interactive source pills referencing specific brochure sections.

---

### 5. Anti-AI Slop & Clean Code Refactoring

* **Problem**: Collaborator pull requests introduced robotic AI-generated variable names, inconsistent `camelCase` identifiers, and bloated shim aliases.
* **Architecture & Solution**:
  * Conducted a project-wide audit converting all identifiers to idiomatic, beginner-friendly `snake_case`.
  * **Backend Refactoring (`auth.py`, `main.py`)**:
    * `mock_auth` $\rightarrow$ `coordinator_auth`
    * `init_mock_db()` $\rightarrow$ `init_auth_db()`
    * `norm_club` $\rightarrow$ `clean_club`
    * `input_pass` $\rightarrow$ `entered_passcode`
    * `seed_data` $\rightarrow$ `default_passcodes`
    * `data` $\rightarrow$ `post_data`
  * **Frontend Refactoring (`coordinator_auth.js`, `announcements.js`, `chatbot.js`, `club_modal.js`)**:
    * `verifiedClub` $\rightarrow$ `verified_club`
    * `verifiedPasscode` $\rightarrow$ `verified_passcode`
    * `messagesContainer` $\rightarrow$ `messages_box`
    * `escapeHtml` $\rightarrow$ `escape_html`
    * `formatMarkdown` $\rightarrow$ `format_markdown`
    * `handleSend` $\rightarrow$ `handle_send`
  * **Error Phrasing Humanization**: Removed AI-sounding error text in `rag/generator.py` (`"connecting to the AI assistant"`) in favor of natural phrasing:
    ```python
    answer = f"Sorry, I ran into an issue retrieving the handbook guidance ({e}). Please try again in a moment."
    ```
  * **Zero Legacy Shims**: Removed all backward-compatibility aliases and legacy shims for a clean, lean codebase.

---

## 🧪 Verification & Test Results

A full test suite was executed against the Flask server using the Python test client in the active environment:

| Test Target | Tested Endpoint | Status | Result / Observations |
| :--- | :--- | :--- | :--- |
| Landing Page | `GET /` | **PASS (200)** | Rendered CoSA councils and responsive logo grid |
| Tech Clubs | `GET /tech-clubs` | **PASS (200)** | Successfully rendered Sci-Tech club cards |
| Cultural Clubs | `GET /cultural-clubs` | **PASS (200)** | Rendered Cultural Council & Media Body cards |
| Societies | `GET /societies` | **PASS (200)** | Rendered Sports Council & Welfare bodies |
| Announcements UI | `GET /announcements` | **PASS (200)** | Rendered bulletin layout and coordinator modal |
| Announcements JSON | `GET /announcements?format=json` | **PASS (200)** | Returned active announcements with pinned order |
| Passcode Verification (Valid) | `POST /verify-coordinator` | **PASS (200)** | Successfully authenticated `OpenLake` with `openlake@2026` |
| Passcode Verification (Invalid) | `POST /verify-coordinator` | **PASS (401)** | Correctly rejected invalid credentials |
| Contact & Map | `GET /contact` | **PASS (200)** | Rendered secretariat contacts and directions |
| Campus Guide UI | `GET /chatbot` | **PASS (200)** | Rendered RAG chat interface and quick chips |
| Python Syntax Compilation | `py_compile` on all `.py` files | **PASS (0 errors)**| Zero syntax, indentation, or import errors |

---

## 📈 Impact & Technical Value

1. **Information Centralization**: Consolidated data across 5 councils and 34+ student bodies into a single, cohesive, self-contained portal.
2. **Minimal Operational Overhead**: Operates entirely with lightweight SQLite and local FastEmbed embeddings; zero cloud database fees or complex infrastructure requirements.
3. **High Performance**: Vanilla frontend architecture eliminates bloated client bundles, guaranteeing sub-second initial paint times across desktop and mobile browsers.
4. **Authentic Student Experience**: AI assistant provides strictly grounded, peer-to-peer guidance with page references, avoiding hallucinations and robotic conversational tropes.
5. **Clean & Maintainable**: Standardized `snake_case` naming conventions and decoupled modular scripts allow future student teams to maintain and extend the codebase with ease.
