export interface ArticleInfo {
  url: string
  title: string
  author: string | null
  published_at: string | null
  domain: string
  source_name: string
}

export interface ScoreBreakdown {
  source: number
  corroboration: number
  evidence: number
  consistency: number
  sensationalism: number
  anti_sensationalism: number
}

export interface BiasOut {
  label: string
  confidence: number
  explanation: string
}

export type Verdict = 'supported' | 'contradicted' | 'partially_supported' | 'unverified'

export interface ClaimOut {
  id: string
  text: string
  importance: number
  verdict: Verdict
  confidence: number
  supporting_urls: string[]
  contradicting_urls: string[]
  explanation: string
}

export interface RelatedSourceOut {
  url: string
  title: string
  domain: string
  outlet_name: string
  reliability_score: number
}

export interface OutletFramingOut {
  url: string
  outlet_name: string
  domain: string
  framing_summary: string
  tone: string
}

export interface StoryProfile {
  analysis_id: number
  article: ArticleInfo
  summary: string
  trust_score: number
  scores: ScoreBreakdown
  weights_used: Record<string, number>
  bias: BiasOut
  reasons: string[]
  warnings: string[]
  claims: ClaimOut[]
  related_sources: RelatedSourceOut[]
  framing: OutletFramingOut[]
  independent_source_count: number
}

export interface Weights {
  source: number
  corroboration: number
  evidence: number
  consistency: number
  anti_sensationalism: number
}
