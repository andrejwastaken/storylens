import { ExternalLink } from 'lucide-react'
import { scoreColor } from '../scoring'
import type { RelatedSourceOut } from '../types'

export default function RelatedSources({ sources, independentCount }: { sources: RelatedSourceOut[]; independentCount: number }) {
  return (
    <div>
      <p className="mb-3 text-sm text-slate-400">
        Found <span className="font-semibold text-slate-200">{sources.length}</span> related articles, spanning{' '}
        <span className="font-semibold text-slate-200">{independentCount}</span> independent outlet
        {independentCount === 1 ? '' : 's'} (syndicated wire copies are grouped together, not double-counted).
      </p>
      <ul className="space-y-2">
        {sources.map((s) => (
          <li key={s.url}>
            <a
              href={s.url}
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-between gap-3 rounded-lg border border-slate-800 bg-slate-900/40 p-3 transition hover:border-violet-500/50"
            >
              <div className="min-w-0">
                <p className="truncate font-medium text-slate-200">{s.title || s.url}</p>
                <p className="text-xs text-slate-500">
                  {s.outlet_name} · {s.domain}
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <span className="font-mono text-xs" style={{ color: scoreColor(s.reliability_score) }}>
                  {Math.round(s.reliability_score)}
                </span>
                <ExternalLink className="h-3.5 w-3.5 text-slate-600" />
              </div>
            </a>
          </li>
        ))}
      </ul>
    </div>
  )
}
