import { useRef } from 'react'

interface Props {
  value: number
  onChange: (value: number) => void
}

/**
 * Custom weight control - deliberately not a native <input type="range">.
 * Supports three equally reliable interactions: +/- buttons (step 5),
 * click-anywhere-on-track to jump, and press-and-drag. This avoids
 * cross-browser/automation quirks with native range inputs.
 */
export default function WeightSlider({ value, onChange }: Props) {
  const trackRef = useRef<HTMLDivElement | null>(null)

  const setFromClientX = (clientX: number) => {
    const el = trackRef.current
    if (!el) return
    const rect = el.getBoundingClientRect()
    const pct = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width))
    onChange(Math.round(pct * 100))
  }

  const handlePointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    e.preventDefault()
    setFromClientX(e.clientX)
    const handleMove = (ev: PointerEvent) => setFromClientX(ev.clientX)
    const handleUp = () => {
      window.removeEventListener('pointermove', handleMove)
      window.removeEventListener('pointerup', handleUp)
    }
    window.addEventListener('pointermove', handleMove)
    window.addEventListener('pointerup', handleUp)
  }

  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        aria-label="Decrease weight"
        onClick={() => onChange(Math.max(0, value - 5))}
        className="flex h-6 w-6 shrink-0 items-center justify-center rounded border border-neutral-700 text-neutral-400 transition hover:border-blue-500 hover:text-blue-400"
      >
        −
      </button>
      <div
        ref={trackRef}
        onPointerDown={handlePointerDown}
        role="slider"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={value}
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'ArrowRight' || e.key === 'ArrowUp') onChange(Math.min(100, value + 5))
          if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') onChange(Math.max(0, value - 5))
        }}
        className="relative h-1.5 flex-1 cursor-pointer rounded-full bg-neutral-800 outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40"
      >
        <div className="absolute inset-y-0 left-0 rounded-full bg-blue-500" style={{ width: `${value}%` }} />
        <div
          className="absolute top-1/2 h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-blue-500 bg-white shadow"
          style={{ left: `${value}%` }}
        />
      </div>
      <button
        type="button"
        aria-label="Increase weight"
        onClick={() => onChange(Math.min(100, value + 5))}
        className="flex h-6 w-6 shrink-0 items-center justify-center rounded border border-neutral-700 text-neutral-400 transition hover:border-blue-500 hover:text-blue-400"
      >
        +
      </button>
      <span className="w-14 shrink-0 text-right font-mono text-xs text-neutral-500">{value}%</span>
    </div>
  )
}
