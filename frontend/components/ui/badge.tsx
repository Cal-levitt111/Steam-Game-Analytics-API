import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type BadgeProps = HTMLAttributes<HTMLDivElement> & {
  variant?: "default" | "accent" | "outline";
};

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex w-fit items-center rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em]",
        variant === "default" && "border-border bg-background-alt text-primary",
        variant === "accent" && "border-accent/30 bg-accent-alt text-accent-foreground",
        variant === "outline" && "border-white/20 bg-white/5 text-primary-foreground",
        className,
      )}
      {...props}
    />
  );
}
