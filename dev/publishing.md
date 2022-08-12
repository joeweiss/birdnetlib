# Releasing a new version and publishing to PyPi

1. Increment the version number in pyproject.toml
2. Commit change to Main
3. Wait for tests via Github Actions (do not cancel test, as the badges are determined by Test action)
4. Make new release using the same version number from above (which will run tests before deploying to PyPi)
