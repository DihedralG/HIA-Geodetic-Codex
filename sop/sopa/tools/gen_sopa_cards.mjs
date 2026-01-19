import fs from "fs";
import path from "path";

const OUT_DIR = path.resolve("sop/sopa/data/cards");
fs.mkdirSync(OUT_DIR, { recursive: true });

const schemaVersion = "sop.datacard.v1";
const moduleName = "SOPA";

// Minimal country list (extend freely)
const members = [
  // Sovereign Americas (35)
  ["USA","United States","sovereign_state","A",[80,92]],
  ["CAN","Canada","sovereign_state","A",[75,88]],
  ["MEX","Mexico","sovereign_state","B",[70,84]],
  ["BRA","Brazil","sovereign_state","A",[70,85]],
  ["CHL","Chile","sovereign_state","A",[72,86]],
  ["COL","Colombia","sovereign_state","B",[65,80]],
  ["PAN","Panama","sovereign_state","A",[70,86]],
  ["HTI","Haiti","sovereign_state","D",[40,60]],
  ["VEN","Venezuela","sovereign_state","B",[55,78]],
  // add the rest here as tuples...
];

// A very simple baseline score template (edit once, applies everywhere)
function defaultKpisForTier(tier) {
  switch (tier) {
    case "A": return { ss:78, et:78, ir:72, gc:72, ec:62, dp:72, si:68 };
    case "B": return { ss:62, et:64, ir:58, gc:56, ec:58, dp:58, si:56 };
    case "C": return { ss:54, et:50, ir:48, gc:46, ec:54, dp:48, si:48 };
    case "D": return { ss:38, et:34, ir:32, gc:30, ec:44, dp:34, si:32 };
    default:  return { ss:50, et:50, ir:50, gc:50, ec:50, dp:50, si:50 };
  }
}

function card(member_id, display_name, type, tier, band, sovereignty = {status:"sovereign", administering_state:null, notes:""}) {
  const d = defaultKpisForTier(tier);
  return {
    schema_version: schemaVersion,
    module: moduleName,
    member_id,
    display_name,
    type,
    sovereignty: {
      status: sovereignty.status ?? "sovereign",
      administering_state: sovereignty.administering_state ?? null,
      notes: sovereignty.notes ?? ""
    },
    tiering: { tier, role_label: tier==="A"?"Core Operator":tier==="B"?"Integrated":tier==="C"?"Functional":"Observer / Limited", confidence_band: band, method: "heuristic_v0" },
    kpis: {
      security_stability: { score: d.ss, confidence: 0.55 },
      economic_throughput: { score: d.et, confidence: 0.55 },
      infrastructure_resilience: { score: d.ir, confidence: 0.55 },
      governance_compliance: { score: d.gc, confidence: 0.55 },
      environment_climate: { score: d.ec, confidence: 0.55 },
      data_participation: { score: d.dp, confidence: 0.55 },
      social_impact: { score: d.si, confidence: 0.55 }
    },
    top_assets: [],
    top_pain_points: [],
    notes: { baseline_only: true, user_overrides_allowed: true, override_guidance: "Edit scores/weights; simulations propagate deltas.", tags: [] }
  };
}

const bundle = { schema_version: "sop.bundle.v1", module: moduleName, baseline_method: "heuristic_v0", members: [] };

for (const [id, name, type, tier, band] of members) {
  const c = card(id, name, type, tier, band);
  bundle.members.push(c);
  fs.writeFileSync(path.join(OUT_DIR, `${id}.json`), JSON.stringify(c, null, 2));
}

const outDir = path.resolve("data/sopa/members");
fs.mkdirSync(outDir, { recursive: true });

for (const member of members) {
  const code = member.code; // e.g., "USA"
  const outPath = path.join(outDir, `${code}.json`);
  fs.writeFileSync(outPath, JSON.stringify(member, null, 2));
}
console.log(`Wrote ${bundle.members.length} cards + bundle`);