import consola from 'consola';

/**
 * Plugin CLI Logger
 *
 * Provides styled logging and progress indicators for plugin operations.
 */

/** Color codes for different log types */
const colors = {
	info: '\x1b[36m', // Cyan
	success: '\x1b[32m', // Green
	warn: '\x1b[33m', // Yellow
	error: '\x1b[31m', // Red
	dim: '\x1b[90m', // Gray
	reset: '\x1b[0m',
	bold: '\x1b[1m',
};

export interface ProgressState {
	current: number;
	total: number;
	label: string;
}

class PluginLogger {
	private progressState: ProgressState | null = null;
	private spinnerInterval: NodeJS.Timeout | null = null;
	private spinnerFrames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
	private spinnerIndex = 0;

	/**
	 * Log info message
	 */
	info(message: string): void {
		consola.info(message);
	}

	/**
	 * Log success message
	 */
	success(message: string): void {
		consola.success(message);
	}

	/**
	 * Log warning message
	 */
	warn(message: string): void {
		consola.warn(message);
	}

	/**
	 * Log error message
	 */
	error(message: string, err?: Error): void {
		consola.error(message);
		if (err && process.env.DEBUG) {
			consola.error(err);
		}
	}

	/**
	 * Log debug message (only in DEBUG mode)
	 */
	debug(message: string): void {
		if (process.env.DEBUG) {
			consola.debug(message);
		}
	}

	/**
	 * Start a spinner with message
	 */
	startSpinner(message: string): void {
		this.stopSpinner();
		this.spinnerIndex = 0;

		const spin = () => {
			const frame = this.spinnerFrames[this.spinnerIndex];
			process.stdout.write(`\r${colors.info}${frame}${colors.reset} ${message}`);
			this.spinnerIndex = (this.spinnerIndex + 1) % this.spinnerFrames.length;
		};

		spin();
		this.spinnerInterval = setInterval(spin, 80);
	}

	/**
	 * Stop the spinner
	 */
	stopSpinner(): void {
		if (this.spinnerInterval) {
			clearInterval(this.spinnerInterval);
			this.spinnerInterval = null;
			process.stdout.write('\r\x1b[K'); // Clear line
		}
	}

	/**
	 * Complete spinner with success
	 */
	spinnerSuccess(message: string): void {
		this.stopSpinner();
		console.log(`${colors.success}✓${colors.reset} ${message}`);
	}

	/**
	 * Complete spinner with error
	 */
	spinnerError(message: string): void {
		this.stopSpinner();
		console.log(`${colors.error}✗${colors.reset} ${message}`);
	}

	/**
	 * Start progress tracking
	 */
	startProgress(total: number, label: string): void {
		this.progressState = { current: 0, total, label };
		this.renderProgress();
	}

	/**
	 * Update progress
	 */
	updateProgress(current: number): void {
		if (this.progressState) {
			this.progressState.current = current;
			this.renderProgress();
		}
	}

	/**
	 * Increment progress by 1
	 */
	incrementProgress(): void {
		if (this.progressState) {
			this.progressState.current++;
			this.renderProgress();
		}
	}

	/**
	 * Complete progress
	 */
	completeProgress(): void {
		if (this.progressState) {
			process.stdout.write('\r\x1b[K'); // Clear line
			const { total, label } = this.progressState;
			console.log(`${colors.success}✓${colors.reset} ${label} (${total}/${total})`);
			this.progressState = null;
		}
	}

	/**
	 * Render progress bar
	 */
	private renderProgress(): void {
		if (!this.progressState) return;

		const { current, total, label } = this.progressState;
		const percent = Math.round((current / total) * 100);
		const barWidth = 20;
		const filled = Math.round((current / total) * barWidth);
		const empty = barWidth - filled;

		const bar = `${'█'.repeat(filled)}${'░'.repeat(empty)}`;
		process.stdout.write(
			`\r${colors.info}↓${colors.reset} ${label} ${colors.dim}[${bar}]${colors.reset} ${current}/${total} (${percent}%)`
		);
	}

	/**
	 * Print a box with content
	 */
	box(title: string, content: string[]): void {
		const width = Math.max(title.length, ...content.map((c) => c.length)) + 4;
		const border = '─'.repeat(width);

		console.log(`${colors.dim}┌${border}┐${colors.reset}`);
		console.log(`${colors.dim}│${colors.reset} ${colors.bold}${title.padEnd(width - 2)}${colors.reset} ${colors.dim}│${colors.reset}`);
		console.log(`${colors.dim}├${border}┤${colors.reset}`);

		for (const line of content) {
			console.log(`${colors.dim}│${colors.reset} ${line.padEnd(width - 2)} ${colors.dim}│${colors.reset}`);
		}

		console.log(`${colors.dim}└${border}┘${colors.reset}`);
	}

	/**
	 * Print skill installation summary
	 */
	skillSummary(slug: string, status: 'installed' | 'skipped' | 'failed'): void {
		const icons = {
			installed: `${colors.success}✓${colors.reset}`,
			skipped: `${colors.warn}○${colors.reset}`,
			failed: `${colors.error}✗${colors.reset}`,
		};

		console.log(`  ${icons[status]} ${slug}`);
	}
}

/** Singleton logger instance */
export const logger = new PluginLogger();
