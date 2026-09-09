import type { OutletFramingOut } from '../types'

export default function OutletFraming({ framing }: { framing: OutletFramingOut[] }) {
  if (framing.length === 0) {
    return <p className="text-sm text-neutral-500">No comparable framing details were found across outlets.</p>
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {framing.map((f) => (
        <a
          key={f.url}
          href={f.url}
          target="_blank"
          rel="noreferrer"
          className="block rounded-xl border border-neutral-800 bg-neutral-950 p-4 transition hover:border-blue-500/50"
        >
          <div className="mb-2 flex items-center justify-between gap-2">
            <span className="font-medium text-neutral-100">{f.outlet_name}</span>
            <span className="rounded-full border border-neutral-700 px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide text-neutral-400">
              {f.tone}
            </span>
          </div>
          <p className="text-sm text-neutral-400">{f.framing_summary}</p>
          <p className="mt-2 text-xs text-neutral-600">{f.domain}</p>
        </a>
      ))}
    </div>
  )
}
