import { Check, Minus, TriangleAlert, X } from 'lucide-react'
import type { ClaimOut, Verdict } from '../types'

const VERDICT_META: Record<Verdict, { label: string; icon: typeof Check; color: string; border: string }> = {
  supported: { label: 'Supported', icon: Check, color: '#3b82f6', border: 'border-blue-500/40 bg-blue-500/5' },
  partially_supported: { label: 'Partially supported', icon: TriangleAlert, color: '#93c5fd', border: 'border-neutral-700 bg-neutral-900' },
  unverified: { label: 'Unverified', icon: Minus, color: '#a3a3a3', border: 'border-neutral-800 bg-neutral-950' },
  contradicted: { label: 'Contradicted', icon: X, color: '#e5e5e5', border: 'border-neutral-600 bg-neutral-900' },
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
          <div key={claim.id} className={`rounded-xl border p-4 ${meta.border}`}>
            <div className="flex items-start gap-3">
              <Icon className="mt-0.5 h-5 w-5 shrink-0" style={{ color: meta.color }} />
              <div className="flex-1 space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-medium text-neutral-100">{claim.text}</p>
                  <span
                    className="shrink-0 rounded-full border px-2.5 py-0.5 text-xs font-medium uppercase tracking-wide"
                    style={{ color: meta.color, borderColor: meta.color }}
                  >
                    {meta.label}
                  </span>
                </div>
                <p className="text-sm text-neutral-400">{claim.explanation}</p>
                <div className="flex flex-wrap items-center gap-3 text-xs text-neutral-500">
                  <span>Importance {Math.round(claim.importance)}/100</span>
                  <span>Confidence {Math.round(claim.confidence)}/100</span>
                  {claim.supporting_urls.length > 0 && (
                    <span>
                      Supported by:{' '}
                      {claim.supporting_urls.map((u, i) => (
                        <a key={u} href={u} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">
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
                        <a key={u} href={u} target="_blank" rel="noreferrer" className="text-neutral-300 hover:underline">
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
