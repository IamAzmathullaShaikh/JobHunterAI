import express from "express";
import cors from "cors";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI, Type } from "@google/genai";
import * as XLSX from "xlsx";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json({ limit: "50mb" }));

// Initialize Google Gen AI
const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
  httpOptions: {
    headers: {
      "User-Agent": "aistudio-build",
    },
  },
});

const DEFAULT_MODEL = "gemini-3.1-flash-lite";

function getModel(requestedModel?: string): string {
  // If the user requests a model from the client, use it. Otherwise, fallback to the default.
  // Note: we do NOT read process.env.GEMINI_MODEL as it conflicts with AI Studio platform env vars.
  return requestedModel || DEFAULT_MODEL;
}

// JSON-based Persistent Local Database
const DB_FILE = process.env.DB_PATH || path.join(process.cwd(), "db.json");

interface LocalDB {
  profile: any | null;
  jobs: any[];
}

function loadDB(): LocalDB {
  if (fs.existsSync(DB_FILE)) {
    try {
      const content = fs.readFileSync(DB_FILE, "utf-8");
      return JSON.parse(content);
    } catch (e) {
      console.error("Error reading database file, resetting:", e);
    }
  }
  return { profile: null, jobs: [] };
}

function saveDB(data: LocalDB) {
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2), "utf-8");
  } catch (e) {
    console.error("Error saving database file:", e);
  }
}

// ----------------------------------------------------------------------
// API Endpoints
// ----------------------------------------------------------------------

// 1. Get Candidate Profile
app.get("/api/profile", (req, res) => {
  const db = loadDB();
  res.json({ profile: db.profile });
});

// 2. Parse Resume (Copy-Paste or Base64 PDF/Text)
app.post("/api/profile/parse", async (req, res) => {
  try {
    const { text, fileBase64, fileName, fileType } = req.body;

    let geminiContents: any[] = [];

    if (fileBase64 && fileType === "application/pdf") {
      geminiContents.push({
        inlineData: {
          data: fileBase64.split(",")[1] || fileBase64,
          mimeType: "application/pdf",
        },
      });
      geminiContents.push(
        "Analyze the uploaded resume PDF. Extract the professional capabilities, full name, education, total years of experience, key skills, suggested search queries for job engines, and 3 experience highlights. Return the data in the requested JSON format."
      );
    } else {
      const resumeContent = text || "No resume text provided.";
      geminiContents.push(
        `Analyze the following resume text. Extract the candidate's professional capabilities, full name, education, total years of experience, key skills, recommended search queries for job engines, and 3 experience highlights.\n\nResume Text:\n${resumeContent}`
      );
    }

    const response = await ai.models.generateContent({
      model: getModel(req.body.model),
      contents: geminiContents,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            full_name: { type: Type.STRING },
            total_experience_years: { type: Type.NUMBER },
            education: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
            },
            key_skills: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
            },
            recommended_search_queries: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
            },
            experience_highlights: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
            },
          },
          required: [
            "full_name",
            "total_experience_years",
            "education",
            "key_skills",
            "recommended_search_queries",
            "experience_highlights",
          ],
        },
      },
    });

    const parsedJson = JSON.parse(response.text || "{}");
    const db = loadDB();
    db.profile = parsedJson;
    saveDB(db);

    res.json({ profile: parsedJson });
  } catch (error: any) {
    console.warn("AI Resume Parsing failed. Falling back to local regex parser.", error);
    
    // Local fallback parsing
    const fallbackProfile = {
      full_name: "Local User",
      total_experience_years: 0,
      education: [],
      key_skills: [] as string[],
      recommended_search_queries: ["Software Engineer", "Developer"],
      experience_highlights: ["Parsed locally due to AI rate limit"]
    };

    try {
      const resumeContent = (req.body.text || "").toLowerCase();
      
      const skills_keywords = ['python', 'java', 'react', 'go', 'rust', 'c#', 'sql', 'aws', 'docker', 'typescript', 'node.js', 'javascript', 'html', 'css', 'kubernetes', 'gcp', 'azure'];
      fallbackProfile.key_skills = skills_keywords.filter(s => resumeContent.includes(s));
      
      const yearsMatch = resumeContent.match(/(\d+)\+?\s*years? of experience/i);
      if (yearsMatch) {
        fallbackProfile.total_experience_years = parseInt(yearsMatch[1], 10);
      }
    } catch (e) {
      console.error("Local parsing also failed", e);
    }
    
    const db = loadDB();
    db.profile = fallbackProfile;
    saveDB(db);
    res.json({ profile: fallbackProfile, fallback: true });
  }
});

