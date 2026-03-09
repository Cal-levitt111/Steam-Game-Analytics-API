import { execSync } from "node:child_process";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";

execSync("next typegen", { stdio: "inherit" });

const cacheLifePath = join(process.cwd(), ".next", "types", "cache-life.d.ts");
mkdirSync(dirname(cacheLifePath), { recursive: true });

if (!existsSync(cacheLifePath)) {
  writeFileSync(cacheLifePath, "export {};\n", "utf8");
}

execSync("tsc --noEmit", { stdio: "inherit" });
