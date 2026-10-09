import React from 'react';
import { Container, Image } from 'semantic-ui-react';
import { Link } from 'react-router-dom';
import { useLocation } from 'react-router-dom';
import { Helmet } from '@plone/volto/helpers';
import { getBaseUrl, flattenToAppURL } from '@plone/volto/helpers/Url/Url';
import config from '@plone/volto/registry';
import { UniversalLink } from '@plone/volto/components';

const MembersOnlyTeaser = ({ content }) => {
  const location = useLocation();
  const loginUrl = `${getBaseUrl(location.pathname)}/login`;
  const siteUrl = config.settings.publicURL || config.settings.apiPath;
  const canonicalUrl = `${siteUrl}${location.pathname}`;

  const getImageUrl = (download) => {
    if (!download) return null;
    const flat = flattenToAppURL(download);
    // If it's a teaser-image URL, route through the API proxy
    if (flat.includes('@@teaser-image')) {
      return `${config.settings.apiPath}/++api++${flat}`;
    }
    // Ensure fully qualified URL for og:image
    if (flat.startsWith('/')) {
      const publicURL = config.settings.publicURL || config.settings.apiPath;
      return `${publicURL}${flat}`;
    }
    return flat;
  };

  const ogImage = getImageUrl(content.preview_image?.download);
  // From the backend: the login prompt, or a membership add-on's message.
  const message = content.access_message;

  return (
    <>
      <Helmet>
        {/* Basic */}
        {content.title && <title>{content.title}</title>}
        {content.description && (
          <meta name="description" content={content.description} />
        )}

        {/* Open Graph */}
        {content.title && <meta property="og:title" content={content.title} />}
        {content.description && (
          <meta property="og:description" content={content.description} />
        )}
        <meta property="og:type" content="article" />
        <meta property="og:url" content={canonicalUrl} />
        {ogImage && <meta property="og:image" content={ogImage} />}

        {/* Twitter */}
        <meta name="twitter:card" content="summary_large_image" />
        {content.title && <meta name="twitter:title" content={content.title} />}
        {content.description && (
          <meta name="twitter:description" content={content.description} />
        )}
        {ogImage && <meta name="twitter:image" content={ogImage} />}

        {/* schema.org — honest gating signal for Google */}
        <script type="application/ld+json">
          {JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Article',
            headline: content.title,
            description: content.description,
            url: canonicalUrl,
            datePublished: content.effective,
            author: content.creators?.map((c) => ({
              '@type': 'Person',
              name: c,
            })),
            isAccessibleForFree: false,
            hasPart: {
              '@type': 'WebPageElement',
              isAccessibleForFree: false,
              cssSelector: '.members-only-gate',
            },
            ...(ogImage ? { image: ogImage } : {}),
          })}
        </script>

        {/* Tell robots to index the teaser but not follow gated links */}
        <meta name="robots" content="index, follow" />
      </Helmet>

      <Container className="view-wrapper members-only-teaser">
        {ogImage && (
          <Image
            src={ogImage}
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
              >
                Log in to read
              </Link>
            </>
          )}
        </div>
      </Container>
    </>
  );
};

export default MembersOnlyTeaser;
