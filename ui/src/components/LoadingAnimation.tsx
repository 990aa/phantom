import { useStore } from '../store';

export function LoadingAnimation() {
  const { isGenerating } = useStore();

  if (!isGenerating) return null;

  return (
    <div className="flex items-center space-x-2 text-xs text-blue-400 animate-pulse pb-2">
      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      <span>Loading Model...</span>
    </div>
  );
}