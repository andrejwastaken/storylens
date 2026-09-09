import type { ScoreBreakdown, Weights } from './types'

export function scoreColor(score: number): string {
  if (score >= 80) return '#34d399' // emerald-400
  if (score >= 60) return '#fbbf24' // amber-400
  return '#f87171' // red-400
}

export function scoreLabel(score: number): string {
  if (score >= 80) return 'High trust signal'
  if (score >= 60) return 'Moderate trust signal'
  if (score >= 40) return 'Low trust signal'
  return 'Very low trust signal'
}

export const DEFAULT_WEIGHTS: Weights = {
  source: 25,
  corroboration: 30,
  evidence: 25,
  consistency: 10,
  anti_sensationalism: 10,
}

/**
 * Mirrors the exact weighted-sum formula in backend/app/scoring.py so moving
 * a slider recomputes the Trust Score instantly client-side, without a
 * network round trip. The underlying sub-scores (source, corroboration,
 * evidence, consistency, sensationalism) are still computed once by the
 * deterministic backend engine - this only recombines them.
 */
export function recomputeTrustScore(scores: ScoreBreakdown, weights: Weights): number {
  const total = weights.source + weights.corroboration + weights.evidence + weights.consistency + weights.anti_sensationalism
  if (total <= 0) return 0
  const w = {
    source: weights.source / total,
    corroboration: weights.corroboration / total,
    evidence: weights.evidence / total,
    consistency: weights.consistency / total,
    anti_sensationalism: weights.anti_sensationalism / total,
  }
  const score =
    w.source * scores.source +
    w.corroboration * scores.corroboration +
    w.evidence * scores.evidence +
    w.consistency * scores.consistency +
    w.anti_sensationalism * scores.anti_sensationalism
  return Math.round(score * 10) / 10
}
