# This markdown has been downloaded from https://github.com/aws-samples

These instructions are for adding a local copy of the Hugo Learn theme to your downloaded AWS Workshop markdown.

1. To automate local setup for rendering this markdown in a Hugo theme we've included `theme.sh` in this repository.
    Note: this script assumes you are running it from within a repository. If you have moved files outside of the original `git clone` directory you may need to run `git init` from the /workshop directory so the Hugo theme can be cloned locally.
2. In a terminal window run `bash theme.sh` to clone the Hugo Learn theme to the correct location. This script will also update the `config.toml` file to point to the new theme.
3. From the workshop directory run `hugo serve` to build the local environment using Hugo.

Note: The Hugo Learn theme is an open source project and not maintained by AWS. Every attempt was made to standardize this workshop content to run with the Hugo Learn theme at the time of publication.