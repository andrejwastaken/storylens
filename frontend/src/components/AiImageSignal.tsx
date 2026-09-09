import { ImageIcon } from 'lucide-react'
import type { AiImageSignalOut } from '../types'

/**
 * Optional feature: soft, heuristic "does the lead image look AI-generated?" signal.
 * Deliberately phrased as a likelihood, never a verdict - see
 * backend/app/services/fal_client.py for why this is an LLM-based estimate
 * rather than a dedicated forensic classifier.
 */
export default function AiImageSignal({ signal }: { signal: AiImageSignalOut }) {
  const pct = Math.round(signal.likelihood)
  return (
    <div className="flex gap-3 rounded-xl border border-neutral-800 bg-neutral-950 p-4">
      <img
        src={signal.image_url}
        alt="Article lead image"
        className="h-20 w-20 shrink-0 rounded-lg object-cover"
        onError={(e) => {
          ;(e.currentTarget as HTMLImageElement).style.display = 'none'
        }}
      />
      <div className="min-w-0 flex-1">
        <div className="mb-1 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-neutral-400">
          <ImageIcon className="h-3.5 w-3.5" />
          Lead image - AI-generation heuristic
        </div>
        <div className="mb-1.5 flex items-center gap-2">
          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-neutral-800">
            <div className="h-full rounded-full bg-blue-500" style={{ width: `${pct}%` }} />
          </div>
          <span className="shrink-0 font-mono text-sm text-neutral-200">{pct}%</span>
        </div>
        <p className="text-xs text-neutral-500">{signal.reasoning || 'No further detail provided.'}</p>
        <p className="mt-1 text-[11px] text-neutral-600">
          A rough LLM-vision estimate, not a forensic verdict - treat as a soft signal only.
        </p>
      </div>
    </div>
  )
}
