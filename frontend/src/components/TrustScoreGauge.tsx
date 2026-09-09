import { scoreColor, scoreLabel } from '../scoring'

interface Props {
  score: number
}

const RADIUS = 72
const STROKE = 10
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

export default function TrustScoreGauge({ score }: Props) {
  const clamped = Math.max(0, Math.min(100, score))
  const offset = CIRCUMFERENCE * (1 - clamped / 100)
  const color = scoreColor(clamped)

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative h-44 w-44">
        <svg width="176" height="176" className="-rotate-90">
          <circle cx="88" cy="88" r={RADIUS} fill="none" stroke="#262626" strokeWidth={STROKE} />
          <circle
            cx="88"
            cy="88"
            r={RADIUS}
            fill="none"
            stroke={color}
            strokeWidth={STROKE}
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.4s ease, stroke 0.4s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-5xl font-semibold text-white">{Math.round(clamped)}</span>
          <span className="text-xs font-medium uppercase tracking-wide text-neutral-500">/ 100</span>
        </div>
      </div>
      <div className="text-center">
        <p className="text-base font-medium text-white">Trust Score</p>
        <p className="text-sm" style={{ color }}>
          {scoreLabel(clamped)}
        </p>
      </div>
    </div>
  )
}