// 3. simulated multi-engine scraping & job discovery
app.post("/api/scrape", async (req, res) => {
  try {
    const { search_query, location, job_type, candidate_context } = req.body;

    if (!search_query || !location) {
      return res.status(400).json({ error: "Search query and location are required." });
    }

    const prompt = `You are an automated multi-engine scraper. We are searching for job listings matching the keyword "${search_query}" in "${location}" for a "${job_type}" role.
Based on this request and the optional candidate profile below:
${candidate_context || "No candidate profile uploaded yet."}

Generate 10 highly realistic, detailed job listing records that would be found across 9 popular platforms: LinkedIn, Indeed, Naukri, Foundit, Glassdoor, Google Jobs, Apify Cloud, Internshala, and YC Jobs.
Ensure each generated job listing has an external unique job ID, highly realistic company name, real title, description, application URL (mock), and specific source (randomly distribute sources across the 9 platforms).
Also specify workplace type (Remote, Hybrid, Onsite) and some realistic salary ranges (min, max, currency, raw string).
Return the result in the requested JSON schema format.`;

    const response = await ai.models.generateContent({
      model: getModel(req.body.model),
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              job_id_raw: { type: Type.STRING },
              title: { type: Type.STRING },
              company_name: { type: Type.STRING },
              location: { type: Type.STRING },
              work_place_type: { type: Type.STRING }, // Remote, Hybrid, Onsite
              job_type: { type: Type.STRING }, // Full-Time, Internship, Apprenticeship
              source: { type: Type.STRING }, // LinkedIn, Indeed, etc.
              url: { type: Type.STRING },
              description_raw: { type: Type.STRING },
              salary_min: { type: Type.NUMBER },
              salary_max: { type: Type.NUMBER },
              salary_currency: { type: Type.STRING },
              salary_raw: { type: Type.STRING },
            },
            required: [
              "job_id_raw",
              "title",
              "company_name",
              "location",
              "work_place_type",
              "job_type",
              "source",
              "url",
              "description_raw",
            ],
          },
        },
      },
    });

    const crawledListings = JSON.parse(response.text || "[]");

    const db = loadDB();
    const existingIds = new Set(db.jobs.map((j) => j.job_id_raw));
    const newJobsAdded: any[] = [];

    crawledListings.forEach((item: any) => {
      if (!existingIds.has(item.job_id_raw)) {
        const id = db.jobs.length > 0 ? Math.max(...db.jobs.map((j) => j.id)) + 1 : 1;
        const newJob = {
          id,
          ...item,
          is_starred: false,
          date_scraped: new Date().toISOString(),
          ai_analysis: null,
          application: null,
        };
        db.jobs.push(newJob);
        newJobsAdded.push(newJob);
      }
    });

    saveDB(db);

    res.json({
      scraped_count: crawledListings.length,
      new_count: newJobsAdded.length,
      jobs: db.jobs,
    });
  } catch (error: any) {
    console.warn("AI Pipeline discovery failed. Using local deterministic fallback.", error);
    const db = loadDB();
    const fallbackJobs = [
      {
        job_id_raw: `mock-${Date.now()}-1`,
        title: "Software Engineer",
        company: "TechCorp",
        location: "Remote",
        description_raw: "Looking for a skilled developer with experience in React and Node.js."
      },
      {
        job_id_raw: `mock-${Date.now()}-2`,
        title: "Backend Developer",
        company: "DataInc",
        location: "New York, NY",
        description_raw: "Python and Go backend role with a focus on high concurrency."
      }
    ];

    const newJobsAdded: any[] = [];
    fallbackJobs.forEach((item: any) => {
        const id = db.jobs.length > 0 ? Math.max(...db.jobs.map((j) => j.id)) + 1 : 1;
        const newJob = {
          id,
          ...item,
          is_starred: false,
          date_scraped: new Date().toISOString(),
          ai_analysis: null,
          application: null,
        };
        db.jobs.push(newJob);
        newJobsAdded.push(newJob);
    });

    saveDB(db);
    res.json({
      scraped_count: fallbackJobs.length,
      new_count: newJobsAdded.length,
      jobs: db.jobs,
      fallback: true
    });
  }
});

