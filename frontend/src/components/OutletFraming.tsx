import type { OutletFramingOut } from '../types'

const TONE_COLORS: Record<string, string> = {
  neutral: 'text-slate-300 border-slate-600',
  critical: 'text-red-400 border-red-500/40',
  sympathetic: 'text-emerald-400 border-emerald-500/40',
  alarmist: 'text-orange-400 border-orange-500/40',
  supportive: 'text-sky-400 border-sky-500/40',
}

function toneClass(tone: string) {
  return TONE_COLORS[tone.toLowerCase()] ?? 'text-violet-300 border-violet-500/40'
}

export default function OutletFraming({ framing }: { framing: OutletFramingOut[] }) {
  if (framing.length === 0) {
    return <p className="text-sm text-slate-500">No comparable framing details were found across outlets.</p>
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {framing.map((f) => (
        <a
          key={f.url}
          href={f.url}
          target="_blank"
          rel="noreferrer"
          className="block rounded-xl border border-slate-800 bg-slate-900/40 p-4 transition hover:border-violet-500/50"
        >
          <div className="mb-2 flex items-center justify-between gap-2">
            <span className="font-semibold text-slate-100">{f.outlet_name}</span>
            <span className={`rounded-full border px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide ${toneClass(f.tone)}`}>
              {f.tone}
            </span>
          </div>
          <p className="text-sm text-slate-400">{f.framing_summary}</p>
          <p className="mt-2 text-xs text-slate-600">{f.domain}</p>
        </a>
      ))}
    </div>
  )
}
