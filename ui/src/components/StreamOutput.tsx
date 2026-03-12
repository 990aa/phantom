import { useStore } from '../store';
import { useEffect, useRef } from 'react';

export function StreamOutput() {
  const { outputStream, isGenerating } = useStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [outputStream]);

  return (
    <div className="flex-1 overflow-y-auto mt-2 text-sm text-gray-200 p-2 bg-gray-800/50 rounded-lg whitespace-pre-wrap font-mono">
      {outputStream || (isGenerating ? '' : 'Waiting for context...')}
      <div ref={bottomRef} />
    </div>
  );
}