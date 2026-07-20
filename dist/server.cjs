"use strict";
var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));

// server.ts
var import_express = __toESM(require("express"), 1);
var import_cors = __toESM(require("cors"), 1);
var import_fs = __toESM(require("fs"), 1);
var import_path = __toESM(require("path"), 1);
var import_url = require("url");
var import_vite = require("vite");
var import_genai = require("@google/genai");
var XLSX = __toESM(require("xlsx"), 1);
var import_meta = {};
var __filename = (0, import_url.fileURLToPath)(import_meta.url);
var __dirname = import_path.default.dirname(__filename);
var app = (0, import_express.default)();
var PORT = 3e3;
app.use((0, import_cors.default)());
app.use(import_express.default.json({ limit: "50mb" }));
var ai = new import_genai.GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
  httpOptions: {
    headers: {
      "User-Agent": "aistudio-build"
    }
  }
});
var DB_FILE = import_path.default.join(process.cwd(), "db.json");
function loadDB() {
  if (import_fs.default.existsSync(DB_FILE)) {
    try {
      const content = import_fs.default.readFileSync(DB_FILE, "utf-8");
      return JSON.parse(content);
    } catch (e) {
      console.error("Error reading database file, resetting:", e);
    }
  }
  return { profile: null, jobs: [] };
}
function saveDB(data) {
  try {
    import_fs.default.writeFileSync(DB_FILE, JSON.stringify(data, null, 2), "utf-8");
  } catch (e) {
    console.error("Error saving database file:", e);
  }
}
app.get("/api/profile", (req, res) => {
  const db = loadDB();
  res.json({ profile: db.profile });
});
app.post("/api/profile/parse", async (req, res) => {
  try {
    const { text, fileBase64, fileName, fileType } = req.body;
    let geminiContents = [];
    if (fileBase64 && fileType === "application/pdf") {
      geminiContents.push({
        inlineData: {
          data: fileBase64.split(",")[1] || fileBase64,
          mimeType: "application/pdf"
        }
      });
      geminiContents.push(
        "Analyze the uploaded resume PDF. Extract the professional capabilities, full name, education, total years of experience, key skills, suggested search queries for job engines, and 3 experience highlights. Return the data in the requested JSON format."
      );
    } else {
      const resumeContent = text || "No resume text provided.";
      geminiContents.push(
        `Analyze the following resume text. Extract the candidate's professional capabilities, full name, education, total years of experience, key skills, recommended search queries for job engines, and 3 experience highlights.

Resume Text:
${resumeContent}`
      );
    }
    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: geminiContents,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: import_genai.Type.OBJECT,
          properties: {
            full_name: { type: import_genai.Type.STRING },
            total_experience_years: { type: import_genai.Type.NUMBER },
            education: {
              type: import_genai.Type.ARRAY,
              items: { type: import_genai.Type.STRING }
            },
            key_skills: {
              type: import_genai.Type.ARRAY,
              items: { type: import_genai.Type.STRING }
            },
            recommended_search_queries: {
              type: import_genai.Type.ARRAY,
              items: { type: import_genai.Type.STRING }
            },
            experience_highlights: {
              type: import_genai.Type.ARRAY,
              items: { type: import_genai.Type.STRING }
            }
          },
          required: [
            "full_name",
            "total_experience_years",
            "education",
            "key_skills",
            "recommended_search_queries",
            "experience_highlights"
          ]
        }
      }
    });
    const parsedJson = JSON.parse(response.text || "{}");
    const db = loadDB();
    db.profile = parsedJson;
    saveDB(db);
    res.json({ profile: parsedJson });
  } catch (error) {
    console.error("Resume Parsing failed:", error);
    res.status(500).json({ error: error.message || "Resume parsing failed." });
  }
});
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
      model: "gemini-3.5-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: import_genai.Type.ARRAY,
          items: {
            type: import_genai.Type.OBJECT,
            properties: {
              job_id_raw: { type: import_genai.Type.STRING },
              title: { type: import_genai.Type.STRING },
              company_name: { type: import_genai.Type.STRING },
              location: { type: import_genai.Type.STRING },
              work_place_type: { type: import_genai.Type.STRING },
              // Remote, Hybrid, Onsite
              job_type: { type: import_genai.Type.STRING },
              // Full-Time, Internship, Apprenticeship
              source: { type: import_genai.Type.STRING },
              // LinkedIn, Indeed, etc.
              url: { type: import_genai.Type.STRING },
              description_raw: { type: import_genai.Type.STRING },
              salary_min: { type: import_genai.Type.NUMBER },
              salary_max: { type: import_genai.Type.NUMBER },
              salary_currency: { type: import_genai.Type.STRING },
              salary_raw: { type: import_genai.Type.STRING }
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
              "description_raw"
            ]
          }
        }
      }
    });
    const crawledListings = JSON.parse(response.text || "[]");
    const db = loadDB();
    const existingIds = new Set(db.jobs.map((j) => j.job_id_raw));
    const newJobsAdded = [];
    crawledListings.forEach((item) => {
      if (!existingIds.has(item.job_id_raw)) {
        const id = db.jobs.length > 0 ? Math.max(...db.jobs.map((j) => j.id)) + 1 : 1;
        const newJob = {
          id,
          ...item,
          is_starred: false,
          date_scraped: (/* @__PURE__ */ new Date()).toISOString(),
          ai_analysis: null,
          application: null
        };
        db.jobs.push(newJob);
        newJobsAdded.push(newJob);
      }
    });
    saveDB(db);
    res.json({
      scraped_count: crawledListings.length,
      new_count: newJobsAdded.length,
      jobs: db.jobs
    });
  } catch (error) {
    console.error("Pipeline discovery failed:", error);
    res.status(500).json({ error: error.message || "Scrape discovery failed." });
  }
});
app.get("/api/jobs", (req, res) => {
  const db = loadDB();
  res.json({ jobs: db.jobs });
});
app.post("/api/jobs/track", (req, res) => {
  const { job_id } = req.body;
  const db = loadDB();
  const job = db.jobs.find((j) => j.id === Number(job_id));
  if (!job) {
    return res.status(404).json({ error: "Job listing not found." });
  }
  if (!job.application) {
    job.application = {
      id: Math.floor(Math.random() * 1e6),
      job_id: job.id,
      status: "Identified",
      notes: "",
      date_created: (/* @__PURE__ */ new Date()).toISOString(),
      date_updated: (/* @__PURE__ */ new Date()).toISOString()
    };
    saveDB(db);
  }
  res.json({ job });
});
app.put("/api/applications/:app_id", (req, res) => {
  const { app_id } = req.params;
  const { status, notes } = req.body;
  const db = loadDB();
  let updatedJob = null;
  db.jobs.forEach((j) => {
    if (j.application && j.application.id === Number(app_id)) {
      j.application.status = status;
      j.application.notes = notes || "";
      j.application.date_updated = (/* @__PURE__ */ new Date()).toISOString();
      updatedJob = j;
    }
  });
  if (!updatedJob) {
    return res.status(404).json({ error: "Application tracking card not found." });
  }
  saveDB(db);
  res.json({ job: updatedJob });
});
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
      model: "gemini-3.5-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: import_genai.Type.OBJECT,
          properties: {
            match_score: { type: import_genai.Type.NUMBER },
            fit_summary: { type: import_genai.Type.STRING },
            keywords_matched: {
              type: import_genai.Type.ARRAY,
              items: { type: import_genai.Type.STRING }
            },
            keywords_missing: {
              type: import_genai.Type.ARRAY,
              items: { type: import_genai.Type.STRING }
            }
          },
          required: [
            "match_score",
            "fit_summary",
            "keywords_matched",
            "keywords_missing"
          ]
        }
      }
    });
    const analysisResult = JSON.parse(response.text || "{}");
    const id = Math.floor(Math.random() * 1e6);
    job.ai_analysis = {
      id,
      job_id: job.id,
      ...analysisResult,
      analyzed_at: (/* @__PURE__ */ new Date()).toISOString()
    };
    saveDB(db);
    res.json({ job });
  } catch (error) {
    console.error("AI Analysis failed:", error);
    res.status(500).json({ error: error.message || "AI Analysis failed." });
  }
});
app.post("/api/jobs/analyze-pending", async (req, res) => {
  try {
    const { resume_text } = req.body;
    if (!resume_text) {
      return res.status(400).json({ error: "Resume text required." });
    }
    const db = loadDB();
    const pendingJobs = db.jobs.filter((j) => !j.ai_analysis);
    let analyzedCount = 0;
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
          model: "gemini-3.5-flash",
          contents: prompt,
          config: {
            responseMimeType: "application/json",
            responseSchema: {
              type: import_genai.Type.OBJECT,
              properties: {
                match_score: { type: import_genai.Type.NUMBER },
                fit_summary: { type: import_genai.Type.STRING },
                keywords_matched: {
                  type: import_genai.Type.ARRAY,
                  items: { type: import_genai.Type.STRING }
                },
                keywords_missing: {
                  type: import_genai.Type.ARRAY,
                  items: { type: import_genai.Type.STRING }
                }
              },
              required: ["match_score", "fit_summary", "keywords_matched", "keywords_missing"]
            }
          }
        });
        const analysisResult = JSON.parse(response.text || "{}");
        job.ai_analysis = {
          id: Math.floor(Math.random() * 1e6),
          job_id: job.id,
          ...analysisResult,
          analyzed_at: (/* @__PURE__ */ new Date()).toISOString()
        };
        analyzedCount++;
      } catch (err) {
        console.error(`Batch AI analyze failed for job ${job.id}:`, err);
      }
    }
    saveDB(db);
    res.json({ analyzed_count: analyzedCount, jobs: db.jobs });
  } catch (error) {
    console.error("Batch alignment evaluate failed:", error);
    res.status(500).json({ error: error.message || "Batch alignment evaluation failed." });
  }
});
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
      model: "gemini-3.5-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: import_genai.Type.OBJECT,
          properties: {
            cold_outreach_dm_template: { type: import_genai.Type.STRING },
            suggested_search_queries: {
              type: import_genai.Type.OBJECT,
              properties: {
                linkedin_recruiters: { type: import_genai.Type.STRING, description: "Google X-Ray query URL to search LinkedIn recruiters of this company" },
                linkedin_founders: { type: import_genai.Type.STRING, description: "Google X-Ray query URL to search founders of this company" },
                twitter_hiring: { type: import_genai.Type.STRING, description: "Google X-Ray query URL to search X/Twitter accounts related to hiring in this company" }
              },
              required: ["linkedin_recruiters", "linkedin_founders", "twitter_hiring"]
            }
          },
          required: ["cold_outreach_dm_template", "suggested_search_queries"]
        }
      }
    });
    const result = JSON.parse(response.text || "{}");
    const formatSearchUrl = (queryText) => `https://www.google.com/search?q=${encodeURIComponent(queryText)}`;
    const l_rec = `site:linkedin.com/in "${company_name}" AND ("recruiter" OR "talent acquisition" OR "hiring manager")`;
    const l_fnd = `site:linkedin.com/in "${company_name}" AND ("founder" OR "co-founder" OR "ceo")`;
    const t_hir = `site:twitter.com "${company_name}" ("hiring" OR "jobs" OR "recruiter")`;
    res.json({
      cold_outreach_dm_template: result.cold_outreach_dm_template,
      suggested_search_queries: {
        "LinkedIn: Talent Acquisition & Recruiters": formatSearchUrl(l_rec),
        "LinkedIn: Founders & CEOs": formatSearchUrl(l_fnd),
        "X (Twitter): Hiring Handles": formatSearchUrl(t_hir)
      }
    });
  } catch (error) {
    console.error("Outreach lookup failed:", error);
    res.status(500).json({ error: error.message || "Outreach generator failed." });
  }
});
app.post("/api/jobs/purge", (req, res) => {
  const db = loadDB();
  const initialLength = db.jobs.length;
  const uniqueTrackedOrFirst = [];
  const seenKeys = /* @__PURE__ */ new Set();
  db.jobs.forEach((j) => {
    const key = `${j.title.toLowerCase().trim()}::${j.company_name.toLowerCase().trim()}`;
    if (j.application) {
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
    jobs: db.jobs
  });
});
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
      "Date Ingested": j.date_scraped ? j.date_scraped.substring(0, 16).replace("T", " ") : ""
    }));
    const worksheet = XLSX.utils.json_to_sheet(excelRows);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Discovered Jobs");
    const wopts = { bookType: "xlsx", type: "buffer" };
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
  } catch (err) {
    console.error("Excel generation failed:", err);
    res.status(500).json({ error: "Failed to generate Excel sheet" });
  }
});
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await (0, import_vite.createServer)({
      server: { middlewareMode: true },
      appType: "spa"
    });
    app.use(vite.middlewares);
  } else {
    const distPath = import_path.default.join(process.cwd(), "dist");
    app.use(import_express.default.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(import_path.default.join(distPath, "index.html"));
    });
  }
  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}
startServer();
//# sourceMappingURL=server.cjs.map