// 4. Get All Job Listings (with joint structures)
app.get("/api/jobs", (req, res) => {
  const db = loadDB();
  res.json({ jobs: db.jobs });
});

// 5. Track Job (Move to pipeline funnel / Kanban)
app.post("/api/jobs/track", (req, res) => {
  const { job_id } = req.body;
  const db = loadDB();
  const job = db.jobs.find((j) => j.id === Number(job_id));

  if (!job) {
    return res.status(404).json({ error: "Job listing not found." });
  }

  if (!job.application) {
    job.application = {
      id: Math.floor(Math.random() * 1000000),
      job_id: job.id,
      status: "Identified",
      notes: "",
      date_created: new Date().toISOString(),
      date_updated: new Date().toISOString(),
    };
    saveDB(db);
  }

  res.json({ job });
});

// 6. Update Application Tracking Status / Notes
app.put("/api/applications/:app_id", (req, res) => {
  const { app_id } = req.params;
  const { status, notes } = req.body;
  const db = loadDB();

  let updatedJob = null;
  db.jobs.forEach((j) => {
    if (j.application && j.application.id === Number(app_id)) {
      j.application.status = status;
      j.application.notes = notes || "";
      j.application.date_updated = new Date().toISOString();
      updatedJob = j;
    }
  });

  if (!updatedJob) {
    return res.status(404).json({ error: "Application tracking card not found." });
  }

  saveDB(db);
  res.json({ job: updatedJob });
});

