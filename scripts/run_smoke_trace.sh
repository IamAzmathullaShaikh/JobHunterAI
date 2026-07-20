#!/bin/bash
echo "Running smoke trace for job URL resolution..."
curl -s -X POST http://localhost:3000/api/scrape -H "Content-Type: application/json" -d '{"search_query": "React", "location": "Remote", "job_type": "Full-Time"}' | grep -o 'needs_validation'
