import type { ConfigType } from '@plone/registry';
import installSettings from './config/settings';
import MembersOnlyUnauthorized from './components/MembersOnlyUnauthorized';
import MembersOnlyTeaserView from './components/MembersOnlyTeaserView';
import offerAddon, { availableAddon } from './offerAddon';
import packageJson from '../package.json';

function applyConfig(config: ConfigType) {
  installSettings(config);

  // Members-only content someone can't read comes as a teaser page.
  config.views.layoutViews.members_only_teaser = MembersOnlyTeaserView;
  // For backends that still answer 401: the teaser from @@teaser.
  config.views.errorViews['401'] = MembersOnlyUnauthorized;

  // Site Setup → Add-ons offers the backend add-on on this frontend; the
  // backend lists it only once it's installed (offerAddon.js).
  offerAddon(
    config,
    availableAddon({
      id: 'collective.membersonly',
      title: 'Plone Members Only',
      description:
        'Gated content with public metadata teaser for Plone 6 / Volto sites. Needs the volto-members-only frontend add-on.',
      version: packageJson.version,
    }),
  );
  return config;
}

export default applyConfig;
