# collective.membersonly / volto-members-only

A Plone 6 / Volto addon that enables gated content with a public metadata teaser.

## The problem

Plone's default workflow offers two states for content visibility: private (invisible to anonymous users and search engines) and published (fully public). There is no middle ground for content that should be discoverable but restricted — where Google and logged-out visitors can see a teaser, but the full content requires authentication.

This is a common need for nonprofits and educational institutions that want to surface member resources in search results while keeping the content itself gated.

## The solution

This addon introduces a `members_only` workflow state that sits between private and published. Content in this state returns a 200 OK to anonymous users, serves only safe metadata fields via a dedicated teaser endpoint, serves full content to the people it's shared with (or to any logged-in user, if the site keeps that setting on), displays a teaser view in Volto with a login prompt, and appears in site search and listing results with meaningful titles and descriptions.

## Installation

This addon has two components — a Python backend package and a Volto frontend addon — both of which need to be installed separately.

### 1. Backend

Add `collective.membersonly` to your Plone project's Python dependencies. If you are using a `pyproject.toml` based setup:

```toml
dependencies = [
    "collective.membersonly",
]
```

The package loads through plone.autoinclude like any other add-on. It has no load-order requirement and needs no `zcml_package_includes` entry; it runs alongside other add-ons, also on a backend that serves several sites. (Before plone-members-only#6, its `overrides.zcml` made Zope refuse to start when another package loaded plone.restapi first.)

Then install the package and restart your Plone instance. Once the frontend add-on (step 2) is in place too, go to Site Setup → Add-ons, find "Plone Members Only" among the available add-ons and click Install.

Site Setup → Add-ons lists it only on a frontend that includes `volto-members-only` (step 2). The backend leaves it out of its add-ons list until it's installed on the site (`setuphandlers.HiddenProfiles`): one backend can serve several sites, and only those whose frontend has the Volto add-on can use it (without it, visitors would get the teaser data with no teaser page), so that frontend adds it to the list itself (`frontend/packages/volto-members-only/src/offerAddon.js`). Once installed it's listed as usual, for upgrades and uninstalling. A policy profile that depends on it still installs it directly.

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

Then rebuild and restart your Volto frontend. This step is required — the teaser view and the Open Graph head markup are all in the Volto addon and will not be active until it is listed here.

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
- **Members only** — teaser public; full content for people with "Can view subscription content" on the item or above it (any logged-in user while that setting is on).
- **Published** — fully public, no restrictions.

### Backend (collective.membersonly)

- Custom `members_only_workflow` with four states and five transitions
- Content GET (plone.restapi) answers people who can't read members-only content with its teaser as a page (layout `members_only_teaser`) rather than a 401, keeping `@components` (navigation, breadcrumbs, actions, inherited settings) so the site's header and menus work around it; all other content still needs View
- `@@teaser` browser view returning only configured safe fields for anonymous requests
- `@@teaser-image` browser view serving image scales protected by `View Teaser`
- Custom `View Teaser` permission granted to Anonymous in the members_only state
- `post_install` handler creates the workflow programmatically on install
- `uninstall` handler safely retracts all members_only content before removing the workflow
- Registry-based settings controlling which fields surface in the teaser
- Content responses and listings say what's members-only (`members_only`)

### Frontend (volto-members-only)

- `members_only_teaser` view for the teaser page the backend sends
- A 401 error view that detects members-only content and fetches the teaser, for backends without the teaser page
- `MembersOnlyTeaser` component rendering title, description, preview image, the access message and its actions (dates read day-month-year, e.g. 9 October 2026)
- Full Open Graph and schema.org head markup including `isAccessibleForFree: false`
- Offers collective.membersonly in Site Setup → Add-ons (`offerAddon.js`), which the backend leaves out of the list until it is installed on the site; it wraps any add-ons reducer configured before it
- Registered automatically via `volto.config.js`
- `config.settings.membersOnly` for other add-ons: see [Building on members-only](#building-on-members-only)

### Configurable fields

Site admins can configure which fields surface in the teaser via Site Setup under Members Only Settings. Available fields are description, preview_image, effective, creators, subjects, and language, plus any other add-on offers. Title and review_state are always included regardless of this setting.

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

## Building on members-only

Nothing here is needed to use the add-on. Each part is optional, for add-ons that want gated content to look like their own, and neither side has to depend on the other.

### Is this gated, and can this visitor see it?

Don't work it out from a state name or a layout. Every content response has:

```json
"members_only": { "gated": true, "can_view": false }
```

Listings and search results have `"members_only": true` or `false`, with no request per item. Who can view something is per person, so listings can't say.

### Offering teaser fields (backend)

The teaser is built by hand, so a field from a behaviour only appears if it's offered. Register a named utility:

```python
from collective.membersonly.interfaces import ITeaserFieldProvider
from collective.membersonly.interfaces import TeaserField
from zope.interface import implementer


@implementer(ITeaserFieldProvider)
class MyTeaserFields:
    def fields(self, site):
        # Utilities are per instance, and an instance can host sites without
        # your add-on: return nothing for those.
        return (
            TeaserField("summary", "Summary", default=True),
            TeaserField(
                "publisher",
                "Publisher",
                serialize=lambda obj, request: obj.publisher.title,
            ),
            TeaserField("attachment", never_public=True),
        )
```

Register it in ZCML with `zcml:condition="installed collective.membersonly"`, so your add-on still works without this one.

- **Fields appear in the settings panel,** and the site admin decides. `default=True` means on until an admin has saved the panel without it. It works the same whichever add-on is installed first.
- **`never_public` refuses a field.** It isn't offered, and stays out of the teaser whatever is stored and whoever else offers it. A provider can refuse a built-in field too. Use it for files.
- **`serialize`** gets `(context, request)` and returns something JSON compatible. Without it, the attribute of that name is used. An empty value leaves the field out.
- **A field can't replace what's in the teaser already,** and a field or provider that fails is logged and left out.

### Rendering a teaser (frontend)

Register a renderer for content you want to show yourself. Add-on load order doesn't matter:

```js
config.registerUtility({
  name: 'my-addon',
  type: 'membersOnlyTeaserRenderer',
  method: (content) => (content['@type'] === 'Book' ? BookTeaser : null),
});
```

`BookTeaser` gets `content` and `Gate`, and **must render `<Gate content={content} />`:** that's the access message and its actions, and the gating markup points at its class.

A renderer replaces the whole teaser, head output included. So it owns the page's tags, and there's no way to end up with two sets of them. Use `gatingJsonLd` to stay honest with Google.

### `config.settings.membersOnly`

Check for it when rendering, not when loading:

| Name | What it is |
|---|---|
| `version` | Goes up when something here changes |
| `gatingJsonLd(content)` | `isAccessibleForFree` and `hasPart` to merge into your JSON-LD; nothing for content that isn't gated |
| `gateSelector` | `.members-only-gate` |
| `isGated(content)` | Whether a full item, a teaser or a listing item is gated |
| `Badge` | `<Badge item={item} />`: "Members only" on a card, from the listing data |

### Tracking

The gate's links have a `data-members-only-action` attribute with the action's label, so a site can track teaser views that lead to a login or a subscription without custom code.

### Sitemap

Gated items are in the sitemap: they reach anonymous `@search`, which is what Volto builds it from.

## Current status

### Complete

- Workflow definition with all states and transitions
- Permission model (`View Teaser` for anonymous)
- `@@teaser` backend endpoint with configurable field list
- `@@teaser-image` backend endpoint for anonymous image access
- Volto teaser view component with login CTA
- Open Graph and schema.org head markup
- Configurable field control panel in Site Setup (Classic and Volto)
- Subscriber role ("Can view subscription content") and the "Any logged-in user can view members-only content" setting
- Access message extension point (`IAccessMessage`), used by collective.membership
- Safe uninstall with content retraction and audit trail
- Private GitHub repository at juizi-com/plone-members-only
- Extension points for other add-ons: access information, teaser fields, teaser renderers and the Members only badge

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
