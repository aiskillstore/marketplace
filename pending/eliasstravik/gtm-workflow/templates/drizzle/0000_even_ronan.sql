CREATE TABLE `enrichment_cache` (
	`provider` text NOT NULL,
	`endpoint` text NOT NULL,
	`inputs_hash` text NOT NULL,
	`inputs` text NOT NULL,
	`value` text NOT NULL,
	`expires_at` integer NOT NULL,
	`created_at` integer NOT NULL,
	PRIMARY KEY(`provider`, `endpoint`, `inputs_hash`)
);
--> statement-breakpoint
CREATE TABLE `enrichment_runs` (
	`id` text PRIMARY KEY NOT NULL,
	`run_key` text NOT NULL,
	`workflow` text NOT NULL,
	`provider` text NOT NULL,
	`endpoint` text NOT NULL,
	`inputs_hash` text NOT NULL,
	`status` text NOT NULL,
	`cost_usd` real,
	`error` text,
	`created_at` integer NOT NULL
);
--> statement-breakpoint
CREATE INDEX `enrichment_runs_run_key_idx` ON `enrichment_runs` (`run_key`);--> statement-breakpoint
CREATE TABLE `workflow_runs` (
	`run_key` text PRIMARY KEY NOT NULL,
	`run_id` text,
	`workflow` text NOT NULL,
	`path` text NOT NULL,
	`method` text NOT NULL,
	`input` text NOT NULL,
	`input_hash` text NOT NULL,
	`status` text NOT NULL,
	`error` text,
	`completed` integer,
	`failed` integer,
	`cost_usd` real,
	`checkpoint` integer,
	`webhook_url` text,
	`approval` text,
	`started_at` integer NOT NULL,
	`finished_at` integer
);
--> statement-breakpoint
CREATE UNIQUE INDEX `workflow_runs_run_id_unique` ON `workflow_runs` (`run_id`);--> statement-breakpoint
CREATE UNIQUE INDEX `workflow_runs_live_idx` ON `workflow_runs` (`path`,`input_hash`) WHERE finished_at IS NULL;
