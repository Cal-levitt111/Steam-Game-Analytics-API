import { execSync } from "node:child_process";

execSync("next typegen", { stdio: "inherit" });
execSync("tsc --noEmit -p tsconfig.typecheck.json", { stdio: "inherit" });
