const { execSync } = require('child_process');

console.log("=== JobHunterAI Local Orchestrator ===");

console.log("\n1. Scraping (Go)");
// fetch('http://localhost:8081/scrape')

console.log("\n2. Normalizing (TS)");
// fetch('http://localhost:8082/normalize')

console.log("\n3. Deduplicating (Rust)");
execSync('rustc ../deduplicator/deduplicator.rs -o dedup && ./dedup "data"', {stdio: 'inherit'});

console.log("\n4. Parsing Resume Locally (Python)");
// fetch('http://localhost:8084/parse')

console.log("\n5. Local Keyword Matching (Python)");
// fetch('http://localhost:8085/match')

console.log("\n6. Storage (Java)");
execSync('javac ../storage/Storage.java && java -cp ../storage Storage', {stdio: 'inherit'});

console.log("\n7. Export (C#)");
// execSync('csc ../exporter/Exporter.cs && mono Exporter.exe');

console.log("\n=== Pipeline Complete ===");
