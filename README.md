# collective.membersonly / volto-members-only

A Plone 6 / Volto addon that enables gated content with a public metadata teaser.

## The problem

Plone's default workflow offers two states for content visibility: private (invisible to anonymous users and search engines) and published (fully public). There is no middle ground for content that should be discoverable but restricted — where Google and logged-out visitors can see a teaser, but the full content requires authentication.

This is a common need for nonprofits and educational institutions that want to surface member resources in search results while keeping the content itself gated.

## The solution

This addon introduces a `members_only` workflow state that sits between private and published. Content in this state returns a 200 OK to anonymous users, serves only safe metadata fields via a dedicated teaser endpoint, serves full content to authenticated users, displays a teaser view in Volto with a login prompt, and appears in site search and listing results with meaningful titles and descriptions.

## Installation

This addon has two components — a Python backend package and a Volto frontend addon — both of which need to be installed separately.

### 1. Backend

Add `collective.membersonly` to your Plone project's Python dependencies. If you are using a `pyproject.toml` based setup:

```toml
dependencies = [
    "collective.membersonly",
]
```

Then install the package and restart your Plone instance. Once running, go to Site Setup and navigate to Add-ons. Find "Plone Members Only" in the available addons list and click Install.

This will:
- Register the `members_only_workflow` in your site's workflow tool
- Add the `Collective Members Only: View Teaser` permission
- Add the Members Only Settings entry to Site Setup
- Register the `@@teaser` and `@@teaser-image` endpoints

### 2. Frontend

Add `volto-members-only` to your Volto project's `volto.config.js`:

```javascript
const addons = ['volto-members-only'];

module.exports = {
  addons,
};
```

Then rebuild and restart your Volto frontend. This step is required — the teaser view, the 401 intercept, and the Open Graph head markup are all in the Volto addon and will not be active until it is listed here.

### 3. Assign the workflow

The addon does not automatically assign `members_only_workflow` to any content types — this is a deliberate site-level decision. After installing, go to Site Setup and navigate to Types. Select each content type you want to use with members-only gating and set its workflow to "Members Only Workflow". Alternatively, if you want all content types to use it by default, you can set it as the site default workflow in the portal_workflow ZMI at: http://yoursite.com/portal_workflow/manage_main

Until this step is done, editors will not see the "Restrict to members" transition in the toolbar.

### Verifying the installation

With both components installed and the workflow assigned, create a new page and transition it to "Members only" via the workflow toolbar. Open the page in an incognito or private browsing window — you should see the teaser view with title, description, and preview image rather than the full page content.

## Architecture

### Security model

The addon introduces a custom permission — `Collective Members Only: View Teaser` — granted to Anonymous in the `members_only` workflow state. The standard `View` permission goes to the **Subscriber** role, shown on the Sharing tab as **"Can view subscription content"** (and to Reader, "Can view"). Classic UI access by anonymous users is blocked at the Zope security layer without requiring any proxy configuration.

- Share a page or folder with people or groups in the "Can view subscription content" column to let them read its members-only content. Sharing on a folder applies to its contents unless "Inherit permissions" is switched off.
- In the private and pending states the role grants nothing, so unpublished items in a shared folder stay hidden.
- **"Any logged-in user can view members-only content"** (Members Only settings, on by default) shares the site root with Logged-in users in that column: the original behaviour, where any account reads members-only content. Switch it off when access should depend on groups, for example with collective.membership.
- Upgrading to profile version 1001 keeps existing sites as they were: the setting is switched on.

### Access message

People who can't read a members-only item see its teaser and a message. By default that's "This content is available to members only" with a login button for anonymous visitors, and "You don't have access to this content" for logged-in people. An add-on can replace it by registering a utility for `collective.membersonly.interfaces.IAccessMessage` that returns `{'text': ..., 'actions': [{'label': ..., 'url': ...}]}`; collective.membership does, naming the plans that include the content.

### Workflow states

- **Private** — working draft, visible to editors only. Direct transitions to members only or published available.
- **Pending review** — submitted for approval. Reviewer can restrict to members or publish.
- **Members only** — teaser public, full content for authenticated users only.
- **Published** — fully public, no restrictions.

### Backend (collective.membersonly)

- Custom `members_only_workflow` with four states and five transitions
- `@@teaser` browser view returning only configured safe fields for anonymous requests
- `@@teaser-image` browser view serving image scales protected by `View Teaser`
- Custom `View Teaser` permission granted to Anonymous in the members_only state
- `post_install` handler creates the workflow programmatically on install
- `uninstall` handler safely retracts all members_only content before removing the workflow
- Registry-based settings controlling which fields surface in the teaser

### Frontend (volto-members-only)

- Custom 401 error view that detects members-only content and fetches the teaser
- `MembersOnlyTeaser` component rendering title, description, preview image, and login CTA
- Full Open Graph and schema.org head markup including `isAccessibleForFree: false`
- Registered automatically via `volto.config.js`

### Configurable fields

Site admins can configure which fields surface in the teaser via Site Setup under Members Only Settings. Available fields are description, preview_image, effective, creators, subjects, and language. Title and review_state are always included regardless of this setting.

The teaser view reads the field list from the Plone registry at request time, so changes take effect immediately without restarting the server.

### Uninstall behaviour

When the addon is uninstalled the handler:

