interface ModelInfo {
  id: string;
  type: string;
}

export function checkCompatibility(model: ModelInfo, task: string): boolean {
  const visionTasks = ['caption', 'navigate'];
  const textTasks = ['summarize', 'simplify', 'explain', 'reply', 'continue', 'custom', 'distill'];
  
  if (visionTasks.includes(task)) {
    return model.type === 'vision';
  }
  if (textTasks.includes(task)) {
    return model.type === 'text';
  }
  return false;
}
