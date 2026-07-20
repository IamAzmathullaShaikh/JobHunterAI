import React from 'react';
import { JobListing, ApplicationStatus } from '../types';
import { Droppable, Draggable } from 'react-beautiful-dnd';
import { GripVertical, Clock } from 'lucide-react';

interface KanbanColumnProps {
  status: ApplicationStatus;
  jobs: JobListing[];
}

export const KanbanColumn: React.FC<KanbanColumnProps> = ({ status, jobs }) => {
  return (
    <div className="bg-panel rounded-xl shadow-soft border border-slate-800 flex flex-col h-full overflow-hidden w-72 flex-shrink-0">
      <div className="p-3 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
        <h3 className="text-sm font-semibold text-white">{status}</h3>
        <span className="bg-surface text-slate-400 text-xs px-2 py-0.5 rounded-full font-medium">
          {jobs.length}
        </span>
      </div>
      
      <Droppable droppableId={status}>
        {(provided, snapshot) => (
          <div 
            ref={provided.innerRef} 
            {...provided.droppableProps}
            className={`flex-1 p-3 overflow-y-auto min-h-[150px] transition-colors ${
              snapshot.isDraggingOver ? 'bg-primary/5' : 'bg-transparent'
            }`}
          >
            {jobs.map((job, index) => (
              <Draggable key={job.id.toString()} draggableId={job.id.toString()} index={index}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.draggableProps}
                    className={`bg-surface border p-3 rounded-lg mb-3 flex flex-col gap-2 shadow-sm relative group ${
                      snapshot.isDragging ? 'border-primary shadow-primary/20 rotate-1 z-10' : 'border-slate-700 hover:border-slate-500'
                    }`}
                  >
                    <div 
                      {...provided.dragHandleProps}
                      className="absolute top-2 right-2 text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity cursor-grab"
                    >
                      <GripVertical className="w-4 h-4" />
                    </div>
                    
                    <h4 className="text-sm font-semibold text-white pr-6 leading-tight">{job.title}</h4>
                    <p className="text-xs text-slate-400">{job.company_name}</p>
                    
                    <div className="flex justify-between items-center mt-1 pt-2 border-t border-slate-800/50">
                      <span className="text-[10px] text-slate-500 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {job.application?.date_updated ? new Date(job.application.date_updated).toLocaleDateString() : 'Recent'}
                      </span>
                      {job.ai_analysis && (
                        <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded font-medium">
                          {job.ai_analysis.match_score}% Match
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </Draggable>
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </div>
  );
};
