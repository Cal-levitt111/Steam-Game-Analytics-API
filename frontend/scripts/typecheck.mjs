import { execSync } from "node:child_process";
import { existsSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";

execSync("next typegen", { stdio: "inherit" });

const cacheLifePath = join(process.cwd(), ".next", "types", "cache-life.d.ts");
const nextCachePath = join(process.cwd(), ".next", "cache");
mkdirSync(dirname(cacheLifePath), { recursive: true });

if (!existsSync(cacheLifePath)) {
  writeFileSync(cacheLifePath, "export {};\n", "utf8");
}

rmSync(nextCachePath, { recursive: true, force: true });

execSync("tsc --noEmit", { stdio: "inherit" });
