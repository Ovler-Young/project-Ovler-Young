# About My Project

Student Name:  Chengyu Jin
Student Email:  <cjin20@syr.edu>

### What it does

It Analyzes Internet Archive Collection.

For instance, I want to analyze the [wikiteam's collections](https://archive.org/details/wikiteam?tab=about).

So this project will grab all the items' metadata in this collection, then analyze its `language`, `Addeddate`, `Size`, and `Last-updated-date` fields. Also include some combined analysis, like the `Size` vs `Last-updated-date` scatter plot, or how long has the item been added to the how long has the item been updated.

And showcase the results with `streamlit` web application.

Perhaps, if time permit, I'll build a docker for this repo.

### How you run my project

#### Use PDM

#### 1. Prerequisites

Have [pdm installed](https://pdm-project.org/en/latest/#installation).

#### 2. Install dependencies

```bash
pdm install
```

#### Directly use pip

```bash
pip install .
```

### Other things you need to know

Please [donate! to Internet Archive!](https://archive.org/donate)
