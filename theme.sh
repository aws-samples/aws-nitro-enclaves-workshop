# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

#This script will add a git submodule for the open source Hugo learn theme.
[ -d workshop/themes ] || mkdir workshop/themes
cd workshop/themes
git submodule add https://github.com/matcornic/hugo-theme-learn
echo "Hugo Learn theme added as a git submodule at /workshop/themes/hugo-theme-learn."
cd ../../

#update workshop/config.toml to use hugo-theme-learn
sed -i '' 's/^theme.*/theme = \"hugo-theme-learn\"/' workshop/config.toml
echo "Updated config.toml to use hugo-theme-learn."