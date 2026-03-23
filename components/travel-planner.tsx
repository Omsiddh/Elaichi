"use client"

import { Plane, MapPin, Compass } from "lucide-react"
import CrewApiForm from "./crew-api-form"

export default function TravelPlanner() {
  // These will be provided via environment variables later
  const baseUrl = process.env.NEXT_PUBLIC_CREW_API_URL || ""
  const bearerToken = process.env.NEXT_PUBLIC_CREW_BEARER_TOKEN || ""

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary">
              <Plane className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-foreground">Travel Planner</h1>
              <p className="text-sm text-muted-foreground">AI-powered trip planning</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-foreground mb-3 text-balance">
              Plan Your Perfect Trip
            </h2>
            <p className="text-muted-foreground text-lg">
              Let our AI crew handle the research and planning for your next adventure.
            </p>
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <div className="flex items-start gap-3 p-4 rounded-lg border border-border bg-card">
              <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-secondary">
                <MapPin className="w-5 h-5 text-secondary-foreground" />
              </div>
              <div>
                <h3 className="font-medium text-foreground">Destination Research</h3>
                <p className="text-sm text-muted-foreground">
                  Get insights on locations, weather, and local attractions.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 rounded-lg border border-border bg-card">
              <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-secondary">
                <Compass className="w-5 h-5 text-secondary-foreground" />
              </div>
              <div>
                <h3 className="font-medium text-foreground">Smart Itineraries</h3>
                <p className="text-sm text-muted-foreground">
                  Receive personalized day-by-day travel plans.
                </p>
              </div>
            </div>
          </div>

          {/* Crew API Form */}
          <div className="rounded-xl border border-border bg-card overflow-hidden">
            <div className="px-6 py-4 border-b border-border">
              <h3 className="font-semibold text-foreground">Start Planning</h3>
              <p className="text-sm text-muted-foreground">
                Click the button below to activate the AI travel crew.
              </p>
            </div>
            <div className="p-6">
              {baseUrl && bearerToken ? (
                <CrewApiForm
                  baseUrl={baseUrl}
                  bearerToken={bearerToken}
                  className="!p-0 !bg-transparent !shadow-none"
                />
              ) : (
                <div className="text-center py-8">
                  <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-muted mb-4">
                    <Plane className="w-6 h-6 text-muted-foreground" />
                  </div>
                  <p className="text-muted-foreground mb-2">
                    Environment configuration required
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Please set <code className="px-1.5 py-0.5 rounded bg-muted font-mono text-xs">NEXT_PUBLIC_CREW_API_URL</code> and{" "}
                    <code className="px-1.5 py-0.5 rounded bg-muted font-mono text-xs">NEXT_PUBLIC_CREW_BEARER_TOKEN</code> to continue.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <p className="text-sm text-muted-foreground text-center">
            Powered by AI Crew Technology
          </p>
        </div>
      </footer>
    </div>
  )
}
