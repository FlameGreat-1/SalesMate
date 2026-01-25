# SalesMate Docs


**Deployment:** Railway (Frontend & Backend)  
**Scale:** Currently handling 65 products (40+ attributes each) with architecture supporting 5,000+.


## **ARCHITECTURE**

┌─────────────────────────────────────────────────────────────────┐
│                      USER BROWSER (Frontend)                    │
│                    (Next.js React Application)                  │
└────────────────────────────────┬────────────────────────────────┘
                                 │ HTTP/REST API
                                 │
┌────────────────────────────────▼───────────────────────────────┐
│                        BACKEND SERVER                          │
│                    (FastAPI Python Application)                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Authentication & Authorization                         │  │
│  │ • Conversation Management                                │  │
│  │ • Intent Analysis (AI)                                   │  │
│  │ • Product Search & Recommendation Engine                 │  │
│  │ • LLM Integration (OpenAI/Gemini)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────┬───────────────────────┬─────────────────── ┬──────────┘ 
         │                       │                    │
    ┌────▼─────┐    ┌────────────▼────────┐  ┌────────▼────────┐
    │ Supabase │    │  Pinecone Vector DB │  │  LLM Services   │
    │PostgreSQL│    │ (Product Embeddings)│  │(OpenAI/Gemini)  │
    └──────────┘    └─────────────────────┘  └─────────────────┘


## **The Technology Stack**

### **Core Infrastructure**
- **Hosting:** **Railway** (Containerized orchestration for both Next.js Frontend and Python Backend).
- **Frontend:** **Next.js** (React) with Server-Sent Events (SSE) for real-time streaming interfaces.
- **Backend:** **Python (FastAPI) + Uvicorn** orchestrating the AI logic and data flow.

### **The AI & Data Layer**
- **Vector Database:** **Pinecone**. Stores product "embeddings" to allow the AI to search by *concept* rather than just *keyword*.
- **Embedding Model:** **Sentence Transformer (all-MiniLM-L6-v2)**. This converts product text into mathematical vectors that capture semantic meaning.
- **Relational Database:** **Supabase (PostgreSQL)**. Manages hard data: Product catalog, User Profiles, Messages, and Conversation logs.
- **LLM Engine:** Hybrid integration of **OpenAI & Gemini AI**, dynamically selected based on configuration/cost optimization.
- **Streaming:** **SSE (Server-Sent Events)** ensures the user sees the response *typing out* in real-time, reducing perceived latency to near zero.


## **The Challenge**

LLM hallucination due to lack of access to complete product details. 
 Feeding all products (with 40+ attributes each) plus user history into every single AI request leads to:
1.  **Enormous Token Consumption:** Costs would skyrocket to ~$0.50+ per message.
2.  **High Latency:** Waiting 10+ seconds for a response.
3.  **Confusion:** The AI gets overwhelmed by irrelevant data and starts "hallucinating" (making things up).

**The Solution: The 2-Tier Context System**
I implemented a proprietary context management flow that solves this tradeoff:

### **Tier 1: Global Awareness (The "Store Directory")**
*   **What it is:** A lightweight summary of **EVERY** product in our inventory.
*   **Role:** Ensures the AI knows *everything* we sell at a high level.

### **Tier 2: Deep Focus (The "Specification Sheet")**
*   **What it is:** Hyper-detailed technical data, but **ONLY** for the 3-5 products actually relevant to the current user query.
*   **Role:** Dynamically loaded via **Pinecone Vector Search** + Metadata Filtering.


### **Scalability**
*   The architecture decouples the *size of the catalog* from the *size of the prompt*.
*   We can scale from 65 products to 5,000+ products with **zero impact** on LLM latency or per-message cost, as Pinecone handles the retrieval heavy lifting.


## 🔄 End-to-End Data Flow

1.  **User Input:** User types "I need a AI and machine learning laptop under $3,000"
2.  **Intent Analysis:** LLM ascertains intent ("Browsing" + "Constraint: <$3,000").
3.  **Vector Retrieval:**
    *   Sentence Transformer converts query to vector.
    *   Pinecone searches 65 products for semantic matches.
    *   Metadata filters apply hard constraint (Price < $3,000).
4.  **Context Construction (The 2-Tier assembly):**
    *   System loads **Tier 1** (All products summary).
    *   System injects **Tier 2** (Full specs for the top 5 matches).
5.  **Generation:** LLM generates response using this hybrid context.
6.  **Streaming:** Response flows to the user via SSE in real-time.


## **DATA FLOW DIAGRAM**

┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Browser)                       │
│              User Types → Send Message                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ HTTP POST with JWT Token
                   ▼
┌──────────────────────────────────────────────────────────────┐
│                  BACKEND API SERVER                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 1. Authenticate user (validate JWT token)              │  │
│  │ 2. Store message in database                           │  │
│  │ 3. Analyze intent (call LLM)                           │  │
│  │ 4. Extract entities (products, categories, budget)     │  │
│  │ 5. Search products (vector DB + traditional filters)   │  │
│  │ 6. Rank recommendations (budget, preferences, scores)  │  │
│  │ 7. Prepare context (history, products, user profile)   │  │
│  │ 8. Generate AI response (call LLM)                     │  │
│  │ 9. Stream response back to frontend                    │  │
│  │ 10. Store assistant message in database                │  │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
   ┌────────┐ ┌──────────┐ ┌──────────┐
   │ Supabase│ │Pinecone │ │LLM APIs  │
   │Database │ │Vector DB│ │(Gemini/  │
   │(Postgres)│ │(Search)  │ │OpenAI) │
   └────────┘ └──────────┘ └──────────┘
        │          │          │
        └──────────┼──────────┘
                   │
        ┌──────────▼────────── ┐
        │ Stream Response Back │
        │ to Frontend (SSE)    │
        └───────────────────── ┘
                   │
                   │ Real-time streaming
                   ▼
   ┌──────────────────────────────┐
   │  FRONTEND Display            │
   │ ├─ AI response text          │
   │ ├─ Product recommendations   │
   │ ├─ Key specifications        │
   │ └─ Interactive buttons       │
   └──────────────────────────────┘