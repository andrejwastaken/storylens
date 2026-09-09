# Database schema

PostgreSQL schema (see `backend/app/models.py`). Tables are created via
`Base.metadata.create_all` on startup - no migration tool.

```mermaid
erDiagram
    SOURCES {
        int id PK
        string name
        string domain "unique"
        float reliability_score "0-100 signal, not fact"
        float bias_score "-1.0 left .. 1.0 right"
    }

    ARTICLES {
        int id PK
        string url
        string title
        int source_id FK
        string author
        datetime published_at
        text content
        string content_hash "sha256, used for caching/dedup"
        bool is_primary "true = user-submitted article"
        datetime created_at
    }

    STORIES {
        int id PK
        string canonical_title
        datetime created_at
    }

    CLAIMS {
        int id PK
        int story_id FK
        text text
        float importance "0-100"
    }

    EVIDENCE {
        int id PK
        int claim_id FK
        int article_id FK
        string relationship_type "supported / contradicted / partially_supported / unverified"
        float confidence "0-100"
        text explanation
    }

    ANALYSES {
        int id PK
        int article_id FK
        float trust_score
        float source_score
        float corroboration_score
        float evidence_score
        float consistency_score
        float sensationalism_score
        string bias_label
        float bias_confidence
        float ai_probability "nullable, optional signal"
        json weights_json
        text summary
        json warnings_json
        json reasons_json
        json framing_json
        datetime created_at
    }

    STORY_ARTICLES {
        int story_id FK
        int article_id FK
        float similarity
    }

    SOURCES ||--o{ ARTICLES : "publishes"
    STORIES ||--o{ CLAIMS : "has"
    CLAIMS ||--o{ EVIDENCE : "has"
    ARTICLES ||--o{ EVIDENCE : "cited as"
    ARTICLES ||--o{ ANALYSES : "scored by"
    STORIES ||--o{ STORY_ARTICLES : "groups"
    ARTICLES ||--o{ STORY_ARTICLES : "belongs to"
```

## Notes

- `sources.reliability_score` / `bias_score` are seeded from a small curated
  table (`app/seed_sources.py`, ~40 well-known outlets) and default to a
  neutral 50 / 0.0 for unknown domains. They are directional signals, not
  facts about the outlet.
- `articles.is_primary` distinguishes the user-submitted article from the
  related/corroborating articles fetched via Exa + Firecrawl for the same
  analysis.
- `articles.content_hash` (sha256 of extracted markdown) is used both to
  detect near-duplicate wire-service content and as the cache key for
  skipping redundant API calls on repeat analyses of the same URL.
- `evidence` rows are only created for articles the LLM actually cited as
  supporting or contradicting a specific claim - not every related article
  gets an evidence row for every claim.
