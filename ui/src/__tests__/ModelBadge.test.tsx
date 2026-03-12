import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ModelBadge } from '../components/ModelBadge';
import { useStore } from '../store';

describe('ModelBadge', () => {
  it('displays the correct model name', () => {
    useStore.setState({ activeModelName: 'Test-Model-1.5B' });
    render(<ModelBadge />);
    expect(screen.getByText('Test-Model-1.5B ▾')).toBeInTheDocument();
  });
});