// 7. Calculate AI Match Scoring & Requirements Gaps
app.post("/api/jobs/analyze", async (req, res) => {
  try {
    const { job_id, resume_text } = req.body;

    if (!resume_text) {
      return res.status(400).json({ error: "Resume text is required to evaluate compatibility." });
    }

    const db = loadDB();
    const job = db.jobs.find((j) => j.id === Number(job_id));

    if (!job) {
      return res.status(404).json({ error: "Job listing not found." });
    }

    const prompt = `We are conducting a deep match analysis between a candidate's resume and a job listing.
Candidate Resume Text:
${resume_text}

Job Listing Details:
Title: ${job.title}
Company: ${job.company_name}
Location: ${job.location}
Description: ${job.description_raw}

Evaluate:
1. Match fit score between 0 and 100 (percentage).
2. Fit Strategic Summary (explain alignment, strengths, and recommendations).
3. Matched skills or keywords (specific overlapping tech, methodologies, or soft skills).
4. Missing structural gaps or keywords (requirements listed in job description that aren't highlighted in resume).

Return the evaluation in the requested JSON format.`;

    const response = await ai.models.generateContent({
      model: getModel(req.body.model),
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            match_score: { type: Type.NUMBER },
            fit_summary: { type: Type.STRING },
            keywords_matched: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
            },
            keywords_missing: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
            },
          },
          required: [
            "match_score",
            "fit_summary",
            "keywords_matched",
            "keywords_missing",
          ],
        },
      },
    });

    const analysisResult = JSON.parse(response.text || "{}");

    // Save back to DB
    const id = Math.floor(Math.random() * 1000000);
    job.ai_analysis = {
      id,
      job_id: job.id,
      ...analysisResult,
      analyzed_at: new Date().toISOString(),
    };

    saveDB(db);
    res.json({ job });
  } catch (error: any) {
    console.warn("AI Analysis failed. Falling back to local heuristic matching.", error);
    const db = loadDB();
    const { job_id } = req.body;
    const job = db.jobs.find((j) => j.id === Number(job_id));
    
    if (job) {
      const resumeProfile = db.profile || { key_skills: [], full_name: "User" };
      const resumeSkills = Array.isArray(resumeProfile.key_skills) ? resumeProfile.key_skills : [];
      const jobDesc = (job.description_raw || "").toLowerCase();
      
      const matchedSkills = resumeSkills.filter(s => jobDesc.includes(s.toLowerCase()));
      const score = Math.min(Math.round((matchedSkills.length / Math.max(resumeSkills.length, 1)) * 100), 100) || 50;
      
      job.ai_analysis = {
        id: Math.floor(Math.random() * 1000000),
        job_id: job.id,
        match_score: score,
        fit_summary: "Local Match: Calculated using keyword intersection.",
        matched_keywords: matchedSkills,
        missing_keywords: ["(Local fallback cannot determine missing keywords effectively)"],
        analyzed_at: new Date().toISOString(),
      };
      
      saveDB(db);
      res.json({ job, fallback: true });
    } else {
      res.status(404).json({ error: "Job not found." });
    }
  }
});

// 8. Auto-Batch Evaluate pending jobs
app.post("/api/jobs/analyze-pending", async (req, res) => {
  try {
    const { resume_text } = req.body;
    if (!resume_text) {
      return res.status(400).json({ error: "Resume text required." });
    }

    const db = loadDB();
    const pendingJobs = db.jobs.filter((j) => !j.ai_analysis);
    let analyzedCount = 0;

    // Evaluate up to 5 jobs in this batch to prevent long times
    const batchLimit = Math.min(pendingJobs.length, 5);

    for (let i = 0; i < batchLimit; i++) {
      const job = pendingJobs[i];
      try {
        const prompt = `Evaluate compatibility score (0-100), detailed fit strategic summary, matched skills array, and missing skills array between this resume and job.
Candidate Resume:
${resume_text}

Job Listing:
Title: ${job.title} at ${job.company_name}
Description: ${job.description_raw}

Return JSON with match_score, fit_summary, keywords_matched (string array), and keywords_missing (string array).`;

        const response = await ai.models.generateContent({
          model: getModel(req.body.model),
          contents: prompt,
          config: {
            responseMimeType: "application/json",
            responseSchema: {
              type: Type.OBJECT,
              properties: {
                match_score: { type: Type.NUMBER },
                fit_summary: { type: Type.STRING },
                keywords_matched: {
                  type: Type.ARRAY,
                  items: { type: Type.STRING },
                },
                keywords_missing: {
                  type: Type.ARRAY,
                  items: { type: Type.STRING },
                },
              },
              required: ["match_score", "fit_summary", "keywords_matched", "keywords_missing"],
            },
          },
        });

        const analysisResult = JSON.parse(response.text || "{}");
        job.ai_analysis = {
          id: Math.floor(Math.random() * 1000000),
          job_id: job.id,
          ...analysisResult,
          analyzed_at: new Date().toISOString(),
        };
        analyzedCount++;
      } catch (err) {
        console.warn(`Batch AI analyze failed for job ${job.id}. Using local fallback.`, err);
        const resumeSkills = Array.isArray(profile.key_skills) ? profile.key_skills : [];
        const jobDesc = (job.description_raw || "").toLowerCase();
        const matchedSkills = resumeSkills.filter(s => jobDesc.includes(s.toLowerCase()));
        const score = Math.min(Math.round((matchedSkills.length / Math.max(resumeSkills.length, 1)) * 100), 100) || 50;

        job.ai_analysis = {
          id: Math.floor(Math.random() * 1000000),
          job_id: job.id,
          match_score: score,
          fit_summary: "Local Match: Calculated using keyword intersection (AI fallback).",
          keywords_matched: matchedSkills,
          keywords_missing: [],
          analyzed_at: new Date().toISOString(),
        };
        analyzedCount++;
      }
    }

    saveDB(db);
    res.json({ analyzed_count: analyzedCount, jobs: db.jobs });
  } catch (error: any) {
    console.error("Batch alignment evaluate failed:", error);
    res.status(500).json({ error: error.message || "Batch alignment evaluation failed." });
  }
});

