import { useState, useEffect } from 'react';
import { useStore } from '../store';
import { invoke } from '@tauri-apps/api/core';

interface ModelInfo {
  id: string;
  name: string;
  type: string;
  size_bytes: number | null;
  is_downloaded: boolean;
  is_default_text: boolean;
  is_default_vision: boolean;
}

export function ModelManager() {
  const { showModelManager, setShowModelManager, setActiveModelName } = useStore();
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [customUrl, setCustomUrl] = useState('');
  const [customName, setCustomName] = useState('');
  const [customType, setCustomType] = useState('text');

  useEffect(() => {
    if (showModelManager) {
      loadModels();
    }
  }, [showModelManager]);

  const loadModels = async () => {
    try {
      const data: ModelInfo[] = await invoke('get_models');
      setModels(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleDownload = async (repo: string, filename: string) => {
    try {
      await invoke('download_model', { hfRepo: repo, filename });
      loadModels();
    } catch(e) {
      console.error(e);
    }
  };

  const handleSetDefault = async (id: string, type: string) => {
    try {
      await invoke('set_default_model', { modelId: id, modelType: type });
      const m = models.find(x => x.id === id);
      if(m) setActiveModelName(m.name);
      loadModels();
    } catch(e) {
      console.error(e);
    }
  };

  if (!showModelManager) return null;

  return (
    <div className="flex flex-col h-full bg-gray-900 absolute inset-0 z-50 p-4 rounded-xl">
      <div className="flex justify-between items-center pb-2 border-b border-gray-700">
        <h2 className="text-sm font-semibold text-gray-200">Model Manager</h2>
        <button onClick={() => setShowModelManager(false)} className="text-gray-400 hover:text-white">✕</button>
      </div>

      <div className="flex-1 overflow-y-auto mt-2 space-y-3 pr-2 scrollbar-hide">
        {models.map(m => (
          <div key={m.id} className="bg-gray-800 p-2 rounded-lg border border-gray-700">
            <div className="flex justify-between items-center">
              <div>
                <span className="text-sm text-gray-200 font-medium">{m.name}</span>
                <span className="ml-2 text-[10px] bg-gray-700 px-1.5 py-0.5 rounded text-gray-400 uppercase">{m.type}</span>
              </div>
              {m.is_default_text || m.is_default_vision ? <span className="text-yellow-500 text-xs">★ Default</span> : null}
            </div>
            
            <div className="flex justify-between items-center mt-2">
              <span className="text-xs text-gray-500">{m.is_downloaded ? 'Downloaded' : 'Not Downloaded'}</span>
              <div className="space-x-2">
                {!m.is_downloaded && (
                  <button onClick={() => handleDownload(m.hf_repo, m.filename)} className="text-xs bg-blue-600 hover:bg-blue-500 px-2 py-1 rounded text-white">Download</button>
                )}
                {m.is_downloaded && (
                  <button onClick={() => handleSetDefault(m.id, m.type)} className="text-xs bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded text-white">Set Default</button>
                )}
              </div>
            </div>
          </div>
        ))}

        <div className="mt-4 border-t border-gray-700 pt-4">
          <h3 className="text-xs font-semibold text-gray-400 mb-2">Add Custom GGUF</h3>
          <input 
            type="text" 
            placeholder="Model Name" 
            value={customName}
            onChange={e => setCustomName(e.target.value)}
            className="w-full text-xs bg-gray-800 border border-gray-700 rounded p-2 mb-2 text-white outline-none focus:border-blue-500" 
          />
          <input 
            type="text" 
            placeholder="HuggingFace URL" 
            value={customUrl}
            onChange={e => setCustomUrl(e.target.value)}
            className="w-full text-xs bg-gray-800 border border-gray-700 rounded p-2 mb-2 text-white outline-none focus:border-blue-500" 
          />
          <select 
            value={customType} 
            onChange={e => setCustomType(e.target.value)}
            className="w-full text-xs bg-gray-800 border border-gray-700 rounded p-2 mb-2 text-white outline-none focus:border-blue-500"
          >
            <option value="text">Text Model</option>
            <option value="vision">Vision Model</option>
          </select>
          <button className="w-full bg-blue-600 hover:bg-blue-500 text-white text-xs py-2 rounded font-medium">Add Model</button>
        </div>
      </div>
    </div>
  );
}