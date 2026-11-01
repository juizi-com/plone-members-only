import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { getBaseUrl } from '@plone/volto/helpers/Url/Url';
import UniversalLink from '@plone/volto/components/manage/UniversalLink/UniversalLink';

/**
 * What a visitor is told and offered instead of the content: the login prompt,
 * or a membership add-on's message. Every teaser shows this element; the
 * gating markup in the page's JSON-LD points at its class.
 */
const MembersOnlyGate = ({ content }) => {
  const location = useLocation();
  const loginUrl = `${getBaseUrl(location.pathname)}/login`;
  const message = content.access_message;

  return (
    <div className="members-only-gate">
      {message ? (
        <>
          <p>{message.text}</p>
          {(message.actions || []).length > 0 && (
            <p className="members-only-actions">
              {message.actions.map((action) => (
                <UniversalLink
                  key={action.url}
                  href={
                    action.url.endsWith('/login')
                      ? `${loginUrl}?return_url=${encodeURIComponent(location.pathname)}`
                      : action.url
                  }
                  className="ui button primary"
                  data-members-only-action={action.label}
                >
                  {action.label}
                </UniversalLink>
              ))}
            </p>
          )}
        </>
      ) : (
        <>
          <p>This content is available to members only.</p>
          <Link
            to={{
              pathname: loginUrl,
              state: { next: location.pathname },
            }}
            className="ui button primary"
            data-members-only-action="login"
          >
            Log in to read
          </Link>
        </>
      )}
    </div>
  );
};

export default MembersOnlyGate;
