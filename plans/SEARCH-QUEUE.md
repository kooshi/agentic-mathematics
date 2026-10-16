# The search queue

*Keryx's file. One line per `search request` from a job's report: what a search would decide, its object and size, the report it
came from, and its fate. *Why a queue:* no lane but the Searcher runs a search (`plans/STANDING-RULES.md` rule 5), so a step a search
could decide must wait somewhere it cannot be lost. Once a day, outside the milestone loop, Keryx briefs the Searcher
(`.claude/agents/searcher.md`) on the open requests; its runs are recorded in `plans/SEARCH-<date>.md`.*

| # | requested | what it would decide | object and size | source | fate |
|---|---|---|---|---|---|
