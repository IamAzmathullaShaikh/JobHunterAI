import asyncio
import re
import random
from urllib.parse import quote
from typing import List, Optional
from bs4 import BeautifulSoup
from loguru import logger
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from scrapers.base import BaseScraper
from schemas.job_listing import JobListingCreate

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

def sanitize_term(text: str) -> str:
    """Strips boolean operators (AND, OR, NOT) and cleans punctuation for search safety."""
    cleaned = re.sub(r'\b(AND|OR|NOT)\b', '', text, flags=re.IGNORECASE)
    cleaned = re.sub(r'[^a-zA-Z0-9\s-]', ' ', cleaned)
    return re.sub(r'\s+', ' ', cleaned).strip()

class NaukriScraper(BaseScraper):
    @property
    def name(self) -> str:
        return "Naukri"

    async def scrape(
        self, 
        search_query: str, 
        location: Optional[str] = None, 
        limit: int = 10, 
        job_type: str = "Full-Time"
    ) -> List[JobListingCreate]:
        log = logger.bind(scraper=self.name)
        target_location = location or "India"
        log.info(f"Spawning stealth instance for Query: '{search_query}' inside '{target_location}' [{job_type}]")
        
        jobs: List[JobListingCreate] = []
        clean_q = sanitize_term(search_query) or "jobs"
        clean_loc = sanitize_term(target_location) or "india"
        
        q_slug = clean_q.lower().replace(" ", "-")
        loc_slug = clean_loc.lower().replace(" ", "-")
        
        # naukri API and web endpoints
        api_url = f"https://www.naukri.com/jobapi/v3/search?noOfResults={limit}&urlType=search_by_keyword&searchType=adv&keyword={quote(clean_q)}&location={quote(clean_loc)}&pageNo=1"
        page_url = f"https://www.naukri.com/{q_slug}-jobs-in-{loc_slug}?k={quote(clean_q)}&l={quote(clean_loc)}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars"
                ]
            )
            
            context = await browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                locale="en-US",
                timezone_id="Asia/Kolkata",
                extra_http_headers={
                    "appid": "109",
                    "systemid": "109",
                    "clientid": "d3skt0p",
                    "accept": "application/json",
                    "Referer": "https://www.naukri.com/"
                }
            )
            
            await Stealth().apply_stealth_async(context)

            # =========================================================================
            # TIER 1: Direct Hit to Internal Naukri JSON API
            # =========================================================================
            try:
                log.debug(f"Querying internal JSON API directly: {api_url}")
                res = await context.request.get(api_url, timeout=10000)
                if res.status == 200:
                    data = await res.json()
                    job_details = data.get("jobDetails", [])
                    if job_details:
                        log.info(f"Successfully harvested {len(job_details)} listings via Naukri REST API!")
                        for item in job_details[:limit]:
                            raw_id = str(item.get("jobId", random.randint(100000, 999999)))
                            title = item.get("title", "Job Role")
                            company_name = item.get("companyName", "Confidential")
                            
                            loc = target_location
                            for ph in item.get("placeholders", []):
                                if ph.get("type") == "location":
                                    loc = ph.get("label", target_location)

                            jd_url = item.get("jdURL", "")
                            if jd_url and not jd_url.startswith("http"):
                                full_url = f"https://www.naukri.com{jd_url}" if jd_url.startswith("/") else f"https://www.naukri.com/{jd_url}"
                            else:
                                full_url = jd_url or f"https://www.naukri.com/job-listings-{raw_id}"

                            desc = item.get("jobDescription") or item.get("snippets") or f"{title} at {company_name}"
                            if isinstance(desc, list):
                                desc = " ".join(desc)

                            jobs.append(
                                JobListingCreate(
                                    job_id_raw=raw_id,
                                    title=title,
                                    company_name=company_name,
                                    location=loc,
                                    work_place_type="Onsite",
                                    job_type=job_type,
                                    source=self.name,
                                    url=full_url,
                                    description_raw=str(desc),
                                    description_clean=str(desc)[:300]
                                )
                            )
                        await context.close()
                        await browser.close()
                        return jobs
            except Exception as api_err:
                log.debug(f"Direct API call bypassed: {api_err}. Proceeding to Tier 2 Network Listener.")

            # =========================================================================
            # TIER 2: Browser Navigation with XHR Network Listener
            # =========================================================================
            page = await context.new_page()
            intercepted_jobs = []

            async def handle_response(response):
                if "/jobapi/v3/search" in response.url and response.status == 200:
                    try:
                        data = await response.json()
                        details = data.get("jobDetails", [])
                        if details:
                            intercepted_jobs.extend(details)
                    except Exception:
                        pass

            page.on("response", handle_response)

            try:
                log.debug(f"Navigating browser to page URL: {page_url}...")
                await page.goto(page_url, timeout=35000, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(2.5, 4.0))

                if intercepted_jobs:
                    log.info(f"Captured {len(intercepted_jobs)} listings via XHR response listener!")
                    for item in intercepted_jobs[:limit]:
                        raw_id = str(item.get("jobId", random.randint(100000, 999999)))
                        title = item.get("title", "Job Role")
                        company_name = item.get("companyName", "Confidential")
                        
                        loc = target_location
                        for ph in item.get("placeholders", []):
                            if ph.get("type") == "location":
                                loc = ph.get("label", target_location)

                        jd_url = item.get("jdURL", "")
                        full_url = f"https://www.naukri.com{jd_url}" if jd_url.startswith("/") else jd_url or page_url

                        desc = item.get("jobDescription") or f"{title} at {company_name}"
                        if isinstance(desc, list):
                            desc = " ".join(desc)

                        jobs.append(
                            JobListingCreate(
                                job_id_raw=raw_id,
                                title=title,
                                company_name=company_name,
                                location=loc,
                                work_place_type="Onsite",
                                job_type=job_type,
                                source=self.name,
                                url=full_url,
                                description_raw=str(desc),
                                description_clean=str(desc)[:300]
                            )
                        )
                    await context.close()
                    await browser.close()
                    return jobs

                # =========================================================================
                # TIER 3: BeautifulSoup DOM Parser Fallback
                # =========================================================================
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                cards = (
                    soup.find_all("div", class_="srp-jobtuple-wrapper") or 
                    soup.find_all("div", class_="cust-job-tuple") or 
                    soup.find_all("article", class_="jobTuple") or
                    soup.find_all("div", attrs={"data-job-id": True})
                )

                log.info(f"DOM fallback found {len(cards)} raw cards.")
                for card in cards[:limit]:
                    try:
                        title_tag = card.find("a", class_="title") or card.find("a", class_="jobTitle") or card.find("a", class_="row1")
                        if not title_tag:
                            continue

                        title = title_tag.get_text(strip=True)
                        job_url = title_tag.get("href", "")
                        raw_id = card.get("data-job-id") or card.get("id", f"nk-{random.randint(100000, 999999)}")

                        comp_tag = card.find("a", class_="comp-name") or card.find("a", class_="subTitle")
                        company_name = comp_tag.get_text(strip=True) if comp_tag else "Confidential / Unlisted"

                        loc_tag = card.find("span", class_="loc-wrap") or card.find("li", class_="location") or card.find("span", class_="locWrf")
                        loc_text = loc_tag.get_text(strip=True) if loc_tag else target_location

                        desc_tag = card.find("span", class_="job-desc") or card.find("div", class_="ellipsis")
                        desc_text = desc_tag.get_text(strip=True) if desc_tag else f"Naukri listed role: {title}."

                        jobs.append(
                            JobListingCreate(
                                job_id_raw=str(raw_id),
                                title=title,
                                company_name=company_name,
                                location=loc_text,
                                work_place_type="Onsite",
                                job_type=job_type,
                                source=self.name,
                                url=job_url,
                                description_raw=desc_text,
                                description_clean=desc_text[:300]
                            )
                        )
                    except Exception as card_err:
                        log.warning(f"Skipping corrupt structural card: {card_err}")

            except Exception as e:
                log.error(f"Naukri stealth scraper execution error: {e}")
            finally:
                await context.close()
                await browser.close()

        return jobs