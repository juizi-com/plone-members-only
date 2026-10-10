import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { withServerErrorCode } from '@plone/volto/helpers/Utils/Utils';
import { getBaseUrl } from '@plone/volto/helpers/Url/Url';
import config from '@plone/volto/registry';
import MembersOnlyTeaser from './MembersOnlyTeaser';

const MembersOnlyUnauthorized = () => {
  const location = useLocation();
  const token = useSelector((state) => state.userSession.token);
  const [teaserContent, setTeaserContent] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Logged-in people may lack access too (content shared with some
    // groups only): they get the teaser and a message meant for them.
    const teaserUrl = `${config.settings.apiPath}/++api++${getBaseUrl(location.pathname)}/@@teaser`;

    fetch(teaserUrl, {
      headers: {
        Accept: 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    })
      .then((res) => {
        if (res.ok) return res.json();
        return null;
      })
      .then((data) => {
        if (data?.is_members_only) {
          setTeaserContent(data);
        }
        setLoading(false);
      })
      .catch((err) => {
        setLoading(false);
      });
  }, [location.pathname, token]);

  if (loading) return null;

  if (teaserContent) {
    return <MembersOnlyTeaser content={teaserContent} />;
  }

  // Fall back to standard unauthorized message
  const DefaultUnauthorized =
    require('@plone/volto/components/theme/Unauthorized/Unauthorized').default;
  return <DefaultUnauthorized />;
};

const MembersOnlyUnauthorizedWithCode = withServerErrorCode(401)(
  MembersOnlyUnauthorized,
);
MembersOnlyUnauthorizedWithCode.displayName = 'unauthorized';
export default MembersOnlyUnauthorizedWithCode;
