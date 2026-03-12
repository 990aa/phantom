import { useStore } from '../store';
import { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';

export function Settings() {
  const { showSettings, setShowSettings } = useStore();
  const [hotkey, setHotkey] = useState('Ctrl+Space');

  if (!showSettings) return null;

  return (
    <div className="flex flex-col h-full bg-gray-900 absolute inset-0 z-50 p-4 rounded-xl">
      <div className="flex justify-between items-center pb-2 border-b border-gray-700">
        <h2 className="text-sm font-semibold text-gray-200">Settings</h2>
        <button onClick={() => setShowSettings(false)} className="text-gray-400 hover:text-white">✕</button>
      </div>

      <div className="flex-1 mt-4 space-y-4 text-sm text-gray-200">
        <div>
          <label className="block text-xs text-gray-400 mb-1">Global Hotkey</label>
          <input 
            type="text" 
            value={hotkey}
            onChange={e => setHotkey(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white outline-none" 
          />
        </div>
        
        <div>
          <button onClick={() => invoke('clear_message_log')} className="w-full bg-red-900/50 hover:bg-red-900 text-red-200 text-xs py-2 rounded font-medium border border-red-800">
            Clear Message History
          </button>
          <p className="text-xs text-gray-500 mt-1">Deletes all context logs used for style distillation.</p>
        </div>
      </div>
    </div>
  );
}