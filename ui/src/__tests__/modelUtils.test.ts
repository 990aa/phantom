import { describe, it, expect } from 'vitest';
import { checkCompatibility } from '../utils/modelUtils';

describe('modelUtils', () => {
  it('returns true for text model and text task', () => {
    expect(checkCompatibility({ id: 'qwen', type: 'text' }, 'summarize')).toBe(true);
  });
  
  it('returns false for text model and vision task', () => {
    expect(checkCompatibility({ id: 'qwen', type: 'text' }, 'navigate')).toBe(false);
  });
  
  it('returns true for vision model and vision task', () => {
    expect(checkCompatibility({ id: 'moondream', type: 'vision' }, 'caption')).toBe(true);
  });
});