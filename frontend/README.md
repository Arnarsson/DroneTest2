# DroneWatch Frontend

Modern, responsive frontend for real-time drone incident tracking.

## 🚀 Features

- **Interactive Map** with clustering
- **Real-time Updates** via React Query
- **Advanced Filters** (evidence, country, time, location type)
- **List View** alternative to map
- **Embed Mode** for newsroom integration
- **Mobile Optimized** (<2s load time)
- **TypeScript** for type safety

## 📦 Tech Stack

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Leaflet** for mapping
- **React Query** for data fetching
- **date-fns** for date formatting

## 🛠️ Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=https://your-api.vercel.app/api
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## 🚀 Deployment

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Or link to GitHub for auto-deploy
```

### Environment Variables (Vercel)

Add in Vercel Dashboard:
- `NEXT_PUBLIC_API_URL` - Your API endpoint

## 📱 Features

### Map View
- Clustered markers for performance
- Color-coded by evidence level
- Popup with incident details
- Auto-zoom to incidents

### List View
- Sortable incident cards
- Quick source links
- Time and location info

### Filters
- **Evidence Level**: 1-4 scale
- **Country**: DK, NO, SE, FI
- **Status**: Active, Resolved, Unconfirmed
- **Location Type**: Airport, Harbor, Military, etc.
- **Time Range**: 24h, Week, Month, All

### Embed Mode

Newsrooms can embed the map:

```html
<iframe
  src="https://dronewatch.cc/embed?minEvidence=3&country=DK"
  width="100%"
  height="500"
  frameborder="0"
></iframe>
```

Parameters:
- `minEvidence` - Minimum evidence score (1-4)
- `country` - Country code
- `status` - Incident status
- `assetType` - Location type

## 🎨 Customization

### Evidence Colors

Edit in `tailwind.config.ts`:
```js
colors: {
  'evidence-4': '#dc2626', // Official - red
  'evidence-3': '#ea580c', // Verified - orange
  'evidence-2': '#facc15', // OSINT - yellow
  'evidence-1': '#9ca3af', // Unverified - gray
}
```

### Map Tiles

Default uses OpenStreetMap. For better tiles, add Mapbox:

1. Get token from [mapbox.com](https://mapbox.com)
2. Add to `.env.local`:
   ```
   NEXT_PUBLIC_MAPBOX_TOKEN=your-token
   ```
3. Update Map component to use Mapbox tiles

## 📊 Performance

- **Bundle Size**: ~200KB gzipped
- **First Load**: <2s on 4G
- **TTI**: <3s on mid-tier mobile
- **Lighthouse Score**: 90+

## 🧪 Testing

```bash
# Type checking
npm run type-check

# Build test
npm run build

# Production preview
npm run start
```

## 📁 Structure

```
frontend/
├── app/              # Next.js app router
│   ├── layout.tsx    # Root layout
│   ├── page.tsx      # Home page
│   └── embed/        # Embed mode
├── components/       # React components
│   ├── Map.tsx       # Leaflet map
│   ├── Filters.tsx   # Filter controls
│   └── Header.tsx    # App header
├── hooks/            # Custom hooks
│   └── useIncidents.ts
├── types/            # TypeScript types
└── public/           # Static assets
```

## 🐛 Troubleshooting

### Map not loading
- Check API URL in `.env.local`
- Verify API is returning data
- Check browser console for errors

### Markers not showing
- Ensure incidents have valid lat/lon
- Check evidence filter isn't too restrictive

### Slow performance
- Reduce `limit` in API call
- Enable marker clustering
- Use production build

## 🔄 Updates

The app auto-refreshes every 60 seconds. Adjust in `providers.tsx`:

```typescript
refetchInterval: 60 * 1000 // milliseconds
```