- Finds all content in `members_only` state and retracts it to `private`
- Adds an audit comment to the workflow history of each affected item so editors know what happened and when
- Resets the site default workflow chain if it was set to `members_only_workflow`
- Removes `members_only_workflow` from any explicit content type bindings
- Fixes orphaned workflow history on any remaining affected items
- Removes the addon's registry records
- Removes the Members Only entry from Site Setup

The site is left in a clean state with all previously gated content safely private and all content types bound to their previous workflow.

## Development setup

### Requirements

- Plone 6.1.4+
- Volto 18+
- Python 3.11+
- Node 22+ (via nvm)
- pnpm

### Running locally

```bash
# Backend (terminal 1)
make backend-install
make backend-start

# Frontend (terminal 2)
make frontend-install
make frontend-start
```

Backend runs at http://localhost:8080/Plone
Frontend runs at http://localhost:3000

### Development environment note

In local development the backend runs on port 8080 and the frontend on port 3000. If you log in directly via the Plone interface at 8080, your browser session cookie may be sent with Volto's API requests, causing authenticated content to appear on port 3000 even for pages you expect to be gated.

This is expected behaviour — an authenticated user should see full content. To test the anonymous teaser experience accurately, always use an incognito or private browsing window, which has no session cookies and replicates what Google's crawler and logged-out visitors see.

In production there is only one URL and one login path through Volto, so this distinction does not arise.

## Current status

### Complete

- Workflow definition with all states and transitions
- Permission model (`View Teaser` for anonymous)
- `@@teaser` backend endpoint with configurable field list
- `@@teaser-image` backend endpoint for anonymous image access
- Volto teaser view component with login CTA
- Open Graph and schema.org head markup
- Configurable field control panel in Site Setup
- Safe uninstall with content retraction and audit trail
- Private GitHub repository at juizi-com/plone-members-only

### Planned

- Members only badge in listing and search results

## Resolved limitations

### Inline preview_image

Plone's `@@images` view checks the `View` permission on the parent content object. Since anonymous users have `View Teaser` but not `View` on `members_only` content, serving inline images through `@@images` returned a 401.

**Resolution:** A custom `@@teaser-image` view was introduced, protected by `View Teaser` instead of `View`. The `@@teaser` endpoint returns image URLs pointing to `@@teaser-image` rather than `@@images`, so anonymous users can access the image without ever needing `View` on the content object. The frontend constructs fully qualified URLs for `og:image` using `config.settings.publicURL` as the base, ensuring social platforms and Google can resolve the image correctly.

## Google indexing and honest signalling

A core concern with gated content is that showing a teaser to Google while restricting full access to logged-in users could be interpreted as cloaking — serving different content to crawlers than to users, which violates Google's spam policies.

This addon handles this correctly by implementing Google's recommended pattern for paywalled and subscription-gated content using schema.org structured data.

### How it works

The teaser view includes a JSON-LD block in the page `<head>` that explicitly declares the content as gated:

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "isAccessibleForFree": false,
  "hasPart": {
    "@type": "WebPageElement",
    "isAccessibleForFree": false,
    "cssSelector": ".members-only-gate"
  }
}
```

The `isAccessibleForFree: false` property on the `Article` tells Google the content is gated. The `hasPart` property with `cssSelector` points to the specific element on the page that contains the restricted content — in this case the `.members-only-gate` div which wraps the login prompt. This allows Google to differentiate between the publicly visible teaser and the gated portion.

This is the same pattern used by news publishers and academic journals. Google understands it and indexes the teaser without penalising the site for showing different content to crawlers and users.

### Validation

You can validate the structured data implementation using Google's Rich Results Test at `https://search.google.com/test/rich-results`. The tool specifically supports `isAccessibleForFree` and `cssSelector` validation for paywalled content.

### Further reading

- Google's official documentation: `https://developers.google.com/search/docs/appearance/structured-data/paywalled-content`
- Google's article structured data guide: `https://developers.google.com/search/docs/appearance/structured-data/article`
- General structured data guidelines: `https://developers.google.com/search/docs/appearance/structured-data/sd-policies`

## Deployment considerations

### Reverse proxy caching

This addon serves different content to anonymous and authenticated users at the same URLs — anonymous users get the teaser, authenticated users get the full content. If your reverse proxy (Nginx, Varnish, or a CDN) caches responses without accounting for authentication state, a cached teaser could be served to an authenticated user or a cached full-content response could be served to an anonymous user.

To prevent this, ensure your proxy configuration varies its cache on authentication state. In Nginx:

```nginx
proxy_cache_bypass $cookie_auth_tkt;
proxy_no_cache $cookie_auth_tkt;
```

Or more broadly using the Vary header approach — ensure your Plone/Volto deployment sets `Vary: Cookie` on content responses, which instructs any intermediate cache to keep separate entries for requests with and without session cookies.

If you are using a CDN, configure it to pass through or vary on the `Authorization` header and session cookies for all content URLs.

### Image serving

The `@@teaser-image` view reads image data from the ZODB and serves it directly. For high-traffic sites this may put unnecessary load on the application server. Consider serving images from a dedicated media server or CDN, pointing `preview_image_link` at images stored on a separately cached origin rather than inline `preview_image` fields stored directly on content objects.

### Workflow assignment

The addon does not automatically assign `members_only_workflow` to any content types on install — this is a deliberate site-level decision left to the administrator. After installing the addon, go to the Types control panel in Site Setup and assign `members_only_workflow` to the content types you want to use it with, or set it as the site default workflow if appropriate.
