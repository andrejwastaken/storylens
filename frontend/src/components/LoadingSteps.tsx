import { useEffect, useState } from 'react'

const STEPS = [
  'Extracting article with Firecrawl…',
  'Reading claims, tone & framing with the LLM…',
  'Searching the web for independent coverage with Exa…',
  'Extracting related articles…',
  'Comparing evidence across sources…',
  'Computing the deterministic Trust Score…',
]

export default function LoadingSteps() {
  const [step, setStep] = useState(0)

  useEffect(() => {
    const id = setInterval(() => {
      setStep((s) => Math.min(s + 1, STEPS.length - 1))
    }, 2600)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="flex flex-col items-center gap-6 rounded-2xl border border-slate-800 bg-slate-900/40 px-8 py-14 text-center">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-700 border-t-violet-500" />
      <div className="space-y-2">
        {STEPS.map((label, i) => (
          <p
            key={label}
            className={
              i === step
                ? 'font-medium text-slate-100 transition'
                : i < step
                  ? 'text-sm text-emerald-500/80 transition'
                  : 'text-sm text-slate-600 transition'
            }
          >
            {i < step ? '✓ ' : ''}
            {label}
          </p>
        ))}
      </div>
      <p className="text-xs text-slate-500">This can take up to a minute - we're reading multiple full articles.</p>
    </div>
  )
}