// 9. Outreach Recruiter DM Draft & Contact X-Ray search queries
app.post("/api/outreach", async (req, res) => {
  try {
    const { company_name, target_role } = req.body;

    if (!company_name) {
      return res.status(400).json({ error: "Company name is required." });
    }

    const roleTitle = target_role || "Territory Sales Executive";

    const prompt = `We want to construct recruiter outreach assets for the company "${company_name}" and job role "${roleTitle}".
Draft an elegant, polite, highly effective direct message (DM) template of 150-200 words that is optimized for LinkedIn connection messages or X/Twitter DMs. Use placeholders like [Your Name], [Company Name], and [Role Name] where needed.
Also suggest direct Google X-Ray search query URLs (LinkedIn, Twitter) that locate founders, hiring managers, or talent acquisition representatives for that company.
Return the result in the requested JSON format.`;

    const response = await ai.models.generateContent({
      model: getModel(req.body.model),
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            cold_outreach_dm_template: { type: Type.STRING },
            suggested_search_queries: {
              type: Type.OBJECT,
              properties: {
                linkedin_recruiters: { type: Type.STRING, description: "Google X-Ray query URL to search LinkedIn recruiters of this company" },
                linkedin_founders: { type: Type.STRING, description: "Google X-Ray query URL to search founders of this company" },
                twitter_hiring: { type: Type.STRING, description: "Google X-Ray query URL to search X/Twitter accounts related to hiring in this company" },
              },
              required: ["linkedin_recruiters", "linkedin_founders", "twitter_hiring"],
            },
          },
          required: ["cold_outreach_dm_template", "suggested_search_queries"],
        },
      },
    });

    const result = JSON.parse(response.text || "{}");

    // Replace the URL with ready-to-click URLs if needed, but since we asked the model to generate them, we can format them or keep them.
    // Let's ensure they are actual URLs or clean Google search links
    const formatSearchUrl = (queryText: string) => `https://www.google.com/search?q=${encodeURIComponent(queryText)}`;
    
    // We override or ensure they are solid search links
    const l_rec = `site:linkedin.com/in "${company_name}" AND ("recruiter" OR "talent acquisition" OR "hiring manager")`;
    const l_fnd = `site:linkedin.com/in "${company_name}" AND ("founder" OR "co-founder" OR "ceo")`;
    const t_hir = `site:twitter.com "${company_name}" ("hiring" OR "jobs" OR "recruiter")`;

    res.json({
      cold_outreach_dm_template: result.cold_outreach_dm_template,
      suggested_search_queries: {
        "LinkedIn: Talent Acquisition & Recruiters": formatSearchUrl(l_rec),
        "LinkedIn: Founders & CEOs": formatSearchUrl(l_fnd),
        "X (Twitter): Hiring Handles": formatSearchUrl(t_hir),
      },
    });
  } catch (error: any) {
    console.warn("Outreach lookup failed. Using fallback templates.", error);
    const { company_name } = req.body;
    const l_rec = `site:linkedin.com/in/ ("recruiter" OR "talent acquisition" OR "human resources") "${company_name}"`;
    const l_fnd = `site:linkedin.com/in/ ("founder" OR "ceo" OR "cto" OR "engineering manager") "${company_name}"`;
    const t_hir = `site:twitter.com "${company_name}" ("hiring" OR "jobs" OR "recruiter")`;
    
    res.json({
      cold_outreach_dm_template: `Hi team at ${company_name},\n\nI noticed you are doing interesting work and I'm currently looking for new opportunities. I have a background in software development and would love to connect to see if there is a mutual fit.\n\nBest,\n[Your Name]`,
      suggested_search_queries: {
        "LinkedIn: Talent Acquisition & Recruiters": formatSearchUrl(l_rec),
        "LinkedIn: Founders & CEOs": formatSearchUrl(l_fnd),
        "X (Twitter): Hiring Handles": formatSearchUrl(t_hir),
      },
      fallback: true
    });
  }
});

