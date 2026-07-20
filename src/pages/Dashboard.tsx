import React, { useState } from 'react';
import { DragDropContext, DropResult } from 'react-beautiful-dnd';
import { UploadCard } from '../components/UploadCard';
import { JobCard } from '../components/JobCard';
import { ProfileCard } from '../components/ProfileCard';
import { SearchPanel } from '../components/SearchPanel';
import { KanbanColumn } from '../components/KanbanColumn';
import { ApplicationStatus, JobListing, CandidateProfile } from '../types';

// Mock Data
const mockProfile: CandidateProfile = {
  full_name: 'Alex Developer',
  total_experience_years: 4,
  education: ['B.S. Computer Science, Tech University'],
  key_skills: ['React', 'TypeScript', 'Node.js', 'Tailwind CSS', 'GraphQL', 'AWS'],
  recommended_search_queries: ['Frontend Engineer', 'React Developer'],
  experience_highlights: ['Built a scalable platform with 10k users']
};

const mockJobs: JobListing[] = Array.from({ length: 6 }).map((_, i) => ({
  id: i + 1,
  job_id_raw: `mock-${i}`,
  title: ['Senior React Developer', 'Frontend Engineer', 'Full Stack Developer', 'UI Engineer'][i % 4],
  company_name: ['TechCorp', 'InnoSoft', 'CloudWorks', 'DataSys'][i % 4],
  location: ['Remote', 'New York, NY', 'San Francisco, CA'][i % 3],
  work_place_type: ['Remote', 'Hybrid', 'Onsite'][i % 3],
  job_type: 'Full-Time',
  source: 'LinkedIn',
  url: 'https://example.com/job',
  canonical_url: 'https://example.com/job-canonical',
  raw_url: 'https://example.com/job',
  description_raw: 'We are looking for an experienced developer to join our growing team. You will work on cutting-edge technologies...',
  ai_analysis: {
    id: i,
    job_id: i + 1,
    match_score: 95 - (i * 10),
    fit_summary: 'Good match based on skills.',
    keywords_matched: ['React', 'TypeScript'],
    keywords_missing: ['Python']
  }
}));

const mockKanbanJobs: JobListing[] = [
  { ...mockJobs[0], id: 101, application: { id: 1, job_id: 101, status: ApplicationStatus.IDENTIFIED } },
  { ...mockJobs[1], id: 102, application: { id: 2, job_id: 102, status: ApplicationStatus.IDENTIFIED } },
  { ...mockJobs[2], id: 103, application: { id: 3, job_id: 103, status: ApplicationStatus.APPLIED } }
];

export const Dashboard: React.FC = () => {
  const [searchFields, setSearchFields] = useState({ query: '', location: '', jobType: 'Full-Time' });
  const [kanbanData, setKanbanData] = useState(mockKanbanJobs);

  const handleDragEnd = (result: DropResult) => {
    if (!result.destination) return;
    const { source, destination, draggableId } = result;
    if (source.droppableId === destination.droppableId) return;

    setKanbanData(prev => prev.map(job => 
      job.id.toString() === draggableId && job.application 
        ? { ...job, application: { ...job.application, status: destination.droppableId as ApplicationStatus } } 
        : job
    ));
  };

  return (
    <div className="min-h-screen bg-[#0B1220] text-slate-200 font-sans p-6">
      <div className="max-w-[1400px] mx-auto">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">JobHunter AI</h1>
            <p className="text-slate-400 mt-1">Your personal, local-first career copilot</p>
          </div>
          <div className="flex gap-3">
            <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1.5 rounded-md text-sm font-medium flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              AI Engine Ready
            </span>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Sidebar */}
          <div className="lg:col-span-3 space-y-6">
            <ProfileCard profile={mockProfile} />
            <SearchPanel 
              fields={searchFields} 
              onChange={setSearchFields} 
              onSearch={() => alert('Search triggered')}
              suggestions={['React Developer', 'Frontend Engineer', 'Remote']}
            />
            <UploadCard 
              onFileUpload={(file) => alert(`Uploaded ${file.name}`)}
              onPasteText={(text) => alert(`Pasted ${text.length} chars`)}
            />
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-6 space-y-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">Recommended Jobs</h2>
              <span className="text-sm text-slate-400">{mockJobs.length} matches</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {mockJobs.map(job => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>
          </div>

          {/* Right Sidebar - Mini Kanban */}
          <div className="lg:col-span-3">
            <h2 className="text-xl font-bold text-white mb-4">Active Pipeline</h2>
            <div className="h-[calc(100vh-140px)] overflow-x-auto pb-4">
              <DragDropContext onDragEnd={handleDragEnd}>
                <div className="flex gap-4 h-full">
                  <KanbanColumn 
                    status={ApplicationStatus.IDENTIFIED} 
                    jobs={kanbanData.filter(j => j.application?.status === ApplicationStatus.IDENTIFIED)} 
                  />
                  <KanbanColumn 
                    status={ApplicationStatus.APPLIED} 
                    jobs={kanbanData.filter(j => j.application?.status === ApplicationStatus.APPLIED)} 
                  />
                </div>
              </DragDropContext>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
