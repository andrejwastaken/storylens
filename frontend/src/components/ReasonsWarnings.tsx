import { CircleCheck, TriangleAlert } from 'lucide-react'

export default function ReasonsWarnings({ reasons, warnings }: { reasons: string[]; warnings: string[] }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
        <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-emerald-400">Why this score</h3>
        <ul className="space-y-2">
          {reasons.length === 0 && <li className="text-sm text-slate-500">No strong positive signals found.</li>}
          {reasons.map((r) => (
            <li key={r} className="flex items-start gap-2 text-sm text-slate-300">
              <CircleCheck className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
              {r}
            </li>
          ))}
        </ul>
      </div>
      <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
        <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-amber-400">Warnings &amp; unverified</h3>
        <ul className="space-y-2">
          {warnings.length === 0 && <li className="text-sm text-slate-500">No notable warnings.</li>}
          {warnings.map((w) => (
            <li key={w} className="flex items-start gap-2 text-sm text-slate-300">
              <TriangleAlert className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
              {w}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
