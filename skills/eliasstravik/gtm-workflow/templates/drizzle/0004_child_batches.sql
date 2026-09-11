ALTER TABLE `workflow_runs` ADD `parent_run_key` text;--> statement-breakpoint
CREATE INDEX `workflow_runs_parent_idx` ON `workflow_runs` (`parent_run_key`);