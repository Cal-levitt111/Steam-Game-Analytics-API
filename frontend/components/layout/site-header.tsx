import Link from "next/link";
import { BarChart3, Gamepad2, Search, Shield } from "lucide-react";

import { Button } from "@/components/ui/button";

const navItems = [
  { href: "/games", label: "Games", icon: Gamepad2 },
  { href: "/search", label: "Search", icon: Search },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/collections", label: "Collections", icon: Shield },
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-30 pt-4">
      <div className="glass-panel flex items-center justify-between rounded-full border border-border/70 bg-card/85 px-4 py-3 shadow-[0_10px_40px_rgba(16,32,51,0.08)]">
        <Link href="/" className="flex items-center gap-3">
          <div className="rounded-full bg-primary px-3 py-2 font-display text-sm font-semibold tracking-[0.18em] text-primary-foreground">
            SGA
          </div>
          <div>
            <p className="font-display text-sm font-semibold tracking-[0.2em] text-primary uppercase">
              Steam Analytics
            </p>
            <p className="text-xs text-muted">Demo frontend</p>
          </div>
        </Link>

        <nav className="hidden items-center gap-2 md:flex">
          {navItems.map(({ href, label, icon: Icon }) => (
            <Button key={href} asChild variant="ghost" size="sm">
              <Link href={href}>
                <Icon className="size-4" />
                {label}
              </Link>
            </Button>
          ))}
        </nav>
      </div>
    </header>
  );
}
