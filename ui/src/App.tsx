import { Overlay } from './components/Overlay';
import { ModelManager } from './components/ModelManager';
import { Settings } from './components/Settings';
import { useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { getCurrentWindow } from '@tauri-apps/api/window';
import { useStore } from './store';

function App() {
  const { appendOutput, setIsGenerating } = useStore();

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

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      unlistenToken.then(f => f());
      unlistenDone.then(f => f());
      unlistenShow.then(f => f());
    };
  }, [appendOutput, setIsGenerating]);

  return (
    <div className="flex flex-col h-screen w-full rounded-xl bg-gray-900/90 border border-gray-700 shadow-2xl backdrop-blur-md p-4 relative overflow-hidden">
      <Overlay />
      <ModelManager />
      <Settings />
    </div>
  );
}

export default App;