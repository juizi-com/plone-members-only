import config from '@plone/volto/registry';
import { gatingJsonLd, isGated, teaserRenderer } from './helpers';

describe('isGated', () => {
  it('reads the access block, the listing flag and older backends', () => {
    expect(isGated({ members_only: { gated: true, can_view: true } })).toBe(
      true,
    );
    expect(isGated({ members_only: true })).toBe(true);
    expect(isGated({ is_members_only: true })).toBe(true);
  });

  it('is false for everything else', () => {
    expect(isGated({ members_only: { gated: false } })).toBe(false);
    expect(isGated({ members_only: false })).toBe(false);
    expect(isGated({})).toBe(false);
    expect(isGated(null)).toBe(false);
  });
});

describe('gatingJsonLd', () => {
  it('marks gated content, pointing at the gate', () => {
    const result = gatingJsonLd({ members_only: { gated: true } });
    expect(result.isAccessibleForFree).toBe(false);
    expect(result.hasPart.cssSelector).toBe('.members-only-gate');
  });

  it('adds nothing to other content', () => {
    expect(gatingJsonLd({ members_only: { gated: false } })).toEqual({});
  });
});

describe('teaserRenderer', () => {
  it('is nothing with no renderer registered', () => {
    expect(teaserRenderer({ '@type': 'Document' })).toBeNull();
  });

  it('asks each renderer', () => {
    const Mine = () => null;
    config.registerUtility({
      name: 'other',
      type: 'membersOnlyTeaserRenderer',
      method: () => null,
    });
    config.registerUtility({
      name: 'mine',
      type: 'membersOnlyTeaserRenderer',
      method: (content) => (content['@type'] === 'Mine' ? Mine : null),
    });
    expect(teaserRenderer({ '@type': 'Mine' })).toBe(Mine);
    expect(teaserRenderer({ '@type': 'Document' })).toBeNull();
  });
});
