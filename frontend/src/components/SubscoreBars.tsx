import { scoreColor } from '../scoring'
import type { ScoreBreakdown, Weights } from '../types'

interface Row {
  key: keyof ScoreBreakdown
  weightKey: keyof Weights
  label: string
  helpText: string
}

const ROWS: Row[] = [
  { key: 'source', weightKey: 'source', label: 'Source reputation', helpText: 'Editorial track-record signal for the outlet, not objective truth.' },
  { key: 'corroboration', weightKey: 'corroboration', label: 'Corroboration', helpText: 'Independent outlets covering this story (wire-service copies do not count as independent).' },
  { key: 'evidence', weightKey: 'evidence', label: 'Evidence quality', helpText: 'How well the important claims hold up against independent coverage.' },
  { key: 'consistency', weightKey: 'consistency', label: 'Headline consistency', helpText: 'Does the headline accurately represent the article body?' },
  { key: 'anti_sensationalism', weightKey: 'anti_sensationalism', label: 'Sensationalism', helpText: 'Higher = calmer, less emotionally-manipulative language.' },
]

interface Props {
  scores: ScoreBreakdown
  weights: Weights
  onWeightsChange: (w: Weights) => void
  editable: boolean
}

export default function SubscoreBars({ scores, weights, onWeightsChange, editable }: Props) {
  return (
    <div className="space-y-5">
      {ROWS.map((row) => {
        const value = scores[row.key]
        const weight = weights[row.weightKey]
        return (
          <div key={row.key}>
            <div className="mb-1.5 flex items-baseline justify-between gap-3">
              <div>
                <span className="font-medium text-slate-200">{row.label}</span>
                <span className="ml-2 text-xs text-slate-500">{row.helpText}</span>
              </div>
              <span className="shrink-0 font-mono text-sm font-semibold" style={{ color: scoreColor(value) }}>
                {Math.round(value)}
              </span>
            </div>
            <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-800">
              <div
                className="h-full rounded-full transition-all"
                style={{ width: `${Math.max(0, Math.min(100, value))}%`, background: scoreColor(value) }}
              />
            </div>
            {editable && (
              <div className="mt-1.5 flex items-center gap-2">
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={weight}
                  onChange={(e) => onWeightsChange({ ...weights, [row.weightKey]: Number(e.target.value) })}
                  className="h-1 flex-1 cursor-pointer accent-violet-500"
                />
                <span className="w-16 shrink-0 text-right text-xs text-slate-500">weight {weight}%</span>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
