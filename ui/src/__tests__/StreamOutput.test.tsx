import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StreamOutput } from '../components/StreamOutput';
import { useStore } from '../store';

// Mock scrollIntoView
window.HTMLElement.prototype.scrollIntoView = function() {};

describe('StreamOutput', () => {
  it('shows waiting text when empty and not generating', () => {
    useStore.setState({ outputStream: '', isGenerating: false });
    render(<StreamOutput />);
    expect(screen.getByText('Waiting for context...')).toBeInTheDocument();
  });

  it('shows streamed tokens', () => {
    useStore.setState({ outputStream: 'Hello World', isGenerating: true });
    render(<StreamOutput />);
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });
});