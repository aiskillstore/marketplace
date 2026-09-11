ALTER TABLE `enrichment_runs` ADD `cost_source` text DEFAULT 'fixed' NOT NULL;--> statement-breakpoint
ALTER TABLE `enrichment_runs` ADD `error_kind` text;--> statement-breakpoint
ALTER TABLE `workflow_runs` ADD `stop_reason` text;--> statement-breakpoint
ALTER TABLE `workflow_runs` ADD `remaining_keys` text;--> statement-breakpoint
ALTER TABLE `workflow_runs` ADD `failed_step` text;--> statement-breakpoint
ALTER TABLE `workflow_runs` ADD `run_url` text;--> statement-breakpoint
ALTER TABLE `workflow_runs` ADD `trigger_token` text;--> statement-breakpoint
ALTER TABLE `workflow_runs` ADD `scheduled_for` text;--> statement-breakpoint
ALTER TABLE `workflow_runs` ADD `cancel_requested_at` integer;--> statement-breakpoint
CREATE UNIQUE INDEX `workflow_runs_scheduled_idx` ON `workflow_runs` (`path`,`scheduled_for`) WHERE scheduled_for IS NOT NULL;
