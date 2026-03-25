/**
 * Recipe 02 — Quick Start (TypeScript)
 * =====================================
 * Same as Recipe 01, but in TypeScript.
 *
 *     npm install @othnielobasi/airg-client
 *     export GOVERNOR_URL=https://api.airg.nov-tia.com
 *     export GOVERNOR_API_KEY=airg_...
 *     npx tsx 02_quick_start.ts
 */
import { GovernorClient, GovernorBlockedError } from "@othnielobasi/airg-client";

const gov = new GovernorClient();

// ── 1. Evaluate a low-risk tool call ─────────────────────────
const safe = await gov.evaluate("read_file", { path: "/tmp/report.csv" });
console.log(`✅  Decision : ${safe.decision}`);
console.log(`    Risk     : ${safe.risk_score}`);
console.log(`    Reason   : ${safe.explanation}`);

// ── 2. Evaluate a high-risk tool call ────────────────────────
try {
  const risky = await gov.evaluate("shell_exec", { command: "rm -rf /" });
  console.log(`\n⚠️  Decision : ${risky.decision}`);
} catch (err) {
  if (err instanceof GovernorBlockedError) {
    console.log(`\n🛑  BLOCKED  : ${err.message}`);
    console.log("    The Governor prevented a dangerous operation.");
  } else {
    throw err;
  }
}
