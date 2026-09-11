export const migrations = [
  {
    "tag": "0000_even_ronan",
    "hash": "32eedee26d98d0f9d28589bd53b1751290cac9dd68092ddc251c13d031b10342",
    "sql": "CREATE TABLE `enrichment_cache` (\n\t`provider` text NOT NULL,\n\t`endpoint` text NOT NULL,\n\t`inputs_hash` text NOT NULL,\n\t`inputs` text NOT NULL,\n\t`value` text NOT NULL,\n\t`expires_at` integer NOT NULL,\n\t`created_at` integer NOT NULL,\n\tPRIMARY KEY(`provider`, `endpoint`, `inputs_hash`)\n);\n--> statement-breakpoint\nCREATE TABLE `enrichment_runs` (\n\t`id` text PRIMARY KEY NOT NULL,\n\t`run_key` text NOT NULL,\n\t`workflow` text NOT NULL,\n\t`provider` text NOT NULL,\n\t`endpoint` text NOT NULL,\n\t`inputs_hash` text NOT NULL,\n\t`status` text NOT NULL,\n\t`cost_usd` real,\n\t`error` text,\n\t`created_at` integer NOT NULL\n);\n--> statement-breakpoint\nCREATE INDEX `enrichment_runs_run_key_idx` ON `enrichment_runs` (`run_key`);--> statement-breakpoint\nCREATE TABLE `workflow_runs` (\n\t`run_key` text PRIMARY KEY NOT NULL,\n\t`run_id` text,\n\t`workflow` text NOT NULL,\n\t`path` text NOT NULL,\n\t`method` text NOT NULL,\n\t`input` text NOT NULL,\n\t`input_hash` text NOT NULL,\n\t`status` text NOT NULL,\n\t`error` text,\n\t`completed` integer,\n\t`failed` integer,\n\t`cost_usd` real,\n\t`checkpoint` integer,\n\t`webhook_url` text,\n\t`approval` text,\n\t`started_at` integer NOT NULL,\n\t`finished_at` integer\n);\n--> statement-breakpoint\nCREATE UNIQUE INDEX `workflow_runs_run_id_unique` ON `workflow_runs` (`run_id`);--> statement-breakpoint\nCREATE UNIQUE INDEX `workflow_runs_live_idx` ON `workflow_runs` (`path`,`input_hash`) WHERE finished_at IS NULL;\n",
    "createdAt": 1787756200390
  },
  {
    "tag": "0001_wise_mac_gargan",
    "hash": "afc547bdbc214af9c8d18689779a320508d50fbc11f4e95418eddd332a79f596",
    "sql": "ALTER TABLE `enrichment_cache` ADD `raw` text;",
    "createdAt": 1787777723887
  },
  {
    "tag": "0002_abandoned_quentin_quire",
    "hash": "27ee3588302f59b4c92c3c27688f97e8844c230ad441e808289a0182b6aa55aa",
    "sql": "ALTER TABLE `enrichment_runs` ADD `cost_source` text DEFAULT 'fixed' NOT NULL;--> statement-breakpoint\nALTER TABLE `enrichment_runs` ADD `error_kind` text;--> statement-breakpoint\nALTER TABLE `workflow_runs` ADD `stop_reason` text;--> statement-breakpoint\nALTER TABLE `workflow_runs` ADD `remaining_keys` text;--> statement-breakpoint\nALTER TABLE `workflow_runs` ADD `failed_step` text;--> statement-breakpoint\nALTER TABLE `workflow_runs` ADD `run_url` text;--> statement-breakpoint\nALTER TABLE `workflow_runs` ADD `trigger_token` text;--> statement-breakpoint\nALTER TABLE `workflow_runs` ADD `scheduled_for` text;--> statement-breakpoint\nALTER TABLE `workflow_runs` ADD `cancel_requested_at` integer;--> statement-breakpoint\nCREATE UNIQUE INDEX `workflow_runs_scheduled_idx` ON `workflow_runs` (`path`,`scheduled_for`) WHERE scheduled_for IS NOT NULL;\n",
    "createdAt": 1787907952921
  },
  {
    "tag": "0003_watery_stone_men",
    "hash": "5bfef38e74bb09d8ab9eaf32add86b946a691e20b8e3d77f4c56f49d0c63af69",
    "sql": "ALTER TABLE `enrichment_runs` ADD `row_key` text;--> statement-breakpoint\nALTER TABLE `enrichment_runs` ADD `step` text;",
    "createdAt": 1787911092741
  },
  {
    "tag": "0004_child_batches",
    "hash": "a0e4718ee3b1528e2db708473715a27eab94742fc0b8e3a78f1ac4c11a18d608",
    "sql": "ALTER TABLE `workflow_runs` ADD `parent_run_key` text;--> statement-breakpoint\nCREATE INDEX `workflow_runs_parent_idx` ON `workflow_runs` (`parent_run_key`);",
    "createdAt": 1789048555595
  },
  {
    "tag": "0005_fearless_angel",
    "hash": "ed723963bbd16160fa8eaace35ca27d602d87da270764e679f3bfdf8282bf73a",
    "sql": "ALTER TABLE `workflow_runs` ADD `workspace_head` text;",
    "createdAt": 1789124048760
  }
] as const;
