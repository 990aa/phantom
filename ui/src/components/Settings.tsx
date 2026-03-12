import { useStore } from '../store';
import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';

export function Settings() {
  const { showSettings, setShowSettings } = useStore();
  const [hotkey, setHotkey] = useState('Ctrl+Space');
  const [learnStyle, setLearnStyle] = useState(true);
  const [rulebook, setRulebook] = useState('');
  const [showRulebook, setShowRulebook] = useState(false);

  useEffect(() => {
    if (showSettings) {
      invoke<string>('get_style_rulebook').then(setRulebook).catch(console.error);
    }
  }, [showSettings]);

  const handleClearData = async () => {
    await invoke('clear_message_log');
    await invoke('clear_style_data');
    setRulebook('');
  };

  if (!showSettings) return null;

  return (
    <div className="flex flex-col h-full bg-gray-900 absolute inset-0 z-50 p-4 rounded-xl">
      <div className="flex justify-between items-center pb-2 border-b border-gray-700">
        <h2 className="text-sm font-semibold text-gray-200">Settings</h2>
        <button onClick={() => setShowSettings(false)} className="text-gray-400 hover:text-white">✕</button>
      </div>

      <div className="flex-1 overflow-y-auto mt-4 space-y-4 text-sm text-gray-200 pr-2">
        <div>
          <label className="block text-xs text-gray-400 mb-1">Global Hotkey</label>
          <input 
            type="text" 
            value={hotkey}
            onChange={e => setHotkey(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white outline-none" 
          />
        </div>
        
        <div className="border-t border-gray-700 pt-4">
          <label className="flex items-center space-x-2">
            <input type="checkbox" checked={learnStyle} onChange={e => setLearnStyle(e.target.checked)} className="accent-blue-600 bg-gray-800" />
            <span className="text-xs">Learn my writing style</span>
          </label>
          <p className="text-[10px] text-gray-500 mt-1">
            Logs sent messages locally to distill your tone. All data is processed entirely offline on your device and never sent to any cloud.
          </p>
        </div>

        <div>
          <button onClick={() => setShowRulebook(!showRulebook)} className="text-xs text-blue-400 hover:text-blue-300">
            {showRulebook ? 'Hide' : 'View'} My Style Rulebook
          </button>
          {showRulebook && (
            <div className="mt-2 p-2 bg-gray-800 rounded border border-gray-700 text-xs italic text-gray-300 min-h-[40px]">
              {rulebook || "No style rules generated yet. Keep typing!"}
            </div>
          )}
        </div>
        
        <div className="border-t border-gray-700 pt-4 pb-4">
          <button onClick={handleClearData} className="w-full bg-red-900/50 hover:bg-red-900 text-red-200 text-xs py-2 rounded font-medium border border-red-800 transition-colors">
            Delete Personalization Data
          </button>
          <p className="text-[10px] text-gray-500 mt-1">Deletes all context logs and the distilled style rulebook from local storage.</p>
        </div>
      </div>
    </div>
  );
}