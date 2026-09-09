# Architecture

High-level system architecture for StoryLens.

```mermaid
graph TB
    subgraph Client
        FE["React + Tailwind Frontend<br/>(Vite, Netlify)"]
    end

    subgraph Server["FastAPI Backend (Render)"]
        API["POST /analyze<br/>orchestration router"]
        LLM_ABS["LLMProvider abstraction"]
        SCORE["Deterministic Scoring Engine<br/>(app/scoring.py)"]
    end

    subgraph External["External Services"]
        FIRECRAWL["Firecrawl API<br/>article extraction"]
        EXA["Exa API<br/>independent source search"]
        OPENAI["OpenAI API<br/>GPT-5.6 Sol (structured outputs)"]
    end

    subgraph Data["Data Layer"]
        PG[("PostgreSQL<br/>sources / articles / stories /<br/>claims / evidence / analyses")]
    end

    FE -- "HTTP JSON" --> API
    API -- "1. scrape URL" --> FIRECRAWL
    API -- "2. extract claims + signals" --> LLM_ABS
    LLM_ABS --> OPENAI
    API -- "3. search independent coverage" --> EXA
    API -- "4. scrape related articles" --> FIRECRAWL
    API -- "5. compare evidence + framing" --> LLM_ABS
    API -- "6. combine signals" --> SCORE
    API -- "persist" --> PG
    API -- "Story Profile JSON" --> FE

    style FE fill:#0b0d12,stroke:#3b82f6,color:#fff
    style API fill:#0b0d12,stroke:#3b82f6,color:#fff
    style SCORE fill:#0b0d12,stroke:#3b82f6,color:#fff
    style LLM_ABS fill:#0b0d12,stroke:#525252,color:#fff
    style PG fill:#0b0d12,stroke:#525252,color:#fff
    style FIRECRAWL fill:#0b0d12,stroke:#525252,color:#fff
    style EXA fill:#0b0d12,stroke:#525252,color:#fff
    style OPENAI fill:#0b0d12,stroke:#525252,color:#fff
```

## Key design decisions

- **The LLM never outputs the final Trust Score.** It only produces sub-signals
  (headline consistency, sensationalism, per-claim verdicts + confidence, bias
  label). `app/scoring.py` is plain, deterministic Python that combines those
  signals with source-reputation priors using a transparent, configurable
  weighted formula.
- **`LLMProvider` is an abstract interface** (`app/services/llm/base.py`) so the
  OpenAI implementation can be swapped for another hosted provider (or a local
  Ollama model later) without touching the rest of the app.
- **No Docker.** Backend runs directly via `uvicorn`, frontend via `npm run dev`
  / static build. Kept deliberately simple.
