import { Overlay } from './components/Overlay';
import { ModelManager } from './components/ModelManager';
import { Settings } from './components/Settings';
import { useEffect } from 'react';

function App() {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        // Hide window instead of closing
        // invoke('hide_window');
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="flex flex-col h-screen w-full rounded-xl bg-gray-900/90 border border-gray-700 shadow-2xl backdrop-blur-md p-4 relative overflow-hidden">
      <Overlay />
      <ModelManager />
      <Settings />
    </div>
  );
}

export default App;