# Release v2.1.0

This branch contains the preparation for releasing version 2.1.0 of the claude-marketplace.

## Tag Created

A git tag `v2.1.0` has been created locally pointing to commit `5584fc0`:

```
tag v2.1.0
Tagger: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Date:   Tue Nov 18 03:38:01 2025 +0000

Release version 2.1.0

commit 5584fc02f2f8792908636f48b9bab7bbaece1e08
```

## Repository Rule Restriction

The tag cannot be pushed directly due to GitHub repository rules that restrict tag creation:

```
remote: error: GH013: Repository rule violations found for refs/tags/v2.1.0.
remote: - Cannot create ref due to creations being restricted.
```

## Next Steps

To complete the release, a repository maintainer with appropriate permissions needs to:

1. **Option A - Create tag via GitHub UI:**
   - Go to https://github.com/letzdoo/claude-marketplace/releases/new
   - Create a new release with tag `v2.1.0`
   - Target the master branch at commit `5584fc0`
   - Add release notes if desired

2. **Option B - Create tag with elevated permissions:**
   ```bash
   git tag -a v2.1.0 5584fc0 -m "Release version 2.1.0"
   git push origin v2.1.0
   ```

3. **Option C - Merge this PR and create tag on master:**
   - Merge this PR to master
   - Create the tag on master branch after merge

## VERSION File

A VERSION file has been added to the repository containing `2.1.0` to document the version.
