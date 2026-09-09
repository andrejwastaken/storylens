import axios from 'axios'
import type { StoryProfile } from './types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function analyzeArticle(
  url: string,
  weights?: Record<string, number>,
): Promise<StoryProfile> {
  const { data } = await axios.post<StoryProfile>(
    `${API_BASE_URL}/analyze`,
    { url, weights },
    { timeout: 180_000 },
  )
  return data
}
