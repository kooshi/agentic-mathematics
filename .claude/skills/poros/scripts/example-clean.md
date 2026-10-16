# A stalled parameter search — one turn of Poros

## Evidence inventory

- `results.csv`, 36 runs of the sweep over (alpha, beta), scores 0.61–0.74 — read against: score should vary smoothly with alpha and beta and only slightly with the seed — surprised: yes; only six distinct scores occur, one per seed, repeating exactly across unrelated (alpha, beta)
- `README.md`, the sweep's narrative: "scores are noisy; concentrate the next batch near run 17" — read against: the narrative would mention the seed column — surprised: yes; it does not
- `launch.sh`, the script that starts each run — read against: nothing yet — surprised: unread
- The sprint goal, "a tuned configuration by Friday" — read against: the goal is the configuration, not the sweep — surprised: no

question: are-the-parameters-reaching-the-process
  evidence: `results.csv` rows 3, 11, 25 and 30 share seed 4 and score 0.7137 exactly, at alpha from 0.01 to 0.9; six seeds, six scores, 36 runs
  expected: score is a function of alpha and beta, with the seed a nuisance variable
  ask: do alpha and beta reach the process at all, or is the score a function of the seed alone?
  if the seed alone: the sweep has measured nothing; fix the launcher before any batch, and re-read every conclusion drawn from the 36 runs
  if they reach it: the landscape is flat at this resolution and the search is the wrong instrument; the next move is a controlled pair, not a batch
  answered by: run — two runs with the same seed and different alpha; if the scores match to four decimals the parameters are not arriving
  cost: two runs, ten minutes
  hunch: the seed alone — six seeds, six scores, and the launcher was edited the day the sweep began
  falsifier: two same-seed runs with different alpha that score differently
  rank: 1

question: is-the-sweep-the-product
  evidence: the sprint goal names "a tuned configuration"; the plan names "the next 12 points"
  expected: the batch is the product
  ask: is a twelve-point batch what Friday is for, or a configuration whose score we can trust?
  if the configuration: one pipeline check outranks any batch, and the batch waits
  if the batch: submit the batch with the pipeline check as its first row, and say so
  answered by: human — the person who set the sprint goal
  cost: one message
  rank: 2

hunch: the-landscape-is-flat
  claim: within the swept ranges, score varies less with alpha and beta than with the seed
  basis: measured
  falsifier: any pair of runs at one seed whose scores differ by more than the seed spread
  registered: 2026-09-06
  status: open

hunch: the-launcher-drops-the-parameters
  claim: `launch.sh` starts every run with the default alpha and beta
  basis: read
  falsifier: a run whose log shows the requested alpha
  registered: 2026-09-06
  status: confirmed (by: `launch.sh` line 12 — the variables are set and never passed on the command line)
