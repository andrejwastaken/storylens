import { Circle, TriangleAlert } from 'lucide-react'

export default function ReasonsWarnings({ reasons, warnings }: { reasons: string[]; warnings: string[] }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <div className="rounded-xl border border-neutral-800 bg-neutral-950 p-4">
        <h3 className="mb-2 text-sm font-medium uppercase tracking-wide text-blue-400">Why this score</h3>
        <ul className="space-y-2">
          {reasons.length === 0 && <li className="text-sm text-neutral-500">No strong positive signals found.</li>}
          {reasons.map((r) => (
            <li key={r} className="flex items-start gap-2 text-sm text-neutral-300">
              <Circle className="mt-1 h-2 w-2 shrink-0 fill-blue-400 text-blue-400" />
              {r}
            </li>
          ))}
        </ul>
      </div>
      <div className="rounded-xl border border-neutral-800 bg-neutral-950 p-4">
        <h3 className="mb-2 text-sm font-medium uppercase tracking-wide text-neutral-400">Warnings &amp; unverified</h3>
        <ul className="space-y-2">
          {warnings.length === 0 && <li className="text-sm text-neutral-500">No notable warnings.</li>}
          {warnings.map((w) => (
            <li key={w} className="flex items-start gap-2 text-sm text-neutral-300">
              <TriangleAlert className="mt-0.5 h-4 w-4 shrink-0 text-neutral-500" />
              {w}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
