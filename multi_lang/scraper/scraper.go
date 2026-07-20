package main

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type Job struct {
	Title       string `json:"raw_title"`
	Company     string `json:"raw_company"`
	Description string `json:"raw_description"`
}

func scrapeHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Simulating local scraping...")
	jobs := []Job{
		{"Backend Engineer", "TechCorp", "Looking for a Go and Python developer."},
		{"Frontend Dev", "WebInc", "React and TypeScript experience required."},
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(jobs)
}

func main() {
	http.HandleFunc("/scrape", scrapeHandler)
	fmt.Println("Scraper running on :8081")
	http.ListenAndServe(":8081", nil)
}
