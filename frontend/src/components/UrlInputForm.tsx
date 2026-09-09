import { Search } from 'lucide-react'
import { useState } from 'react'

interface Props {
  onSubmit: (url: string) => void
  loading: boolean
}

export default function UrlInputForm({ onSubmit, loading }: Props) {
  const [url, setUrl] = useState('')

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        if (url.trim()) onSubmit(url.trim())
      }}
      className="flex w-full flex-col gap-3 sm:flex-row"
    >
      <div className="relative flex-1">
        <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-neutral-500" />
        <input
          type="url"
          required
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste a news article URL, e.g. https://www.reuters.com/..."
          className="w-full rounded-lg border border-neutral-700 bg-neutral-950 py-3.5 pl-12 pr-4 text-white placeholder-neutral-500 outline-none transition focus:border-blue-500"
        />
      </div>
      <button
        type="submit"
        disabled={loading || !url.trim()}
        className="shrink-0 rounded-lg bg-blue-600 px-6 py-3.5 font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {loading ? 'Analyzing…' : 'Analyze'}
      </button>
    </form>
  )
}
