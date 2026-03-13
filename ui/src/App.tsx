import { Overlay } from './components/Overlay';
import { ModelManager } from './components/ModelManager';
import { Settings } from './components/Settings';
import { useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { getCurrentWindow } from '@tauri-apps/api/window';
import { useStore } from './store';

function App() {
  const { appendOutput, setIsGenerating, setShowModelManager, setShowSettings } = useStore();

  useEffect(() => {
    const handleKeyDown = async (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        const win = getCurrentWindow();
        await win.hide();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    
    // Listen for streaming tokens
    const unlistenToken = listen<string>('token', (e) => {
      appendOutput(e.payload);
    });
    
    // Listen for generation complete
    const unlistenDone = listen('done', () => {
      setIsGenerating(false);
    });
    
    // Listen for hotkey to show window
    const unlistenShow = listen('show-window', async () => {
      const win = getCurrentWindow();
      await win.show();
      await win.setFocus();
    });

    const unlistenOpenModels = listen('open-models', () => {
      setShowModelManager(true);
    });

    const unlistenOpenSettings = listen('open-settings', () => {
      setShowSettings(true);
    });

    const unlistenContext = listen<any>('context-received', async (e) => {
      const ctx = e.payload;
      const state = useStore.getState();
      let task = state.activeTask;

      if (ctx.screenshot_path && !['caption', 'navigate'].includes(task)) {
        task = 'navigate';
        useStore.setState({ activeTask: 'navigate' });
      }

      const req = {
        task: task,
        text: ctx.text_before || '',
        context: {
          process_name: ctx.process_name || '',
          window_title: ctx.window_title || '',
          text_before: ctx.text_before || '',
          text_after: ctx.text_after || '',
          screenshot_path: ctx.screenshot_path || null
        },
        image_path: ctx.screenshot_path || null,
        stream: true
      };

      useStore.setState({ outputStream: '', isGenerating: true });
      try {
        await invoke('run_inference', { request: req });
      } catch (err) {
        console.error("Inference failed:", err);
        useStore.setState({ isGenerating: false });
      }
    });

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      unlistenToken.then(f => f());
      unlistenDone.then(f => f());
      unlistenShow.then(f => f());
      unlistenOpenModels.then(f => f());
      unlistenOpenSettings.then(f => f());
      unlistenContext.then(f => f());
    };
  }, [appendOutput, setIsGenerating, setShowModelManager, setShowSettings]);

  return (
    <div className="flex flex-col h-screen w-full rounded-xl bg-gray-900/90 border border-gray-700 shadow-2xl backdrop-blur-md p-4 relative overflow-hidden">
      <Overlay />
      <ModelManager />
      <Settings />
    </div>
  );
}

export default App;