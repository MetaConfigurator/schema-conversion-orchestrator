# Third-Party Notices

Last reviewed: 2026-06-03.

This project is licensed under [LICENSE](LICENSE). Ordinary source dependencies
are declared in the package manager files:

- Python: `requirements/runtime.txt`, `requirements/dev.txt`
- Node: `external_converters/node/package.json`,
  `external_converters/node/package-lock.json`
- Java/Maven: `external_converters/java/pom.xml`

This notice file is limited to third-party artifacts that are bundled, shaded,
vendored, or otherwise easy to miss from the normal dependency declarations.

## Bundled Artifacts

### ROBOT

`external_converters/robot/robot.jar` is bundled and used as an external Java
process for OWL/OBO conversions.

ROBOT is distributed by the OBO Library project. Public project documentation
and the ROBOT paper report ROBOT as BSD-3-Clause licensed:

- https://robot.obolibrary.org/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC6664714/

Before distributing binaries or Docker images, confirm the license for the exact
ROBOT JAR version bundled in this repository and include any required license
text or notices with the release artifact.