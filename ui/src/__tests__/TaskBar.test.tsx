import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { TaskBar } from '../components/TaskBar';
import { useStore } from '../store';

describe('TaskBar', () => {
  it('renders all 8 task buttons', () => {
    render(<TaskBar />);
    const buttons = screen.getAllByRole('button');
    expect(buttons).toHaveLength(8);
  });

  it('highlights the active task', () => {
    useStore.setState({ activeTask: 'simplify' });
    render(<TaskBar />);
    const simplifyBtn = screen.getByText('Simplify');
    expect(simplifyBtn).toHaveClass('bg-blue-600');
  });

  it('changes active task on click', () => {
    render(<TaskBar />);
    const explainBtn = screen.getByText('Explain');
    fireEvent.click(explainBtn);
    expect(useStore.getState().activeTask).toBe('explain');
  });
});