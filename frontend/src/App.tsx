import { useState } from 'react'
import { analyzeArticle } from './api'
import logo from './assets/logo.jpg'
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
    <div className="min-h-screen bg-black">
      <div className="mx-auto max-w-4xl px-4 py-10 sm:py-16">
        <header className="mb-10 text-center">
          <div className="mb-3 inline-flex items-center gap-1.5 rounded-full border border-neutral-800 px-3 py-1 text-xs font-medium text-neutral-500">
            Built at the Cursor Skopje Hackathon
          </div>
          <div className="mb-5 flex items-center justify-center gap-3">
            <img src={logo} alt="StoryLens logo" className="h-10 w-10 rounded-lg object-cover" />
            <h1 className="text-4xl font-semibold text-white sm:text-5xl">
              Story<span className="text-blue-500">Lens</span>
            </h1>
          </div>
          <p className="mx-auto max-w-xl text-neutral-400">
            Paste a news article. Get an evidence-backed Story Profile: how trustworthy it is, what supports it, and
            how other outlets frame the same event.
          </p>
        </header>

        <div className="mb-10">
          <UrlInputForm onSubmit={handleAnalyze} loading={loading} />
          {error && (
            <p className="mt-3 rounded-lg border border-neutral-700 bg-neutral-900 p-3 text-sm text-neutral-200">
              {error}
            </p>
          )}
        </div>

        {loading && <LoadingSteps />}
        {!loading && profile && <StoryProfile profile={profile} />}

        {!loading && !profile && !error && (
          <div className="rounded-2xl border border-dashed border-neutral-800 p-10 text-center text-neutral-500">
            <p>Try a real article URL from Reuters, AP, BBC, or any outlet to see a full Story Profile.</p>
          </div>
        )}

        <footer className="mt-16 text-center text-xs text-neutral-600">
          StoryLens shows signals, not verdicts. It never claims to definitively determine whether something is
          "fake" - trust scores, bias labels, and reliability ratings are directional indicators to support your own
          judgement.
        </footer>
      </div>
    </div>
  )
}

export default App
