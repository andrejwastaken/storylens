import { CheckCircle2, HelpCircle, TriangleAlert, XCircle } from 'lucide-react'
import type { ClaimOut, Verdict } from '../types'

const VERDICT_META: Record<Verdict, { label: string; icon: typeof CheckCircle2; color: string; bg: string }> = {
  supported: { label: 'Supported', icon: CheckCircle2, color: '#34d399', bg: 'bg-emerald-500/10 border-emerald-500/30' },
  partially_supported: { label: 'Partially supported', icon: TriangleAlert, color: '#fbbf24', bg: 'bg-amber-500/10 border-amber-500/30' },
  unverified: { label: 'Unverified', icon: HelpCircle, color: '#94a3b8', bg: 'bg-slate-500/10 border-slate-500/30' },
  contradicted: { label: 'Contradicted', icon: XCircle, color: '#f87171', bg: 'bg-red-500/10 border-red-500/30' },
}

function domainOf(url: string) {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

export default function ClaimsList({ claims }: { claims: ClaimOut[] }) {
  const sorted = [...claims].sort((a, b) => b.importance - a.importance)

  return (
    <div className="space-y-3">
      {sorted.map((claim) => {
        const meta = VERDICT_META[claim.verdict] ?? VERDICT_META.unverified
        const Icon = meta.icon
        return (
          <div key={claim.id} className={`rounded-xl border p-4 ${meta.bg}`}>
            <div className="flex items-start gap-3">
              <Icon className="mt-0.5 h-5 w-5 shrink-0" style={{ color: meta.color }} />
              <div className="flex-1 space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-medium text-slate-100">{claim.text}</p>
                  <span
                    className="shrink-0 rounded-full border px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide"
                    style={{ color: meta.color, borderColor: meta.color }}
                  >
                    {meta.label}
                  </span>
                </div>
                <p className="text-sm text-slate-400">{claim.explanation}</p>
                <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                  <span>Importance {Math.round(claim.importance)}/100</span>
                  <span>Confidence {Math.round(claim.confidence)}/100</span>
                  {claim.supporting_urls.length > 0 && (
                    <span>
                      Supported by:{' '}
                      {claim.supporting_urls.map((u, i) => (
                        <a
                          key={u}
                          href={u}
                          target="_blank"
                          rel="noreferrer"
                          className="text-emerald-400 hover:underline"
                        >
                          {domainOf(u)}
                          {i < claim.supporting_urls.length - 1 ? ', ' : ''}
                        </a>
                      ))}
                    </span>
                  )}
                  {claim.contradicting_urls.length > 0 && (
                    <span>
                      Contradicted by:{' '}
                      {claim.contradicting_urls.map((u, i) => (
                        <a key={u} href={u} target="_blank" rel="noreferrer" className="text-red-400 hover:underline">
                          {domainOf(u)}
                          {i < claim.contradicting_urls.length - 1 ? ', ' : ''}
                        </a>
                      ))}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
