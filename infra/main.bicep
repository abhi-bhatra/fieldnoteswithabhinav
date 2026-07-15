@description('Azure region — eastus has Standard SKU for gpt-5.1')
param location string = 'eastus'

// ---------------------------------------------------------------------------
// Azure OpenAI — only Azure resource we need
// ---------------------------------------------------------------------------
resource openAi 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: 'fieldnotes-openai'
  location: location
  kind: 'OpenAI'
  sku: { name: 'S0' }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openAi
  name: 'gpt-5-1'
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-5.1'
      version: '2025-11-13'
    }
  }
  sku: {
    name: 'Standard'
    capacity: 10
  }
}

output endpoint string = openAi.properties.endpoint
output key string = openAi.listKeys().key1
