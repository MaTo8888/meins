# CLAUDE.md

This file provides guidance for AI assistants (e.g., Claude Code) working in this repository.

## Project Overview

**Name:** meins
**Status:** Newly initialized — no source code yet.
**Repository:** https://github.com/MaTo8888/meins
**Primary branch:** `master`

> This CLAUDE.md will grow as the project evolves. Update it whenever the tech stack, conventions, or workflows change.

## Repository Structure

```
meins/
└── README.md   # Project title only — no content yet
```

No source code, build system, tests, or dependencies exist yet. The project is ready for initial development.

## Development Workflow

### Branching

- Development happens on `master` (default) or feature branches.
- Claude Code uses branches prefixed with `claude/` followed by a session ID.
- Never force-push to `master` without explicit permission.

### Commits

- Write clear, descriptive commit messages in the imperative mood (e.g., "Add user authentication module").
- Keep commits focused and atomic — one logical change per commit.
- Reference issue numbers when applicable (e.g., `Fix login bug (#42)`).

### Pull Requests

- PRs should include a summary of changes and a test plan.
- All CI checks must pass before merging.

## Getting Started

Since no build system or language has been chosen yet, this section will be populated once the stack is decided.

**Placeholder checklist:**
- [ ] Choose primary language / framework
- [ ] Initialize package manager / dependency manifest
- [ ] Add `.gitignore` appropriate for the chosen stack
- [ ] Set up CI/CD (e.g., GitHub Actions)
- [ ] Add linting and formatting tooling
- [ ] Write a proper README with setup instructions

## Conventions (to be defined)

Once a tech stack is selected, document the following here:

- **Code style / formatter:** TBD
- **Linter:** TBD
- **Testing framework:** TBD
- **How to run tests:** TBD
- **How to build:** TBD
- **Environment variables:** TBD

## Notes for AI Assistants

- The repository is empty; there is no existing code to conflict with.
- Before writing any code, confirm the intended language, framework, and architecture with the user.
- Keep changes minimal and focused — avoid adding boilerplate or features that were not requested.
- Update this file whenever significant architectural decisions are made.
- Do not commit secrets, credentials, or `.env` files.
