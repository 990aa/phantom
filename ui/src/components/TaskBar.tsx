import { useStore } from '../store';

const tasks = ['Summarize', 'Simplify', 'Explain', 'Reply', 'Continue', 'Caption', 'Navigate', 'Custom'];

export function TaskBar() {
  const { activeTask, setActiveTask, isGenerating } = useStore();

  return (
    <div className="flex space-x-2 overflow-x-auto pb-2 scrollbar-hide">
      {tasks.map((task) => {
        const isActive = activeTask.toLowerCase() === task.toLowerCase();
        return (
          <button
            key={task}
            disabled={isGenerating}
            onClick={() => setActiveTask(task.toLowerCase())}
            className={`px-3 py-1 text-xs rounded-full whitespace-nowrap transition-colors ${
              isActive 
                ? 'bg-blue-600 text-white font-medium' 
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            } ${isGenerating ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {task}
          </button>
        );
      })}
    </div>
  );
}