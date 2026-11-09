# Task 3: Describe the behaviour

**Data:** `export_english.csv` contains 8,753 rows of weekly case counts. Its missing codes ("Not available", index −1, population 0) were loaded as None/NaN, and `clean_matrix` replaced **147 values in 94 rows** with −1.

**(a) Trend.** Plots 1 and 3 show no clear relationship between a group's population and its weekly cases. Most rows have 1–5 cases at every population size, and the fitted line is flat (r = −0.01), so there is no linear relationship and no clear direction. Plot 4 shows a weak pattern: index 1 has the highest mean rate (67 per 100,000) and index 3 the lowest (25).

**(b) Replaced points.** In Plot 2 the 11 rows with population −1 (red ×) sit by themselves to the left of zero and are far from every real observation (the smallest real population is 470). In Plot 4 the replaced points form a separate column at index −1, and the 11 rows with population −1 give impossible rates between −100,000 and −300,000 per 100,000.

**(c) Distortion.** The placeholders make the averages wrong. The mean rate drops from **35.8 to −123.3** per 100,000, and the mean socioeconomic index drops from 2.90 to 2.86. A trend line would be pulled towards these fake points.

**(d) Alternatives.** Dropping incomplete rows is the best choice here, because only 94 of 8,753 rows (1.1%) are affected. Filling with the median works better when many rows are missing; for the socioeconomic index the median is 3. NaN can also be kept so that libraries skip it.
