import { useEffect } from 'react';

function App() {
  useEffect(() => {
    // Hide window when clicking outside
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        // We will call Tauri API to hide window later
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="flex flex-col h-screen w-full rounded-xl bg-gray-900/90 border border-gray-700 shadow-2xl backdrop-blur-md p-4">
      <div className="flex justify-between items-center pb-2 border-b border-gray-700/50">
        <h1 className="text-sm font-semibold text-gray-300">Phantom</h1>
        <div className="text-xs text-green-400">Idle</div>
      </div>
      <div className="flex-1 overflow-y-auto mt-2 text-sm text-gray-200">
        <p>Waiting for context...</p>
      </div>
    </div>
  );
}

export default App;