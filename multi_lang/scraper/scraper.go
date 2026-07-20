package main

import (
	"fmt"
	"net/http"
)

func scrapeHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Scraping jobs...")
	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(`[{"raw_title": "Dev", "raw_company": "Tech"}]`))
}

func main() {
	http.HandleFunc("/scrape", scrapeHandler)
	http.ListenAndServe(":8081", nil)
}
