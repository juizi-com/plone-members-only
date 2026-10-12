import type { ConfigType } from '@plone/registry';
import installSettings from './config/settings';
import MembersOnlyUnauthorized from './components/MembersOnlyUnauthorized';
import MembersOnlyTeaserView from './components/MembersOnlyTeaserView';

function applyConfig(config: ConfigType) {
  installSettings(config);

  // Members-only content someone can't read comes as a teaser page.
  config.views.layoutViews.members_only_teaser = MembersOnlyTeaserView;
  // For backends that still answer 401: the teaser from @@teaser.
  config.views.errorViews['401'] = MembersOnlyUnauthorized;

  return config;
}

export default applyConfig;
