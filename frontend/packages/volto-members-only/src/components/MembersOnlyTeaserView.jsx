import React from 'react';
import MembersOnlyTeaser from './MembersOnlyTeaser';

/**
 * The view for members-only content someone can't read: the backend sends
 * the teaser as the page itself (layout "members_only_teaser"), so the
 * site's navigation, breadcrumbs and settings work around it.
 */
const MembersOnlyTeaserView = ({ content }) => (
  <MembersOnlyTeaser content={content} />
);

export default MembersOnlyTeaserView;
