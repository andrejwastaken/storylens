import { Info } from 'lucide-react'
import type { ArticleInfo, BiasOut } from '../types'

const BIAS_POSITION: Record<string, number> = {
  left: 8,
  'center-left': 30,
  center: 50,
  'center-right': 70,
  right: 92,
  unclear: 50,
}

export default function ArticleHeader({ article, bias }: { article: ArticleInfo; bias: BiasOut }) {
  const pos = BIAS_POSITION[bias.label] ?? 50
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <a
          href={article.url}
          target="_blank"
          rel="noreferrer"
          className="text-xl font-semibold text-white hover:underline"
        >
          {article.title}
        </a>
      </div>
      <p className="text-sm text-slate-400">
        {article.source_name} ({article.domain})
        {article.author ? ` · ${article.author}` : ''}
        {article.published_at ? ` · ${new Date(article.published_at).toLocaleDateString()}` : ''}
      </p>

      <div className="max-w-xs rounded-lg border border-slate-800 bg-slate-900/40 p-3">
        <div className="mb-1.5 flex items-center justify-between text-xs text-slate-400">
          <span>Political framing signal</span>
          <span className="font-medium capitalize text-slate-200">
            {bias.label} ({Math.round(bias.confidence)}% confidence)
          </span>
        </div>
        <div className="relative h-1.5 rounded-full bg-gradient-to-r from-sky-500 via-slate-500 to-red-500">
          <div
            className="absolute -top-1 h-3.5 w-3.5 -translate-x-1/2 rounded-full border-2 border-slate-950 bg-white shadow"
            style={{ left: `${pos}%` }}
          />
        </div>
        <div className="mt-1 flex justify-between text-[10px] text-slate-600">
          <span>Left</span>
          <span>Center</span>
          <span>Right</span>
        </div>
      </div>

      <p className="flex items-start gap-1.5 text-xs text-slate-600">
        <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" />
        Source reputation and framing are directional signals based on a small curated outlet list and LLM
        judgement - not objective facts about this outlet or article.
      </p>
    </div>
  )
}
