import { useStore } from '../store';

export function CustomPrompt() {
  const { activeTask, isGenerating } = useStore();

  if (activeTask !== 'custom') return null;

  return (
    <div className="mt-2">
      <input 
        type="text" 
        placeholder="Enter custom instruction..." 
        disabled={isGenerating}
        className="w-full bg-gray-800 text-gray-200 text-xs px-3 py-2 rounded-md outline-none border border-gray-700 focus:border-blue-500"
      />
    </div>
  );
}