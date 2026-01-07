export interface Incident {
  id: string
  title: string
  narrative?: string
  occurred_at: string
  first_seen_at: string
  last_seen_at: string
  lat: number
  lon: number
  location_name?: string
  asset_type?: 'airport' | 'harbor' | 'military' | 'powerplant' | 'bridge' | 'other'
  status: 'active' | 'resolved' | 'unconfirmed' | 'false_positive'
  evidence_score: 1 | 2 | 3 | 4
  verification_status?: 'pending' | 'verified' | 'rejected' | 'auto_verified'
  country: string
  region?: string
  sources: IncidentSource[]
}

export interface IncidentSource {
  source_name?: string
  source_url: string
  source_type: 'police' | 'military' | 'aviation_authority' | 'notam' | 'verified_media' | 'media' | 'news' | 'social' | 'other' | string
  source_title?: string
  source_quote?: string
  published_at?: string
  domain?: string
  trust_weight?: number  // 1-4: 4=Official/Police, 3=Verified Media, 2=Media, 1=Social/Low Trust
}

export interface FilterState {
  minEvidence: number
  country: string
  status: string
  assetType: string | null
  dateRange: 'day' | 'week' | 'month' | 'all'
  searchQuery: string
}

export interface ApiResponse<T> {
  data: T
  error?: string
}