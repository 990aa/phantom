import { useStore } from '../store';

export function ModelBadge() {
  const { activeModelName, setShowModelManager, isGenerating } = useStore();

  return (
    <button 
      onClick={() => setShowModelManager(true)}
      disabled={isGenerating}
      className="text-xs bg-gray-800 text-gray-300 px-2 py-1 rounded-md hover:bg-gray-700 transition-colors border border-gray-700"
    >
      {activeModelName} ▾
    </button>
  );
}