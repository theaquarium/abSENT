# abSENT    [![CodeQL](https://github.com/bykevinyang/abSENT/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/bykevinyang/abSENT/actions/workflows/codeql-analysis.yml)

 ![abSENT Github Banner](marketing/banner.png)

## What is it?
An SMS schoology bot that texts NPS students when their teachers are absent. Supports both Newton high schools, [Newton South](https://www.newton.k12.ma.us/nshs) & [Newton North](https://www.newton.k12.ma.us/nnhs).
abSENT uses the [Schoolopy](https://github.com/ErikBoesen/schoolopy) API wrapper to grab teacher absences from Schoology, which are processed. Alerts are then texted through TextNow using the [PyTextNow](https://github.com/leogomezz4t/PyTextNow_API) API wrapper, to students who have teachers that are absent.

## How does it work?
Students sign up by texting abSENT's phone number and inputting their schedule. The schedule is then saved as an SQLite database using 3 tables:

- One table stores students and their characteristics (name and phone number)
- Another stores teachers and their characteristics (name)
- The third table is an array of classes that maps teacher & block -> student. 

Every school day, abSENT retrives the new absence list and parses it. It then queries the SQLite database by teacher ID and block to find students who have absent teachers. These students are then notifed over text that their teacher is absent.

## Why?
Refreshing Schoology 20 times every morning is somewhat draining.

## Contributors
- [Kevin Yang](https://github.com/bykevinyang)
- [Roshan Karim](https://github.com/karimroshan)

## Disclaimer:
abSENT as a project is not affiliated with any of the entities who's students it serves. We are students and have written this project just for fun, as a minor QOL improvement in the morning.
