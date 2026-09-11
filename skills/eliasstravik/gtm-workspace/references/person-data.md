# Person-data research contract

Use this contract for the default person data in every newly created `MEMBER.md` and `PERSONA.md`, and whenever research refreshes either artifact. `MEMBER.md` records sourced facts about a person. `PERSONA.md` records desired or accepted person criteria. Numeric persona values may be target ranges, and persona lists may contain accepted values.

`MEMBER.md` also requires an `Email` identifier outside this shared contract. Use only an email the user supplies or a source states directly. Never infer one. `PERSONA.md` does not include email by default.

Research every shared field when safe sources are available. Preserve uncertainty and source limits. Keep every field visible in the rendered Markdown and write `Unknown` when a value cannot be resolved. Never invent a value or infer a persona criterion from organization or member facts.

Use `## Person data` followed by these eight top-level fields in this order. Optional structural metadata and free-form notes may follow the person data, but they are not default research targets.

1. **Full name**
   - A free-text string containing the person's full name.
2. **Education**
   - A structured list of education records.
   - Each record supports activities, degree, description, end date, field of study, school name, and start date.
3. **Estimated followers**
   - A non-negative integer estimating the follower count on the relevant professional profile.
   - Keep the estimate explicit in the field label.
4. **Experience**
   - A structured list of employment records.
   - Each record supports company name, employment type, end date, experience description, current-role status, job title, location, seniority, start date, and years of experience.
   - Experience location supports city, country, display location, region, and state.
5. **Languages**
   - A list of strings naming languages associated with the person.
6. **Location**
   - A structured location supporting city, country, region, and state.
7. **Network size**
   - A non-negative integer giving the size of the person's professional network.
8. **Professional profile**
   - A structured profile supporting about and headline.
