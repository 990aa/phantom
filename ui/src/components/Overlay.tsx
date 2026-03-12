import { TaskBar } from './TaskBar';
import { StreamOutput } from './StreamOutput';
import { ModelBadge } from './ModelBadge';
import { LoadingAnimation } from './LoadingAnimation';
import { CustomPrompt } from './CustomPrompt';
import { useStore } from '../store';

export function Overlay() {
  const { showModelManager, showSettings, setShowSettings } = useStore();

  if (showModelManager || showSettings) return null;

  return (
    <>
      <div className="flex justify-between items-center pb-2 border-b border-gray-700/50">
        <h1 className="text-sm font-semibold text-gray-300 tracking-wide flex items-center space-x-2">
          <span>Phantom</span>
          <button onClick={() => setShowSettings(true)} className="text-gray-500 hover:text-gray-300">⚙</button>
        </h1>
        <ModelBadge />
      </div>
      
      <div className="mt-3">
        <TaskBar />
      </div>
      
      <CustomPrompt />
      
      <div className="mt-2 flex-1 flex flex-col min-h-[150px]">
        <LoadingAnimation />
        <StreamOutput />
      </div>
    </>
  );
}