export function SiteFooter() {
  return (
    <footer className="border-t border-border/80 py-8 text-sm text-muted">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <p>Steam Analytics Demo Frontend</p>
        <p>Built against the FastAPI backend in this repository.</p>
      </div>
    </footer>
  );
}
