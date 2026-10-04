import React, { createContext, useContext, useState, useEffect } from 'react';
import { getProjects } from '../lib/api';

const ProjectContext = createContext();

export function ProjectProvider({ children }) {
  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProject] = useState(null);

  async function loadProjects() {
    try {
      const data = await getProjects();
      setProjects(data);
      if (data.length > 0 && !activeProject) {
        const saved = localStorage.getItem('dg_active_project');
        if (saved && data.find(p => p.id === parseInt(saved))) {
          setActiveProject(data.find(p => p.id === parseInt(saved)));
        } else {
          setActiveProject(data[0]);
        }
      }
    } catch (err) {
      console.error("Failed to load projects", err);
    }
  }

  useEffect(() => {
    if (typeof window !== 'undefined' && localStorage.getItem('dg_api_key')) {
      loadProjects();
    }
  }, []);

  const selectProject = (project) => {
    setActiveProject(project);
    localStorage.setItem('dg_active_project', project.id);
  };

  return (
    <ProjectContext.Provider value={{ projects, activeProject, selectProject, reloadProjects: loadProjects }}>
      {children}
    </ProjectContext.Provider>
  );
}

export function useProject() {
  return useContext(ProjectContext);
}
