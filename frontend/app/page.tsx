import Link from "next/link";
import { ArrowRight, BarChart3, Search, ShieldCheck, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const featureCards = [
  {
    title: "Catalog exploration",
    description: "Responsive discovery views for games, taxonomies, filters, and search.",
    icon: Search,
  },
  {
    title: "Authenticated flows",
    description: "A cookie-backed BFF layer for login, profile retrieval, and protected actions.",
    icon: ShieldCheck,
  },
  {
    title: "Analytics storytelling",
    description: "Dedicated surfaces for trends, breakdowns, and similarity-driven exploration.",
    icon: BarChart3,
  },
];

export default function Home() {
  return (
    <div className="space-y-10">
      <section className="glass-panel animate-rise overflow-hidden rounded-[2rem] border border-border/70 bg-surface px-6 py-10 text-primary-foreground shadow-lg sm:px-8 lg:px-12">
        <div className="grid gap-8 lg:grid-cols-[1.35fr_0.9fr] lg:items-end">
          <div className="space-y-6">
            <Badge variant="accent">Next.js demo frontend</Badge>
            <div className="space-y-4">
              <h1 className="max-w-3xl font-display text-4xl font-semibold tracking-tight text-balance sm:text-5xl lg:text-6xl">
                A focused demo shell for the Steam Game Analytics API.
              </h1>
              <p className="max-w-2xl text-base leading-7 text-primary-foreground/78 sm:text-lg">
                This frontend is being built as a live demonstration surface for search, collections,
                similarity, and analytics. The next commits layer in backend integration route by
                route.
              </p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Button asChild size="lg">
                <Link href="/games">
                  Explore games
                  <ArrowRight className="size-4" />
                </Link>
              </Button>
              <Button asChild variant="secondary" size="lg">
                <Link href="/analytics">View analytics</Link>
              </Button>
            </div>
          </div>

          <div className="animate-rise-delay rounded-[1.5rem] border border-white/10 bg-white/8 p-6">
            <div className="mb-5 flex items-center gap-3">
              <div className="rounded-full bg-accent/20 p-2 text-accent-alt">
                <Sparkles className="size-5" />
              </div>
              <div>
                <p className="text-sm uppercase tracking-[0.28em] text-primary-foreground/55">
                  Foundation status
                </p>
                <p className="text-lg font-medium text-primary-foreground">Shell committed</p>
              </div>
            </div>
            <ul className="space-y-3 text-sm text-primary-foreground/78">
              <li>Shared theme tokens and typography</li>
              <li>Reusable card, badge, button, and state components</li>
              <li>Persistent navigation for public and protected demo areas</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-3">
        {featureCards.map(({ title, description, icon: Icon }) => (
          <Card key={title} className="animate-rise">
            <CardHeader>
              <div className="mb-4 inline-flex w-fit rounded-2xl bg-primary p-3 text-primary-foreground">
                <Icon className="size-5" />
              </div>
              <CardTitle>{title}</CardTitle>
              <CardDescription>{description}</CardDescription>
            </CardHeader>
            <CardContent className="text-sm leading-6 text-muted">
              The app shell is ready to receive the API client, BFF auth routes, and the feature
              pages described in the implementation plan.
            </CardContent>
          </Card>
        ))}
      </section>
    </div>
  );
}
