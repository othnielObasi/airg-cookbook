/**
 * Recipe 02 - Quick Start (TypeScript)
 * ====================================
 * Create an AIRG SDK client and evaluate two tool calls.
 *
 * GovernorClient reads GOVERNOR_URL and GOVERNOR_API_KEY from the environment
 * unless you pass explicit config to the constructor.
 *
 *     npm install @othnielobasi/airg-client
 *     export GOVERNOR_URL=https://api.airg.nov-tia.com
 *     export GOVERNOR_API_KEY="<your AIRG account API key>"
 *     npx tsx 02_quick_start.ts
 */
import { GovernorClient, GovernorBlockedError } from "@othnielobasi/airg-client";

const gov = new GovernorClient();
const context = {
  agent_id: "quickstart-ts-agent",
  session_id: "quickstart-ts-demo",
};

const safe = await gov.evaluate("read_file", { path: "/tmp/report.csv" }, context);
console.log("Safe tool call");
console.log(`  Decision   : ${safe.decision}`);
console.log(`  Risk       : ${safe.risk_score}/100`);
console.log(`  Explanation: ${safe.explanation}`);

try {
  const risky = await gov.evaluate("shell_exec", { command: "rm -rf /" }, context);
  console.log("\nHigh-risk tool call");
  console.log(`  Decision   : ${risky.decision}`);
} catch (err) {
  if (err instanceof GovernorBlockedError) {
    console.log("\nHigh-risk tool call");
    console.log("  Decision   : block");
    console.log("  Result     : AIRG prevented execution");
    console.log(`  Detail     : ${err.message}`);
  } else {
    throw err;
  }
}
