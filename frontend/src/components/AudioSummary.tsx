import { Volume2 } from 'lucide-react'
import { useState } from 'react'
import { audioSummaryUrl } from '../api'

/**
 * P2: ~30s spoken summary via ElevenLabs. Lazily loaded - nothing is
 * requested from the backend until the user clicks Listen. Fails silently
 * (hides itself) if audio summaries aren't configured on the backend.
 */
export default function AudioSummary({ analysisId, available }: { analysisId: number; available: boolean }) {
  const [started, setStarted] = useState(false)
  const [failed, setFailed] = useState(false)

  if (!available || failed) return null

  if (!started) {
    return (
      <button
        type="button"
        onClick={() => setStarted(true)}
        className="inline-flex items-center gap-1.5 rounded-md border border-neutral-700 px-3 py-1.5 text-xs font-medium text-neutral-300 transition hover:border-blue-500 hover:text-blue-400"
      >
        <Volume2 className="h-3.5 w-3.5" />
        Listen to summary
      </button>
    )
  }

  return (
    <audio
      controls
      autoPlay
      preload="auto"
      src={audioSummaryUrl(analysisId)}
      onError={() => setFailed(true)}
      className="h-9 max-w-full"
    >
      Your browser does not support audio playback.
    </audio>
  )
}
