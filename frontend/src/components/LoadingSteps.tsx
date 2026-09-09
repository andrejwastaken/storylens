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
    <div className="flex flex-col items-center gap-6 rounded-xl border border-neutral-800 bg-neutral-950 px-8 py-14 text-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-neutral-700 border-t-blue-500" />
      <div className="space-y-2">
        {STEPS.map((label, i) => (
          <p
            key={label}
            className={
              i === step
                ? 'font-medium text-white transition'
                : i < step
                  ? 'flex items-center justify-center gap-2 text-sm text-blue-400/70 transition'
                  : 'text-sm text-neutral-600 transition'
            }
          >
            {i < step && <span className="inline-block h-1 w-1 rounded-full bg-blue-400" />}
            {label}
          </p>
        ))}
      </div>
      <p className="text-xs text-neutral-500">This can take up to a minute - we're reading multiple full articles.</p>
    </div>
  )
}
