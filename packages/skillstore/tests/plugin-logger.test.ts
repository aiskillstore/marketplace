import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { logger, type ProgressState } from '../src/lib/plugin-logger.js';

// Mock consola
vi.mock('consola', () => ({
	default: {
		info: vi.fn(),
		success: vi.fn(),
		warn: vi.fn(),
		error: vi.fn(),
		debug: vi.fn(),
	},
}));

import consola from 'consola';

describe('plugin-logger', () => {
	const mockConsola = vi.mocked(consola);
	let stdoutSpy: ReturnType<typeof vi.spyOn>;
	let consoleSpy: ReturnType<typeof vi.spyOn>;

	beforeEach(() => {
		vi.clearAllMocks();
		stdoutSpy = vi.spyOn(process.stdout, 'write').mockImplementation(() => true);
		consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
	});

	afterEach(() => {
		stdoutSpy.mockRestore();
		consoleSpy.mockRestore();
		// Reset logger state
		logger.stopSpinner();
	});

	describe('basic logging methods', () => {
		it('should log info message', () => {
			logger.info('Test info message');
			expect(mockConsola.info).toHaveBeenCalledWith('Test info message');
		});

		it('should log success message', () => {
			logger.success('Test success message');
			expect(mockConsola.success).toHaveBeenCalledWith('Test success message');
		});

		it('should log warning message', () => {
			logger.warn('Test warning message');
			expect(mockConsola.warn).toHaveBeenCalledWith('Test warning message');
		});

		it('should log error message', () => {
			logger.error('Test error message');
			expect(mockConsola.error).toHaveBeenCalledWith('Test error message');
		});

		it('should log error with Error object in DEBUG mode', () => {
			const originalDebug = process.env.DEBUG;
			process.env.DEBUG = 'true';

			const testError = new Error('Test error');
			logger.error('Error occurred', testError);

			expect(mockConsola.error).toHaveBeenCalledWith('Error occurred');
			expect(mockConsola.error).toHaveBeenCalledWith(testError);

			process.env.DEBUG = originalDebug;
		});

		it('should not log error object when DEBUG is not set', () => {
			const originalDebug = process.env.DEBUG;
			delete process.env.DEBUG;

			const testError = new Error('Test error');
			logger.error('Error occurred', testError);

			expect(mockConsola.error).toHaveBeenCalledTimes(1);
			expect(mockConsola.error).toHaveBeenCalledWith('Error occurred');

			process.env.DEBUG = originalDebug;
		});
	});

	describe('debug logging', () => {
		it('should log debug message when DEBUG is set', () => {
			const originalDebug = process.env.DEBUG;
			process.env.DEBUG = 'true';

			logger.debug('Debug message');

			expect(mockConsola.debug).toHaveBeenCalledWith('Debug message');

			process.env.DEBUG = originalDebug;
		});

		it('should not log debug message when DEBUG is not set', () => {
			const originalDebug = process.env.DEBUG;
			delete process.env.DEBUG;

			logger.debug('Debug message');

			expect(mockConsola.debug).not.toHaveBeenCalled();

			process.env.DEBUG = originalDebug;
		});
	});

	describe('spinner', () => {
		it('should start spinner with message', () => {
			vi.useFakeTimers();

			logger.startSpinner('Loading...');

			expect(stdoutSpy).toHaveBeenCalled();
			const output = stdoutSpy.mock.calls[0][0];
			expect(output).toContain('Loading...');

			vi.useRealTimers();
		});

		it('should stop spinner', () => {
			vi.useFakeTimers();

			logger.startSpinner('Loading...');
			logger.stopSpinner();

			// Should clear the line
			expect(stdoutSpy).toHaveBeenCalledWith('\r\x1b[K');

			vi.useRealTimers();
		});

		it('should show success message on spinnerSuccess', () => {
			logger.spinnerSuccess('Done!');

			expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('✓'));
			expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Done!'));
		});

		it('should show error message on spinnerError', () => {
			logger.spinnerError('Failed!');

			expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('✗'));
			expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Failed!'));
		});

		it('should stop existing spinner when starting new one', () => {
			vi.useFakeTimers();

			logger.startSpinner('First');
			logger.startSpinner('Second');

			// Should have cleared the line for the first spinner
			const clearCalls = stdoutSpy.mock.calls.filter(
				(call) => call[0] === '\r\x1b[K'
			);
			expect(clearCalls.length).toBeGreaterThanOrEqual(1);

			vi.useRealTimers();
		});
	});

	describe('progress tracking', () => {
		it('should start progress with total and label', () => {
			logger.startProgress(10, 'Downloading');

			expect(stdoutSpy).toHaveBeenCalled();
			const output = stdoutSpy.mock.calls[0][0];
			expect(output).toContain('Downloading');
			expect(output).toContain('0/10');
		});

		it('should update progress', () => {
			logger.startProgress(10, 'Processing');
			logger.updateProgress(5);

			const lastCall = stdoutSpy.mock.calls[stdoutSpy.mock.calls.length - 1][0];
			expect(lastCall).toContain('5/10');
			expect(lastCall).toContain('50%');
		});

		it('should increment progress', () => {
			logger.startProgress(5, 'Installing');
			logger.incrementProgress();
			logger.incrementProgress();

			const lastCall = stdoutSpy.mock.calls[stdoutSpy.mock.calls.length - 1][0];
			expect(lastCall).toContain('2/5');
		});

		it('should complete progress', () => {
			logger.startProgress(3, 'Done');
			logger.completeProgress();

			expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('✓'));
			expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Done'));
			expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('3/3'));
		});

		it('should handle updateProgress when no progress started', () => {
			// Should not throw
			expect(() => logger.updateProgress(5)).not.toThrow();
		});

		it('should handle incrementProgress when no progress started', () => {
			// Should not throw
			expect(() => logger.incrementProgress()).not.toThrow();
		});

		it('should handle completeProgress when no progress started', () => {
			// Should not throw
			expect(() => logger.completeProgress()).not.toThrow();
		});
	});

	describe('box', () => {
		it('should print box with title and content', () => {
			logger.box('Title', ['Line 1', 'Line 2']);

			// Should print: top border, title, separator, content line 1, content line 2, bottom border
			expect(consoleSpy).toHaveBeenCalledTimes(6);

			// Check title is included
			const calls = consoleSpy.mock.calls.map((c) => c[0] as string);
			expect(calls.some((c) => c.includes('Title'))).toBe(true);
			expect(calls.some((c) => c.includes('Line 1'))).toBe(true);
			expect(calls.some((c) => c.includes('Line 2'))).toBe(true);
		});

		it('should handle empty content', () => {
			expect(() => logger.box('Title', [])).not.toThrow();
		});

		it('should adjust width based on content', () => {
			logger.box('Short', ['This is a much longer line of content']);

			// The box should be wide enough for the longest line
			const calls = consoleSpy.mock.calls.map((c) => c[0] as string);
			const borderLine = calls[0];
			expect(borderLine.length).toBeGreaterThan(10);
		});
	});

	describe('skillSummary', () => {
		it('should print installed status with checkmark', () => {
			logger.skillSummary('test-skill', 'installed');

			expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('✓'));
			expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('test-skill'));
		});

		it('should print skipped status with circle', () => {
			logger.skillSummary('test-skill', 'skipped');

			expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('○'));
			expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('test-skill'));
		});

		it('should print failed status with X', () => {
			logger.skillSummary('test-skill', 'failed');

			expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('✗'));
			expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('test-skill'));
		});
	});
});
