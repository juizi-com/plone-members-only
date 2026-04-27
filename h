[33m3338bae[m[33m ([m[1;36mHEAD -> [m[1;32mmain[m[33m, [m[1;31morigin/main[m[33m)[m Replace generated README with project documentation
 README.md | 157 [32m++++++++++++++++++++[m[31m----------------------------------------------------------------------------------[m
 1 file changed, 30 insertions(+), 127 deletions(-)
[33m5e19e89[m Add Volto teaser view and update README with current status
 frontend/packages/volto-members-only/src/components/MembersOnlyTeaser.jsx   | 48 [32m++++++++++++++++++++++++++++++[m
 .../packages/volto-members-only/src/components/MembersOnlyUnauthorized.jsx  | 59 [32m+++++++++++++++++++++++++++++++++++++[m
 frontend/packages/volto-members-only/src/config/settings.ts                 |  2 [32m+[m[31m-[m
 frontend/packages/volto-members-only/src/index.ts                           |  3 [32m++[m
 4 files changed, 111 insertions(+), 1 deletion(-)
[33mcf5791b[m Add @@teaser endpoint and members-only serialiser
 backend/src/collective/membersonly/configure.zcml             |  2 [32m++[m
 backend/src/collective/membersonly/overrides.zcml             | 11 [32m++++++++++[m
 backend/src/collective/membersonly/serializers/configure.zcml |  7 [32m+++[m[31m----[m
 backend/src/collective/membersonly/serializers/summary.py     | 58 [32m++++++++++++++++++++++++++++++++++++++++++++++++++[m[31m-[m
 backend/src/collective/membersonly/views/__init__.py          |  0
 backend/src/collective/membersonly/views/configure.zcml       | 12 [32m+++++++++++[m
 backend/src/collective/membersonly/views/teaser.py            | 53 [32m++++++++++++++++++++++++++++++++++++++++++++++[m
 7 files changed, 138 insertions(+), 5 deletions(-)
[33mecf6460[m Add members_only_workflow with permission-based teaser access
 .editorconfig                                                               |    35 [32m+[m
 .github/instructions/docs.instructions.md                                   |    69 [32m+[m
 .github/instructions/general/docs.md                                        |   126 [32m+[m
 .github/instructions/volto.instructions.md                                  |    75 [32m+[m
 .github/workflows/backend.yml                                               |    97 [32m+[m
 .github/workflows/changelog.yml                                             |   135 [32m+[m
 .github/workflows/config.yml                                                |   115 [32m+[m
 .github/workflows/docs.yml                                                  |    22 [32m+[m
 .github/workflows/frontend.yml                                              |   107 [32m+[m
 .github/workflows/main.yml                                                  |    77 [32m+[m
 .github/workflows/rtd-pr-preview.yml                                        |    27 [32m+[m
 .gitignore                                                                  |     5 [32m+[m
 .readthedocs.yml                                                            |    25 [32m+[m
 .vscode/extensions.json                                                     |    15 [32m+[m
 .vscode/launch.json                                                         |    19 [32m+[m
 .vscode/settings.json                                                       |    25 [32m+[m
 CHANGELOG.md                                                                |     9 [32m+[m
 Makefile                                                                    |   249 [32m+[m
 README.md                                                                   |   148 [32m+[m
 backend/.dockerignore                                                       |    14 [32m+[m
 backend/.editorconfig                                                       |    35 [32m+[m
 backend/.flake8                                                             |    22 [32m+[m
 backend/.gitignore                                                          |    45 [32m+[m
 backend/CHANGELOG.md                                                        |    10 [32m+[m
 backend/CONTRIBUTORS.md                                                     |     3 [32m+[m
 backend/Dockerfile                                                          |    38 [32m+[m
 backend/Dockerfile.acceptance                                               |    40 [32m+[m
 backend/LICENSE.GPL                                                         |   339 [32m+[m
 backend/LICENSE.md                                                          |    15 [32m+[m
 backend/Makefile                                                            |   171 [32m+[m
 backend/README.md                                                           |    87 [32m+[m
 backend/bobtemplate.cfg                                                     |     7 [32m+[m
 backend/instance.yaml                                                       |     5 [32m+[m
 backend/mx.ini                                                              |    17 [32m+[m
 backend/news/.changelog_template.jinja                                      |    15 [32m+[m
 backend/news/.gitkeep                                                       |     1 [32m+[m
 backend/pyproject.toml                                                      |   185 [32m+[m
 backend/scripts/create_site.py                                              |    74 [32m+[m
 backend/src/collective/membersonly/__init__.py                              |    14 [32m+[m
 backend/src/collective/membersonly/configure.zcml                           |    26 [32m+[m
 backend/src/collective/membersonly/content/__init__.py                      |     0
 backend/src/collective/membersonly/controlpanels/__init__.py                |     0
 backend/src/collective/membersonly/controlpanels/configure.zcml             |    10 [32m+[m
 backend/src/collective/membersonly/dependencies.zcml                        |     7 [32m+[m
 backend/src/collective/membersonly/indexers/__init__.py                     |     0
 backend/src/collective/membersonly/indexers/configure.zcml                  |     7 [32m+[m
 backend/src/collective/membersonly/interfaces.py                            |     7 [32m+[m
 backend/src/collective/membersonly/locales/__init__.py                      |     0
 backend/src/collective/membersonly/locales/__main__.py                      |    69 [32m+[m
 backend/src/collective/membersonly/locales/collective.membersonly.pot       |    18 [32m+[m
 .../collective/membersonly/locales/de/LC_MESSAGES/collective.membersonly.po |    15 [32m+[m
 .../collective/membersonly/locales/en/LC_MESSAGES/collective.membersonly.po |    15 [32m+[m
 .../collective/membersonly/locales/es/LC_MESSAGES/collective.membersonly.po |    15 [32m+[m
 .../collective/membersonly/locales/it/LC_MESSAGES/collective.membersonly.po |    15 [32m+[m
 .../membersonly/locales/pt_BR/LC_MESSAGES/collective.membersonly.po         |    15 [32m+[m
 backend/src/collective/membersonly/permissions.zcml                         |     8 [32m+[m
 backend/src/collective/membersonly/profiles.zcml                            |    42 [32m+[m
 backend/src/collective/membersonly/profiles/default/browserlayer.xml        |     6 [32m+[m
 backend/src/collective/membersonly/profiles/default/catalog.xml             |    13 [32m+[m
 backend/src/collective/membersonly/profiles/default/controlpanel.xml        |     8 [32m+[m
 backend/src/collective/membersonly/profiles/default/diff_tool.xml           |     6 [32m+[m
 backend/src/collective/membersonly/profiles/default/metadata.xml            |     7 [32m+[m
 backend/src/collective/membersonly/profiles/default/registry/.gitkeep       |     0
 backend/src/collective/membersonly/profiles/default/registry/main.xml       |     8 [32m+[m
 backend/src/collective/membersonly/profiles/default/repositorytool.xml      |     6 [32m+[m
 backend/src/collective/membersonly/profiles/default/rolemap.xml             |    17 [32m+[m
 backend/src/collective/membersonly/profiles/default/types.xml               |    10 [32m+[m
 backend/src/collective/membersonly/profiles/default/types/.gitkeep          |     0
 .../profiles/default/workflows/members_only_workflow/definition.xml         |   282 [32m+[m
 backend/src/collective/membersonly/profiles/default/workflows/workflows.xml |     8 [32m+[m
 backend/src/collective/membersonly/profiles/initial/metadata.xml            |     4 [32m+[m
 backend/src/collective/membersonly/profiles/uninstall/browserlayer.xml      |     6 [32m+[m
 backend/src/collective/membersonly/serializers/__init__.py                  |     0
 backend/src/collective/membersonly/serializers/configure.zcml               |    10 [32m+[m
 backend/src/collective/membersonly/serializers/summary.py                   |    10 [32m+[m
 backend/src/collective/membersonly/setuphandlers/__init__.py                |    70 [32m+[m
 backend/src/collective/membersonly/setuphandlers/examplecontent/.gitkeep    |     0
 .../membersonly/setuphandlers/examplecontent/content/__metadata__.json      |    40 [32m+[m
 .../examplecontent/content/a58ccead718140c1baa98d43595fc3e6/data.json       |    56 [32m+[m
 .../content/a58ccead718140c1baa98d43595fc3e6/image/plone-foundation.png     |   Bin [31m0[m -> [32m50737[m bytes
 .../examplecontent/content/a720393b3c0240e5bd27c43fcd2cfd1e/data.json       |    98 [32m+[m
 .../setuphandlers/examplecontent/content/plone_site_root/data.json          |   267 [32m+[m
 .../src/collective/membersonly/setuphandlers/examplecontent/principals.json |     4 [32m+[m
 .../src/collective/membersonly/setuphandlers/examplecontent/redirects.json  |     1 [32m+[m
 .../src/collective/membersonly/setuphandlers/examplecontent/relations.json  |     1 [32m+[m
 .../collective/membersonly/setuphandlers/examplecontent/translations.json   |     1 [32m+[m
 backend/src/collective/membersonly/setuphandlers/initial.py                 |    16 [32m+[m
 backend/src/collective/membersonly/testing.py                               |    49 [32m+[m
 backend/src/collective/membersonly/upgrades/__init__.py                     |     0
 backend/src/collective/membersonly/upgrades/configure.zcml                  |    21 [32m+[m
 backend/src/collective/membersonly/vocabularies/__init__.py                 |     0
 backend/src/collective/membersonly/vocabularies/configure.zcml              |     5 [32m+[m
 backend/tests/conftest.py                                                   |    16 [32m+[m
 backend/tests/setup/test_setup_install.py                                   |    17 [32m+[m
 backend/tests/setup/test_setup_uninstall.py                                 |    19 [32m+[m
 backend/version.txt                                                         |     1 [32m+[m
 dependabot.yml                                                              |     8 [32m+[m
 docker-compose.yml                                                          |   100 [32m+[m
 docs/.gitignore                                                             |     7 [32m+[m
 docs/.vale.ini                                                              |    12 [32m+[m
 docs/Makefile                                                               |   138 [32m+[m
 docs/README.md                                                              |   124 [32m+[m
 docs/docs/_static/favicon.ico                                               |   Bin [31m0[m -> [32m15406[m bytes
 docs/docs/_static/logo.svg                                                  |    54 [32m+[m
 docs/docs/_templates/404.html                                               |    20 [32m+[m
 docs/docs/concepts/index.md                                                 |    20 [32m+[m
 docs/docs/conf.py                                                           |   368 [32m+[m
 docs/docs/glossary.md                                                       |    57 [32m+[m
 docs/docs/how-to-guides/index.md                                            |    30 [32m+[m
 docs/docs/index.md                                                          |    60 [32m+[m
 docs/docs/reference/index.md                                                |    23 [32m+[m
 docs/docs/robots.txt                                                        |     8 [32m+[m
 docs/docs/tutorials/index.md                                                |    19 [32m+[m
 docs/pyproject.toml                                                         |    61 [32m+[m
 docs/styles/config/vocabularies/Base/accept.txt                             |     0
 docs/styles/config/vocabularies/Base/reject.txt                             |     0
 docs/styles/config/vocabularies/Plone/accept.txt                            |    51 [32m+[m
 docs/styles/config/vocabularies/Plone/reject.txt                            |     3 [32m+[m
 frontend/.dockerignore                                                      |     6 [32m+[m
 frontend/.eslintrc.js                                                       |    41 [32m+[m
 frontend/.gitignore                                                         |    13 [32m+[m
 frontend/.npmignore                                                         |    16 [32m+[m
 frontend/.npmrc                                                             |     6 [32m+[m
 frontend/.prettierignore                                                    |     3 [32m+[m
 frontend/.prettierrc                                                        |    12 [32m+[m
 frontend/.storybook/main.js                                                 |   192 [32m+[m
 frontend/.storybook/preview.jsx                                             |    26 [32m+[m
 frontend/.stylelintrc                                                       |    32 [32m+[m
 frontend/Dockerfile                                                         |    38 [32m+[m
 frontend/Makefile                                                           |   159 [32m+[m
 frontend/README.md                                                          |   195 [32m+[m
 frontend/cypress.config.js                                                  |    13 [32m+[m
 frontend/cypress/.gitkeep                                                   |     0
 frontend/cypress/support/commands.js                                        |     1 [32m+[m
 frontend/cypress/support/e2e.js                                             |    15 [32m+[m
 frontend/cypress/support/index.ts                                           |    43 [32m+[m
 frontend/cypress/tests/.gitkeep                                             |     0
 frontend/cypress/tests/example.cy.js                                        |    22 [32m+[m
 frontend/cypress/tsconfig.json                                              |     8 [32m+[m
 frontend/jest-addon.config.js                                               |    17 [32m+[m
 frontend/mrs.developer.json                                                 |    10 [32m+[m
 frontend/package.json                                                       |    50 [32m+[m
 frontend/packages/volto-members-only/.gitignore                             |     3 [32m+[m
 frontend/packages/volto-members-only/.release-it.json                       |    34 [32m+[m
 frontend/packages/volto-members-only/CHANGELOG.md                           |     9 [32m+[m
 frontend/packages/volto-members-only/babel.config.js                        |    17 [32m+[m
 frontend/packages/volto-members-only/locales/de/LC_MESSAGES/volto.po        |    12 [32m+[m
 frontend/packages/volto-members-only/locales/en/LC_MESSAGES/volto.po        |    12 [32m+[m
 frontend/packages/volto-members-only/locales/es/LC_MESSAGES/volto.po        |    19 [32m+[m
 frontend/packages/volto-members-only/locales/pt_BR/LC_MESSAGES/volto.po     |    17 [32m+[m
 frontend/packages/volto-members-only/locales/volto.pot                      |    14 [32m+[m
 frontend/packages/volto-members-only/news/.gitkeep                          |     0
 frontend/packages/volto-members-only/package.json                           |    45 [32m+[m
 frontend/packages/volto-members-only/public/.gitkeep                        |     0
 frontend/packages/volto-members-only/src/components/.gitkeep                |     0
 frontend/packages/volto-members-only/src/config/settings.ts                 |     5 [32m+[m
 frontend/packages/volto-members-only/src/index.ts                           |    10 [32m+[m
 frontend/packages/volto-members-only/towncrier.toml                         |    33 [32m+[m
 frontend/packages/volto-members-only/tsconfig.json                          |    30 [32m+[m
 frontend/pnpm-lock.yaml                                                     | 30287 [32m++++++++++++++++++++++++++++++++++[m
 frontend/pnpm-workspace.yaml                                                |     5 [32m+[m
 frontend/volto.config.js                                                    |     7 [32m+[m
 news/.changelog_template.jinja                                              |    15 [32m+[m
 repository.toml                                                             |    32 [32m+[m
 towncrier.toml                                                              |    33 [32m+[m
 version.txt                                                                 |     1 [32m+[m
 166 files changed, 36590 insertions(+)
