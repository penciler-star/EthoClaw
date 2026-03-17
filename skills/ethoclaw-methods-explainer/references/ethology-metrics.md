# Ethology Metrics Reference

Read this file when users ask about behavioral metrics "how they are defined, calculated, and interpreted".

## Scope

Prioritize for explaining these common ethology metrics:

- Frequency / rate
- Duration
- Latency
- Proportion / time budget
- Transition count / transition probability
- Bout length / bout count
- Inter-event interval
- Individual-level summary vs. group-level summary

## Explanation Order

When explaining any metric, prioritize outputting in this order:

1. What is the raw input.
2. What does one record represent.
3. What preprocessing was done.
4. How the metric is calculated.
5. What is the unit of result.
6. How to interpret biologically.
7. What are common misunderstandings or limitations.

## Common Metric Definitions

### Frequency

- Meaning: The number of times a behavior starts occurring within a given observation window.
- Common input: Behavior event table, at least containing individual ID, behavior label, start time.
- Formula: Frequency = event onset count within window
- Unit: counts/window, or counts/minute, counts/hour.
- Note: Must specify whether counting by onset or by any tagged frames.

### Duration

- Meaning: Total time a behavior lasts cumulatively within the observation window.
- Common input: Behavior segment table containing start time and end time.
- Formula: Duration = sum(end_time - start_time)
- Unit: seconds, minutes, or proportion of window.
- Note: Specify whether invisible periods and interruption segments are excluded.

### Latency

- Meaning: Waiting time from a reference time point to the first occurrence of target behavior.
- Common input: Reference event time, first onset time of target behavior.
- Formula: Latency = first_target_onset - reference_time
- Unit: seconds, minutes.
- Note: If target behavior does not occur, specify whether it's recorded as missing, censored, or assigned maximum observation duration.

### Proportion / Time Budget

- Meaning: Proportion of a behavior's duration to total observable time.
- Formula: Proportion = behavior_duration / observable_time
- Unit: 0 to 1, or percentage.
- Note: Observable time is not necessarily equal to total session duration; may need to deduct occlusion, out-of-frame, uncodeable times.

### Transition Probability

- Meaning: Conditional probability of transitioning from behavior A to behavior B.
- Common input: Time-ordered behavior sequence.
- Formula: P(A -> B) = count(A -> B) / total outgoing transitions from A
- Note: Specify whether self-transitions are allowed, and whether calculations are done per individual first then aggregated.

### Bout Length

- Meaning: Duration of one continuous occurrence of a behavior until switching to another behavior.
- Formula: Bout length = end_of_continuous_run - start_of_continuous_run
- Note: Must define criteria for "continuous", e.g., whether brief interruptions are allowed to be merged.

### Inter-event Interval

- Meaning: Time interval between two adjacent target events.
- Formula: IEI = onset(i+1) - onset(i)
- Note: Only meaningful when event definition is clear and time ordering is reliable.

## Common Preprocessing

When explaining metrics, prioritize checking if the following are involved:

- Behavior label merging or recoding.
- Time window binning.
- Smoothing or rolling windows.
- Missing value or invisible period exclusion.
- Aggregation per individual, session, trial first, then inter-group analysis.
- Normalization per minute, per hour, or per trial.

## Common Pitfalls

- Confusing frequency and duration.
- Not specifying denominator, making proportion unreproducible.
- Using group mean to mask individual variation.
- Mixing raw event-level data with aggregated summary-level data.
- Not explaining how latency is handled when target behavior is not observed.

## Recommended Output Sentence Patterns

### Parameter Card Minimum Template

- Name:
- Input:
- Formula:
- Unit:
- Preprocessing:
- Interpretation:
- Limitation:

### Methods Writing Tips

Prioritize using this pattern:

"For each individual / trial / session, we calculated ... as ..."

In English, can write as:

"For each individual / trial / session, calculate... with the definition of..."
