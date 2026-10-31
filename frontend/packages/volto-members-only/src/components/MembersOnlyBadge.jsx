import React from 'react';
import { isGated } from '../helpers';

/** For cards: works from the listing data, with no request per item. */
const MembersOnlyBadge = ({ item }) =>
  isGated(item) ? (
    <span className="members-only-badge">Members only</span>
  ) : null;

export default MembersOnlyBadge;
