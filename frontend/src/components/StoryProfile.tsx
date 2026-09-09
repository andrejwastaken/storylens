import { useMemo, useState } from 'react'
import { DEFAULT_WEIGHTS, recomputeTrustScore } from '../scoring'
import type { StoryProfile as StoryProfileType, Weights } from '../types'
import ArticleHeader from './ArticleHeader'
import ClaimsList from './ClaimsList'
import OutletFraming from './OutletFraming'
import RelatedSources from './RelatedSources'
import ReasonsWarnings from './ReasonsWarnings'
import SubscoreBars from './SubscoreBars'
import TrustScoreGauge from './TrustScoreGauge'

function initialWeights(weightsUsed: Record<string, number>): Weights {
  return {
    source: Math.round((weightsUsed.source ?? 0.25) * 100),
    corroboration: Math.round((weightsUsed.corroboration ?? 0.3) * 100),
    evidence: Math.round((weightsUsed.evidence ?? 0.25) * 100),
    consistency: Math.round((weightsUsed.consistency ?? 0.1) * 100),
    anti_sensationalism: Math.round((weightsUsed.anti_sensationalism ?? 0.1) * 100),
  }
}

export default function StoryProfile({ profile }: { profile: StoryProfileType }) {
  const [weights, setWeights] = useState<Weights>(() => initialWeights(profile.weights_used))
  const [editingWeights, setEditingWeights] = useState(false)

  const liveTrustScore = useMemo(() => recomputeTrustScore(profile.scores, weights), [profile.scores, weights])

  return (
    <div className="space-y-8">
      <section className="rounded-2xl border border-slate-800 bg-slate-900/30 p-6">
        <ArticleHeader article={profile.article} bias={profile.bias} />
      </section>

      <section className="grid gap-8 rounded-2xl border border-slate-800 bg-slate-900/30 p-6 lg:grid-cols-[220px_1fr]">
        <div className="flex flex-col items-center justify-center">
          <TrustScoreGauge score={liveTrustScore} />
        </div>
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Score breakdown</h2>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setEditingWeights((v) => !v)}
                className="rounded-lg border border-slate-700 px-3 py-1 text-xs font-medium text-slate-300 transition hover:border-violet-500 hover:text-violet-300"
              >
                {editingWeights ? 'Done adjusting' : 'Adjust weights'}
              </button>
              {editingWeights && (
                <button
                  type="button"
                  onClick={() => setWeights(DEFAULT_WEIGHTS)}
                  className="rounded-lg border border-slate-700 px-3 py-1 text-xs font-medium text-slate-400 transition hover:border-slate-500"
                >
                  Reset
                </button>
              )}
            </div>
          </div>
          <SubscoreBars scores={profile.scores} weights={weights} onWeightsChange={setWeights} editable={editingWeights} />
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/30 p-6">
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-400">Summary</h2>
        <p className="text-slate-300">{profile.summary}</p>
      </section>

      <section>
        <ReasonsWarnings reasons={profile.reasons} warnings={profile.warnings} />
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/30 p-6">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-400">
          Key claims &amp; evidence ({profile.claims.length})
        </h2>
        <ClaimsList claims={profile.claims} />
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/30 p-6">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-400">How other outlets frame this story</h2>
        <OutletFraming framing={profile.framing} />
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/30 p-6">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-400">Related sources</h2>
        <RelatedSources sources={profile.related_sources} independentCount={profile.independent_source_count} />
      </section>
    </div>
  )
}
