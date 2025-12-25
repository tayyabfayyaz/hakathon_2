import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TodoForm from '@/components/todos/TodoForm';

// Mock validation module
vi.mock('@/lib/validation', () => ({
  validateTodoTitle: (title: string) => {
    const trimmed = title?.trim() || '';
    if (!trimmed) return { isValid: false, error: 'Title is required' };
    if (trimmed.length > 200) return { isValid: false, error: 'Title must be 200 characters or less' };
    return { isValid: true };
  },
}));

describe('TodoForm', () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it('renders input and add button', () => {
    render(<TodoForm onSubmit={mockOnSubmit} />);

    expect(screen.getByPlaceholderText(/what needs to be done/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /add/i })).toBeInTheDocument();
  });

  it('shows error for empty title', async () => {
    render(<TodoForm onSubmit={mockOnSubmit} />);

    const submitButton = screen.getByRole('button', { name: /add/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
    });
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('shows error for title longer than 200 characters', async () => {
    render(<TodoForm onSubmit={mockOnSubmit} />);

    const input = screen.getByPlaceholderText(/what needs to be done/i);
    const longTitle = 'a'.repeat(201);

    fireEvent.change(input, { target: { value: longTitle } });
    fireEvent.click(screen.getByRole('button', { name: /add/i }));

    await waitFor(() => {
      expect(screen.getByText(/title must be 200 characters or less/i)).toBeInTheDocument();
    });
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('submits with valid title', async () => {
    mockOnSubmit.mockResolvedValue(true);
    render(<TodoForm onSubmit={mockOnSubmit} />);

    const input = screen.getByPlaceholderText(/what needs to be done/i);
    fireEvent.change(input, { target: { value: 'Buy groceries' } });
    fireEvent.click(screen.getByRole('button', { name: /add/i }));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('Buy groceries', undefined);
    });
  });

  it('clears form after successful submit', async () => {
    mockOnSubmit.mockResolvedValue(true);
    render(<TodoForm onSubmit={mockOnSubmit} />);

    const input = screen.getByPlaceholderText(/what needs to be done/i);
    fireEvent.change(input, { target: { value: 'Buy groceries' } });
    fireEvent.click(screen.getByRole('button', { name: /add/i }));

    await waitFor(() => {
      expect(input).toHaveValue('');
    });
  });

  it('does not clear form after failed submit', async () => {
    mockOnSubmit.mockResolvedValue(false);
    render(<TodoForm onSubmit={mockOnSubmit} />);

    const input = screen.getByPlaceholderText(/what needs to be done/i);
    fireEvent.change(input, { target: { value: 'Buy groceries' } });
    fireEvent.click(screen.getByRole('button', { name: /add/i }));

    await waitFor(() => {
      expect(input).toHaveValue('Buy groceries');
    });
  });

  it('shows add description button', () => {
    render(<TodoForm onSubmit={mockOnSubmit} />);

    expect(screen.getByText(/add description/i)).toBeInTheDocument();
  });

  it('shows description textarea when clicking add description', () => {
    render(<TodoForm onSubmit={mockOnSubmit} />);

    fireEvent.click(screen.getByText(/add description/i));

    expect(screen.getByPlaceholderText(/add a description/i)).toBeInTheDocument();
  });

  it('submits with title and description', async () => {
    mockOnSubmit.mockResolvedValue(true);
    render(<TodoForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByPlaceholderText(/what needs to be done/i);
    fireEvent.change(titleInput, { target: { value: 'Buy groceries' } });

    fireEvent.click(screen.getByText(/add description/i));
    const descInput = screen.getByPlaceholderText(/add a description/i);
    fireEvent.change(descInput, { target: { value: 'Milk, eggs, bread' } });

    fireEvent.click(screen.getByRole('button', { name: /add/i }));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('Buy groceries', 'Milk, eggs, bread');
    });
  });

  it('disables form when loading', () => {
    render(<TodoForm onSubmit={mockOnSubmit} isLoading={true} />);

    expect(screen.getByPlaceholderText(/what needs to be done/i)).toBeDisabled();
  });

  it('add button is disabled when title is empty', () => {
    render(<TodoForm onSubmit={mockOnSubmit} />);

    expect(screen.getByRole('button', { name: /add/i })).toBeDisabled();
  });

  it('add button is enabled when title has content', () => {
    render(<TodoForm onSubmit={mockOnSubmit} />);

    const input = screen.getByPlaceholderText(/what needs to be done/i);
    fireEvent.change(input, { target: { value: 'Buy groceries' } });

    expect(screen.getByRole('button', { name: /add/i })).not.toBeDisabled();
  });
});
