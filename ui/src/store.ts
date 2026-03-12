import { create } from 'zustand';

interface StoreState {
  activeTask: string;
  setActiveTask: (task: string) => void;
  showModelManager: boolean;
  setShowModelManager: (show: boolean) => void;
  showSettings: boolean;
  setShowSettings: (show: boolean) => void;
  isGenerating: boolean;
  setIsGenerating: (gen: boolean) => void;
  outputStream: string;
  setOutputStream: (stream: string) => void;
  appendOutput: (text: string) => void;
  activeModelName: string;
  setActiveModelName: (name: string) => void;
}

export const useStore = create<StoreState>((set) => ({
  activeTask: 'summarize',
  setActiveTask: (task) => set({ activeTask: task }),
  showModelManager: false,
  setShowModelManager: (show) => set({ showModelManager: show }),
  showSettings: false,
  setShowSettings: (show) => set({ showSettings: show }),
  isGenerating: false,
  setIsGenerating: (gen) => set({ isGenerating: gen }),
  outputStream: '',
  setOutputStream: (stream) => set({ outputStream: stream }),
  appendOutput: (text) => set((state) => ({ outputStream: state.outputStream + text })),
  activeModelName: 'Qwen3.5-0.8B',
  setActiveModelName: (name) => set({ activeModelName: name }),
}));