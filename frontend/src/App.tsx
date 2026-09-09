import { useState } from 'react'
import { analyzeArticle } from './api'
import LoadingSteps from './components/LoadingSteps'
import StoryProfile from './components/StoryProfile'
import UrlInputForm from './components/UrlInputForm'
import type { StoryProfile as StoryProfileType } from './types'

function App() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [profile, setProfile] = useState<StoryProfileType | null>(null)

  async function handleAnalyze(url: string) {
    setLoading(true)
    setError(null)
    setProfile(null)
    try {
      const result = await analyzeArticle(url)
      setProfile(result)
    } catch (err) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (err instanceof Error ? err.message : 'Something went wrong analyzing this article.')
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#1e1b3a,_#0b0d12_60%)]">
      <div className="mx-auto max-w-4xl px-4 py-10 sm:py-16">
        <header className="mb-10 text-center">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-4 py-1 text-xs font-medium text-violet-300">
            Built at the Cursor Skopje Hackathon
          </div>
          <h1 className="text-4xl font-bold text-white sm:text-5xl">
            Story<span className="text-violet-400">Lens</span>
          </h1>
          <p className="mx-auto mt-3 max-w-xl text-slate-400">
            Paste a news article. Get an evidence-backed Story Profile: how trustworthy it is, what supports it, and
            how other outlets frame the same event.
          </p>
        </header>

        <div className="mb-10">
          <UrlInputForm onSubmit={handleAnalyze} loading={loading} />
          {error && (
            <p className="mt-3 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">
              {error}
            </p>
          )}
        </div>

        {loading && <LoadingSteps />}
        {!loading && profile && <StoryProfile profile={profile} />}

        {!loading && !profile && !error && (
          <div className="rounded-2xl border border-dashed border-slate-800 p-10 text-center text-slate-500">
            <p>Try a real article URL from Reuters, AP, BBC, or any outlet to see a full Story Profile.</p>
          </div>
        )}

        <footer className="mt-16 text-center text-xs text-slate-600">
          StoryLens shows signals, not verdicts. It never claims to definitively determine whether something is
          "fake" - trust scores, bias labels, and reliability ratings are directional indicators to support your own
          judgement.
        </footer>
      </div>
    </div>
  )
}

export default App
