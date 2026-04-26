import type { ConfigType } from '@plone/registry';
import installSettings from './config/settings';
import MembersOnlyUnauthorized from './components/MembersOnlyUnauthorized';

function applyConfig(config: ConfigType) {
  installSettings(config);

  config.views.errorViews['401'] = MembersOnlyUnauthorized;

  return config;
}

export default applyConfig;
