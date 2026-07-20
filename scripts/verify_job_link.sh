#!/bin/bash
if [ -z "$1" ]; then
  echo "Usage: ./verify_job_link.sh <job_id>"
  exit 1
fi

JOB_ID=$1
DB_FILE="database/db.json"

if [ ! -f "$DB_FILE" ]; then
  # Fallback to local
  DB_FILE="db.json"
fi

if [ ! -f "$DB_FILE" ]; then
  echo "Database file $DB_FILE not found!"
  exit 1
fi

node -e "
const db = require('./' + '$DB_FILE');
const job = db.jobs.find(j => j.id == $JOB_ID);
if (!job) {
  console.log('Job not found');
  process.exit(1);
}
console.log('--- DB Record ---');
console.log('ID:', job.id);
console.log('Title:', job.title);
console.log('Company:', job.company_name);
console.log('Raw URL:', job.raw_url);
console.log('Canonical URL:', job.canonical_url);
console.log('Portal ID:', job.portal_id);
console.log('Needs Validation:', job.needs_validation);

const linkToOpen = job.canonical_url || job.raw_url;
console.log('\n--- Link Check ---');
console.log('Link to open:', linkToOpen);
" > verify_tmp.txt

cat verify_tmp.txt

LINK=$(grep "Link to open:" verify_tmp.txt | awk '{print $4}')

if [ -n "$LINK" ] && [[ "$LINK" != "undefined" && "$LINK" != "null" && "$LINK" != "" ]]; then
  echo "Curling link..."
  curl -I -L -s "$LINK" | head -n 1
else
  echo "No valid link found to curl."
fi

rm verify_tmp.txt
