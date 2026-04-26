import React from 'react';
import { Container, Image } from 'semantic-ui-react';
import { Link } from 'react-router-dom';
import { useLocation } from 'react-router-dom';
import { getBaseUrl, flattenToAppURL } from '@plone/volto/helpers/Url/Url';

const MembersOnlyTeaser = ({ content }) => {
  const location = useLocation();
  const loginUrl = `${getBaseUrl(location.pathname)}/login`;

  return (
    <Container className="view-wrapper members-only-teaser">
      {content.preview_image && (
        <Image
          src={flattenToAppURL(content.preview_image.download)}
          alt={content.title}
          className="members-only-preview-image"
        />
      )}
      <h1>{content.title}</h1>
      {content.description && (
        <p className="description">{content.description}</p>
      )}
      {content.effective && (
        <p className="members-only-date">
          {new Date(content.effective).toLocaleDateString()}
        </p>
      )}
      {content.creators?.length > 0 && (
        <p className="members-only-creators">{content.creators.join(', ')}</p>
      )}
      <div className="members-only-gate">
        <p>This content is available to members only.</p>
        <Link
          to={{
            pathname: loginUrl,
            state: { next: location.pathname },
          }}
          className="ui button primary"
        >
          Log in to read
        </Link>
      </div>
    </Container>
  );
};

export default MembersOnlyTeaser;
