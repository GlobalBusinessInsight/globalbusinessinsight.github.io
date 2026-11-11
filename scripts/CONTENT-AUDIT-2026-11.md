# Content audit and archive decision — 11 November 2026

## Scope

The repository contains 500 editorial HTML pages. The build now scores every page against the site's published 100-point rubric: completeness and substance (30), argument and structure (25), evidence and traceability (30), and editorial clarity (15).

## Decision

- 108 pages meet the 70-point threshold and fit one of the four active research desks.
- 355 pages score below 70 and are archived.
- 37 additional pages score 70 or more but are demos, prototypes, legacy tools, promotional material, or outside the current research desks; they are archived as well.
- 392 pages are therefore classified as archive material; 108 remain in the active research catalogue.

The score is a consistent editorial screen. It checks for a clear title, enough substantive text, section structure, a thesis or conclusion, a limitations/risk discussion, external references, dates, data and direct language. It cannot establish that every source is authoritative or that each historical claim is still current. The archive label does not mean the contents were re-researched.

## What changed

- Active research cards are used on the home page, topic pages and default archive search.
- Archived pages are removed from active topic lists, default search results and the sitemap.
- Archived pages carry `noindex,follow` and remain at their original URLs to preserve incoming links. The archive directory remains available for readers who deliberately search historical material.
- No article body was rewritten as part of this screening. The current 2026 research remains in its original authored language; the new homepage is English-first and links to the original reports.

## Recheck before restoring an archived page

Review the source links and reporting period, distinguish facts from estimates and forecasts, check the thesis and limitations, then confirm that the page belongs in an active research desk. A build-time score above 70 alone is not sufficient to restore it.
