/**
 * SOPA Schema Validator
 * ---------------------
 * Validates generated SOPA JSON against declared schemas.
 * Non-blocking by default; intended for CI / preflight checks.
 */

const fs = require("fs");
const path = require("path");
const Ajv = require("ajv");

const ajv = new Ajv({ allErrors: true, strict: false });

const ROOT = path.resolve(__dirname, "..");
const SCHEMA_DIR = path.join(ROOT, "data", "schemas");
const DATA_DIR = path.resolve(ROOT, "..", "..", "data", "sopa");

function loadJSON(p) {
  return JSON.parse(fs.readFileSync(p, "utf-8"));
}

function validateFile(dataPath, schemaPath) {
  const data = loadJSON(dataPath);
  const schema = loadJSON(schemaPath);

  const validate = ajv.compile(schema);
  const valid = validate(data);

  if (!valid) {
    console.error(`❌ Schema validation failed: ${path.basename(dataPath)}`);
    console.error(validate.errors);
    return false;
  }

  console.log(`✅ Valid: ${path.basename(dataPath)}`);
  return true;
}

function main() {
  let ok = true;

  // Validate indexes
  ok &= validateFile(
    path.join(DATA_DIR, "members.index.json"),
    path.join(SCHEMA_DIR, "members.index.schema.json")
  );

  ok &= validateFile(
    path.join(DATA_DIR, "pilots.index.json"),
    path.join(SCHEMA_DIR, "pilots.index.schema.json")
  );

  // Validate each member card
  const membersDir = path.join(DATA_DIR, "members");
  const memberSchema = path.join(SCHEMA_DIR, "member.schema.json");

  fs.readdirSync(membersDir)
    .filter(f => f.endsWith(".json"))
    .forEach(file => {
      ok &= validateFile(
        path.join(membersDir, file),
        memberSchema
      );
    });

  if (!ok) {
    console.error("\n🚨 SOPA schema validation completed with errors.");
    process.exit(1);
  }

  console.log("\n🎯 SOPA schema validation complete. All files valid.");
}

main();