// 10. Clean / Purge Duplicate & Applied Jobs from database
app.post("/api/jobs/purge", (req, res) => {
  const db = loadDB();
  const initialLength = db.jobs.length;

  // Filter out duplicates (same title + company) that are NOT actively tracked
  const uniqueTrackedOrFirst: any[] = [];
  const seenKeys = new Set<string>();

  db.jobs.forEach((j) => {
    const key = `${j.title.toLowerCase().trim()}::${j.company_name.toLowerCase().trim()}`;
    if (j.application) {
      // Always keep actively tracked jobs
      uniqueTrackedOrFirst.push(j);
      seenKeys.add(key);
    } else if (!seenKeys.has(key)) {
      uniqueTrackedOrFirst.push(j);
      seenKeys.add(key);
    }
  });

  db.jobs = uniqueTrackedOrFirst;
  saveDB(db);

  res.json({
    purged_count: initialLength - db.jobs.length,
    jobs: db.jobs,
  });
});

// 11. Generate Styled Excel Export (.xlsx)
app.get("/api/export", (req, res) => {
  try {
    const { status_filter } = req.query;
    const db = loadDB();

    let filteredJobs = db.jobs;
    if (status_filter && status_filter !== "All") {
      filteredJobs = db.jobs.filter(
        (j) => j.application && j.application.status === status_filter
      );
    }

    // Format rows for Excel sheet
    const excelRows = filteredJobs.map((j) => ({
      "Job Title": j.title,
      Company: j.company_name,
      Location: j.location,
      "Workplace Type": j.work_place_type,
      "Job Type": j.job_type,
      "Source Portal": j.source,
      "Match Score (%)": j.ai_analysis ? `${j.ai_analysis.match_score}%` : "Not Evaluated",
      "Tracking Status": j.application ? j.application.status : "Untracked",
      "Tracking Notes": j.application ? j.application.notes || "" : "",
      "Application Link": j.url,
      "Date Ingested": j.date_scraped ? j.date_scraped.substring(0, 16).replace("T", " ") : "",
    }));

    const worksheet = XLSX.utils.json_to_sheet(excelRows);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Discovered Jobs");

    // Write workbook to memory buffer
    const wopts: XLSX.WritingOptions = { bookType: "xlsx", type: "buffer" };
    const excelBuffer = XLSX.write(workbook, wopts);

    res.setHeader(
      "Content-Type",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    );
    res.setHeader(
      "Content-Disposition",
      `attachment; filename="JobHunterAI_Export_${status_filter || "All"}.xlsx"`
    );
    res.send(excelBuffer);
  } catch (err: any) {
    console.error("Excel generation failed:", err);
    res.status(500).json({ error: "Failed to generate Excel sheet" });
  }
});

// ----------------------------------------------------------------------
// Vite Middleware / Static Files Setup
// ----------------------------------------------------------------------
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
