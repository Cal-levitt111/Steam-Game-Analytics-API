import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { requireSession } from "@/lib/auth/guards";

const backendBaseUrl = process.env.FASTAPI_BASE_URL ?? "http://127.0.0.1:8000";
const mcpUrl = `${backendBaseUrl}/mcp`;

const vscodeConfig = `{
  "servers": {
    "steam-api": {
      "type": "http",
      "url": "${mcpUrl}"
    }
  }
}`;

export default async function McpPage() {
  await requireSession();

  return (
    <div className="space-y-6">
      <section className="glass-panel rounded-[2rem] border border-border/70 bg-surface px-6 py-8 text-primary-foreground shadow-lg">
        <Badge variant="outline">MCP access</Badge>
        <h1 className="mt-4 font-display text-4xl font-semibold tracking-tight">
          Test the MCP server from VS Code or another MCP client.
        </h1>
        <p className="mt-3 max-w-3xl text-base leading-7 text-primary-foreground/76">
          The backend exposes a read-only MCP server at <code>{mcpUrl}</code>. In local
          development it is open for testing. In production, when MCP is enabled, the mount stays
          protected by bearer authentication.
        </p>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Local VS Code test flow</CardTitle>
            <CardDescription>
              This is the quickest path for validating MCP support on your own machine.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm leading-6 text-muted">
            <ol className="list-decimal space-y-2 pl-5">
              <li>Start the FastAPI backend locally with <code>uvicorn app.main:app --reload</code>.</li>
              <li>
                Confirm <code>{mcpUrl}</code> is reachable while the backend is running.
              </li>
              <li>
                Create or update <code>.vscode/mcp.json</code> in the repository root with the
                config shown on this page.
              </li>
              <li>Open the project in VS Code and reload the window if the MCP server is not detected immediately.</li>
              <li>Use the registered MCP server from your VS Code MCP-compatible workflow.</li>
            </ol>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>VS Code config</CardTitle>
            <CardDescription>Use this exact structure for local HTTP MCP testing.</CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="overflow-x-auto rounded-[1.2rem] bg-background-alt p-4 text-sm leading-6 text-primary">
              <code>{vscodeConfig}</code>
            </pre>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>What the MCP server exposes</CardTitle>
            <CardDescription>
              The MCP allowlist is intentionally read-only and excludes auth and collection writes.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm leading-6 text-muted">
            <p>Available tool tags:</p>
            <ul className="list-disc space-y-1 pl-5">
              <li><code>health</code></li>
              <li><code>games</code></li>
              <li><code>search</code></li>
              <li><code>genres</code></li>
              <li><code>tags</code></li>
              <li><code>developers</code></li>
              <li><code>publishers</code></li>
              <li><code>analytics</code></li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Production note</CardTitle>
            <CardDescription>
              Local testing is the simple path. Production MCP has stricter expectations.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm leading-6 text-muted">
            <p>
              If you enable MCP in production, clients must be able to authenticate to the backend.
              The mount stays protected outside development.
            </p>
            <p>
              For this project, local VS Code testing against the development backend is the
              recommended first validation step before exposing MCP on the hosted deployment.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
