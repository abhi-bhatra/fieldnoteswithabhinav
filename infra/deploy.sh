#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Field Notes With Abhinav — deploy Azure OpenAI + push secrets to GitHub
# Usage: BEEHIIV_API_KEY=xxx BEEHIIV_PUB_ID=xxx ./infra/deploy.sh
# ---------------------------------------------------------------------------
set -euo pipefail

RESOURCE_GROUP="${RESOURCE_GROUP:-fieldnotes-rg}"
LOCATION="${LOCATION:-eastus}"
GITHUB_REPO="abhi-bhatra/fieldnoteswithabhinav"

: "${BEEHIIV_API_KEY:?Need BEEHIIV_API_KEY}"
: "${BEEHIIV_PUB_ID:?Need BEEHIIV_PUB_ID}"

echo "==> Checking Azure login"
az account show --output table

echo "==> Creating resource group: $RESOURCE_GROUP"
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output table

echo "==> Deploying Azure OpenAI"
az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file "$(dirname "$0")/main.bicep" \
  --parameters location="$LOCATION" \
  --output table

echo "==> Fetching OpenAI credentials"
OPENAI_ENDPOINT=$(az deployment group show \
  --resource-group "$RESOURCE_GROUP" \
  --name main \
  --query "properties.outputs.endpoint.value" \
  --output tsv)

OPENAI_KEY=$(az deployment group show \
  --resource-group "$RESOURCE_GROUP" \
  --name main \
  --query "properties.outputs.key.value" \
  --output tsv)

echo "==> Pushing secrets to GitHub ($GITHUB_REPO)"
gh secret set AZURE_OPENAI_ENDPOINT  --body "$OPENAI_ENDPOINT" --repo "$GITHUB_REPO"
gh secret set AZURE_OPENAI_API_KEY   --body "$OPENAI_KEY"      --repo "$GITHUB_REPO"
gh secret set BEEHIIV_API_KEY        --body "$BEEHIIV_API_KEY" --repo "$GITHUB_REPO"
gh secret set BEEHIIV_PUBLICATION_ID --body "$BEEHIIV_PUB_ID"  --repo "$GITHUB_REPO"

echo ""
echo "All done."
echo "Newsletter runs every Monday at 06:00 UTC via GitHub Actions."
echo "Monitor at: https://github.com/$GITHUB_REPO/actions"
