import config from '@plone/volto/registry';

/** Renderers must include it: the gating markup points at it. */
export const GATE_SELECTOR = '.members-only-gate';

/**
 * The gating markup for an item, to merge into JSON-LD: how Google can tell a
 * teaser from cloaking. Nothing for content that isn't gated.
 */
export const gatingJsonLd = (content) =>
  isGated(content)
    ? {
        isAccessibleForFree: false,
        hasPart: {
          '@type': 'WebPageElement',
          isAccessibleForFree: false,
          cssSelector: GATE_SELECTOR,
        },
      }
    : {};

/**
 * Whether content is gated. A full item or a teaser has an access block,
 * a listing item a flag. Older backends only have is_members_only.
 */
export const isGated = (content) =>
  content?.members_only === true ||
  content?.members_only?.gated === true ||
  content?.is_members_only === true;

/**
 * The renderer for a teaser: another add-on's, if one wants this content,
 * otherwise none. Add-ons register one through the registry, so the order
 * add-ons load in doesn't matter:
 *
 *   config.registerUtility({
 *     name: 'my-addon',
 *     type: 'membersOnlyTeaserRenderer',
 *     method: (content) => (isMine(content) ? MyTeaser : null),
 *   });
 */
export const teaserRenderer = (content) => {
  const renderers = config.getUtilities({ type: 'membersOnlyTeaserRenderer' });
  for (const { method } of renderers) {
    const renderer = method(content);
    if (renderer) return renderer;
  }
  return null;
};
