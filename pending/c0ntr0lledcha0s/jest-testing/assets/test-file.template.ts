/**
 * Jest Test File Template
 * 
 * Usage:
 * 1. Copy this file to your __tests__ directory or next to your source file
 * 2. Rename to match your file (e.g., myModule.test.ts)
 * 3. Update imports and test cases
 */

// === UNIT TEST TEMPLATE ===

import { functionToTest, ClassToTest } from '../myModule';

describe('functionToTest', () => {
  // Setup/teardown
  beforeEach(() => {
    // Reset state before each test
  });

  afterEach(() => {
    // Cleanup after each test
    jest.clearAllMocks();
  });

  describe('happy path', () => {
    it('should return expected result for valid input', () => {
      // Arrange
      const input = { key: 'value' };
      const expected = { result: 'expected' };

      // Act
      const result = functionToTest(input);

      // Assert
      expect(result).toEqual(expected);
    });

    it('should handle multiple inputs correctly', () => {
      // Arrange
      const inputs = [1, 2, 3];

      // Act
      const results = inputs.map(functionToTest);

      // Assert
      expect(results).toHaveLength(3);
      results.forEach(result => {
        expect(result).toBeDefined();
      });
    });
  });

  describe('error handling', () => {
    it('should throw error for invalid input', () => {
      // Arrange
      const invalidInput = null;

      // Act & Assert
      expect(() => functionToTest(invalidInput)).toThrow('Invalid input');
    });

    it('should throw specific error type', () => {
      // Arrange
      const invalidInput = {};

      // Act & Assert
      expect(() => functionToTest(invalidInput)).toThrow(ValidationError);
    });
  });

  describe('edge cases', () => {
    it('should handle empty input', () => {
      expect(functionToTest([])).toEqual([]);
      expect(functionToTest('')).toBe('');
      expect(functionToTest({})).toEqual({});
    });

    it('should handle boundary values', () => {
      expect(functionToTest(Number.MAX_SAFE_INTEGER)).toBeDefined();
      expect(functionToTest(0)).toBeDefined();
      expect(functionToTest(-1)).toBeDefined();
    });
  });
});

// === ASYNC TEST TEMPLATE ===

describe('asyncFunction', () => {
  it('should resolve with data', async () => {
    // Arrange
    const input = 'test';

    // Act
    const result = await asyncFunction(input);

    // Assert
    expect(result).toEqual({ data: 'test' });
  });

  it('should reject with error', async () => {
    // Arrange
    const invalidInput = null;

    // Act & Assert
    await expect(asyncFunction(invalidInput)).rejects.toThrow('Error');
  });

  it('should handle timeout', async () => {
    jest.useFakeTimers();

    const promise = asyncFunctionWithTimeout();

    jest.advanceTimersByTime(5000);

    await expect(promise).rejects.toThrow('Timeout');

    jest.useRealTimers();
  });
});

// === CLASS TEST TEMPLATE ===

describe('ClassToTest', () => {
  let instance: ClassToTest;

  beforeEach(() => {
    instance = new ClassToTest();
  });

  describe('constructor', () => {
    it('should initialize with default values', () => {
      expect(instance.property).toBe('default');
    });

    it('should accept configuration', () => {
      const configured = new ClassToTest({ option: 'value' });
      expect(configured.option).toBe('value');
    });
  });

  describe('method', () => {
    it('should update state', () => {
      instance.method('new value');
      expect(instance.property).toBe('new value');
    });
  });
});

// === MOCK TEST TEMPLATE ===

// Mock external dependency
jest.mock('../externalService');
import { externalService } from '../externalService';

const mockExternalService = externalService as jest.Mocked<typeof externalService>;

describe('functionWithDependency', () => {
  beforeEach(() => {
    mockExternalService.fetch.mockReset();
  });

  it('should call external service', async () => {
    // Arrange
    mockExternalService.fetch.mockResolvedValue({ data: 'mocked' });

    // Act
    const result = await functionWithDependency('input');

    // Assert
    expect(mockExternalService.fetch).toHaveBeenCalledWith('input');
    expect(result).toEqual({ data: 'mocked' });
  });

  it('should handle service error', async () => {
    // Arrange
    mockExternalService.fetch.mockRejectedValue(new Error('Service error'));

    // Act & Assert
    await expect(functionWithDependency('input')).rejects.toThrow('Service error');
  });
});

// === REACT COMPONENT TEST TEMPLATE ===

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MyComponent } from '../MyComponent';

describe('MyComponent', () => {
  it('should render correctly', () => {
    render(<MyComponent />);

    expect(screen.getByRole('heading')).toHaveTextContent('Title');
    expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument();
  });

  it('should handle user interaction', async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn();

    render(<MyComponent onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText('Name'), 'John');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    expect(onSubmit).toHaveBeenCalledWith({ name: 'John' });
  });

  it('should display loading state', async () => {
    render(<MyComponent />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });

    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('should display error state', async () => {
    // Mock error response
    server.use(
      http.get('/api/data', () => {
        return HttpResponse.json({ error: 'Failed' }, { status: 500 });
      })
    );

    render(<MyComponent />);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Error');
    });
  });
});

// === HOOK TEST TEMPLATE ===

import { renderHook, act } from '@testing-library/react';
import { useCustomHook } from '../useCustomHook';

describe('useCustomHook', () => {
  it('should return initial state', () => {
    const { result } = renderHook(() => useCustomHook());

    expect(result.current.value).toBe(0);
    expect(result.current.isLoading).toBe(false);
  });

  it('should update state', () => {
    const { result } = renderHook(() => useCustomHook());

    act(() => {
      result.current.increment();
    });

    expect(result.current.value).toBe(1);
  });

  it('should handle async operations', async () => {
    const { result } = renderHook(() => useCustomHook());

    await act(async () => {
      await result.current.fetchData();
    });

    expect(result.current.data).toBeDefined();
  });
});
