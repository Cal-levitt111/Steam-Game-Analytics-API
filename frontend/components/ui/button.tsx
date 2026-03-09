import type { ButtonHTMLAttributes } from "react";
import { Slot } from "@radix-ui/react-slot";

import { cn } from "@/lib/utils";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  asChild?: boolean;
  size?: "default" | "sm" | "lg";
  variant?: "default" | "secondary" | "ghost" | "outline" | "danger";
};

export function Button({
  asChild = false,
  className,
  size = "default",
  variant = "default",
  ...props
}: ButtonProps) {
  const Comp = asChild ? Slot : "button";

  return (
    <Comp
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-full font-medium transition-transform duration-150 hover:-translate-y-0.5 disabled:pointer-events-none disabled:opacity-60",
        size === "default" && "min-h-11 px-4 py-2 text-sm",
        size === "sm" && "min-h-9 px-3 py-2 text-sm",
        size === "lg" && "min-h-12 px-5 py-3 text-base",
        variant === "default" && "bg-primary text-primary-foreground shadow-lg hover:bg-primary/92",
        variant === "secondary" && "bg-accent-alt text-accent-foreground shadow-lg hover:bg-accent-alt/90",
        variant === "ghost" && "bg-transparent text-primary hover:bg-primary/7",
        variant === "outline" && "border border-border bg-card text-foreground hover:bg-background-alt",
        variant === "danger" && "bg-danger text-white hover:bg-danger/92",
        className,
      )}
      {...props}
    />
  );
}
