# collective.membersonly / volto-members-only

A Plone 6 / Volto addon that enables gated content with a public metadata teaser.

## The problem

Plone's default workflow offers two states for content visibility: private (invisible to anonymous users and search engines) and published (fully public). There is no middle ground for content that should be discoverable but restricted — where Google and logged-out visitors can see a teaser, but the full content requires authentication.

This is a common need for nonprofits and educational institutions that want to surface member resources in search results while keeping the content itself gated.

## The solution

This addon introduces a members_only workflow state that sits between private and published. Content in this state returns a 200 OK to anonymous users, serves only safe metadata fields via a dedicated teaser endpoint, serves full content to authenticated users, displays a teaser view in Volto with a login prompt, and appears in site search and listing results with meaningful titles and descriptions.

## Architecture

### Security model

The addon introduces a custom permission — Collective Members Only: View Teaser — granted to Anonymous in the members_only workflow state. The standard View permission remains restricted to authenticated users. Classic UI access by anonymous users is blocked at the Zope security layer without requiring any proxy configuration.

### Workflow states

- Private: working draft, visible to editors only. Direct transitions to members only or published available.
- Pending review: submitted for approval. Reviewer can restrict to members or publish.
- Members only: teaser public, full content for authenticated users only.
- Published: fully public, no restrictions.

### Backend

- Custom members_only_workflow with four states and five transitions
- A teaser browser view returning only safe fields for anonymous requests
- Custom View Teaser permission granted to Anonymous in the members_only state
- post_install handler creates the workflow programmatically on install

### Frontend

- Custom 401 error view that detects members-only content and fetches the teaser
- MembersOnlyTeaser component rendering title, description, preview image, and login CTA
- Registered automatically via volto.config.js

## Current status

Complete: workflow definition, permission model, teaser backend endpoint, Volto teaser view component, automatic install handler, private GitHub repository.

In progress: configurable field list via control panel, schema.org and Open Graph head markup, members only badge in listing and search results, uninstall profile cleanup.

## Development setup

Requires Plone 6.1.4+, Volto 18+, Python 3.11+, Node 22+ via nvm, and pnpm.

Backend runs at http://localhost:8080/Plone and frontend at http://localhost:3000.

## Resolved limitations

### Inline preview_image — resolved

Plone's `@@images` view checks the `View` permission on the parent content object. Since anonymous users have `View Teaser` but not `View` on `members_only` content, serving inline images through `@@images` returned a 401.

**Resolution:** A custom `@@teaser-image` view was introduced, protected by `View Teaser` instead of `View`. The `@@teaser` endpoint returns image URLs pointing to `@@teaser-image` rather than `@@images`, so anonymous users can access the image without ever needing `View` on the content object. The frontend constructs fully qualified URLs for `og:image` using `config.settings.publicURL` as the base, ensuring social platforms and Google can resolve the image correctly.
