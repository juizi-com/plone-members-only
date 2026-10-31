import React from 'react';
import MembersOnlyGate from './MembersOnlyGate';
import MembersOnlyTeaser from './MembersOnlyTeaser';
import { teaserRenderer } from '../helpers';

/**
 * The view for members-only content someone can't read: the backend sends
 * the teaser as the page itself (layout "members_only_teaser"), so the
 * site's navigation, breadcrumbs and settings work around it.
 *
 * Another add-on's renderer takes over the page, head included. It gets the
 * teaser and the Gate to show in it.
 */
const MembersOnlyTeaserView = ({ content }) => {
  const Renderer = teaserRenderer(content) || MembersOnlyTeaser;
  return <Renderer content={content} Gate={MembersOnlyGate} />;
};

export default MembersOnlyTeaserView;
