import type { ConfigType } from '@plone/registry';
import MembersOnlyBadge from '../components/MembersOnlyBadge';
import { GATE_SELECTOR, gatingJsonLd, isGated } from '../helpers';

/**
 * What other add-ons can use. Optional for them, and read when rendering, so
 * neither add-on needs the other and the order they load in doesn't matter.
 * The version goes up when something here changes.
 */
export const capabilities = {
  version: 1,
  gateSelector: GATE_SELECTOR,
  gatingJsonLd,
  isGated,
  Badge: MembersOnlyBadge,
};

export default function install(config: ConfigType) {
  config.settings.membersOnly = capabilities;
  return config;
}
