import { create } from 'zustand';

interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  login: (user: User, token: string) => void;
  logout: () => void;
  setError: (error: string | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('access_token'),
  isLoading: false,
  error: null,
  login: (user, token) => {
    set({ user, token });
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('access_token', token);
  },
  logout: () => {
    set({ user: null, token: null });
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
  },
  setError: (error) => set({ error }),
}));

interface ProjectsState {
  projects: any[];
  isLoading: boolean;
  setProjects: (projects: any[]) => void;
  addProject: (project: any) => void;
  removeProject: (id: number) => void;
  setLoading: (loading: boolean) => void;
}

export const useProjectsStore = create<ProjectsState>((set) => ({
  projects: [],
  isLoading: false,
  setProjects: (projects) => set({ projects }),
  addProject: (project) => set((state) => ({ projects: [project, ...state.projects] })),
  removeProject: (id) => set((state) => ({ projects: state.projects.filter(p => p.id !== id) })),
  setLoading: (loading) => set({ isLoading: loading }),
}));
