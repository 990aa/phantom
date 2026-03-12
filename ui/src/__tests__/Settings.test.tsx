import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Settings } from '../components/Settings';
import { useStore } from '../store';

vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(),
}));

describe('Settings', () => {
  it('renders nothing when showSettings is false', () => {
    useStore.setState({ showSettings: false });
    const { container } = render(<Settings />);
    expect(container.firstChild).toBeNull();
  });

  it('renders settings when showSettings is true', () => {
    useStore.setState({ showSettings: true });
    render(<Settings />);
    expect(screen.getByText('Global Hotkey')).toBeInTheDocument();
  });
});