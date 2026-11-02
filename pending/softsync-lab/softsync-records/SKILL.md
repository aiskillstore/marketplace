---
name: softsync-records
description: "Find, create, update, merge, delete and restore records such as companies, contacts, deals and tasks, and chart them. Use when the user names a company, person or deal, wants to add or change one, clean up duplicates, or count and chart their data."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Records

Records are the rows of workspace tables: companies, contacts, deals, tasks and any custom objects.

## Start here
1. Call `describe_workspace_schema` to learn the tables, their fields and the groups you can see.
2. Name tables and fields by their `apiName` (snake_case), never by display label.
3. System fields are `__system_created_at`, `__system_updated_at` and `__system_created_by`. The double underscore is required.
4. Most features have one tool for reading (such as `groups`) and one for changing (such as `manage_groups`). Say what to do with `action`, and send only the fields that action uses.

## Finding records
- `search_records`: exact filters on fields (equals, contains, greater than, empty…) with sort and paging. Use it for "deals in negotiation" or "contacts at Acme".
- `semantic_search_records`: search by meaning when the user describes something loosely.
- `get_record_by_id`: the full record once you have its id.
- `query_records_by_view`: the records a saved view shows, with that view's filters and sort.
- `get_related_record_ids`: records linked to one record, such as the contacts at a company.
- `get_record_activity`: what changed on a record, when and by whom. Use it to answer "what happened?" instead of guessing.
- `get_record_moves`: which statuses a record may move to next, and which moves need a comment.

## Creating and changing records
- `record_creation`: create one or many records, across tables in one call. Records in the same call can link to each other through `_ref`. Pick a duplicate-detection field per table so existing records are matched instead of duplicated.
- `update_record`: change fields on specific records. Send only the fields that change.
- `update_field_on_records`: set the same values on many records. For "all of them", get the ids first with `find_matching_record_ids`.
- `manage_records` with action `add_to_group` or `remove_from_group`: change which group records appear in.
- A status move that needs a comment is refused without one; pass `comment` with the update.

## Time on records
`manage_timers` with action `start` starts your timer on a record and `stop` stops it and logs the time. `get_timer` shows what is running. You have one timer: starting another stops the running one and keeps its time.

## Cleaning up
- `check_duplicate_records`: find likely duplicates in a table so the user can review them.
- `manage_records` with action `merge`: fold duplicates into one record. The service chooses the survivor, and a merge cannot be undone.
- `manage_records` with action `delete`: move records to the Bin. Action `restore` brings them back within 30 days.

## Numbers and charts
- `record_statistic`: one count, sum, average or ratio, optionally split by a field — "how many open deals per stage?".
- `generate_analytics`: several chart datasets at once. Both return data, not pictures. To keep a chart on a group's Reports page, use `manage_dashboards` with action `add_chart`.
- For forecasts and trends use `generate_analytics`: a period with `compareTo` for "this quarter vs last", `forecast` on a bar chart over time for "where will we land", `asOf` for "what did the pipeline look like on 1 March", a `bridge` for "what moved the pipeline this month", and `reached` / `days_in_value` for stage conversion and time in each stage.
- A weighted pipeline needs a probability per deal: if the deals table has none, offer to add a number field (filled from the stage) and a formula field multiplying value by probability, then sum it.

## Rules
- Never invent ids. Look records, people and groups up first and use the ids that come back.
- A relation field takes record ids; a person field takes workspace member ids.
- Say what you are about to change before a bulk update, a merge or a delete, and wait for the user to agree.

## More detail
Read these when the task needs them:
- [searching-records](references/searching-records.md): Filters, operators, sorting, related-record filters and counting, with good and bad examples.
- [resolving-records](references/resolving-records.md): Turning a company or person into every linked record id before reading their messages or acting on them.
- [writing-records](references/writing-records.md): Creating and updating records without duplicates, linking them, enriching them and formatting each field kind.
