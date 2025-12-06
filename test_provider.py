from anyfunction import setProvider, getAvailableModels

provider = {
    "url": "https://api.mistral.ai/v1",
    "key": "APi klic pro pristup ke sluzbam Mistral",
    "model": "mistral-large-latest",
}

setProvider(provider)

models = getAvailableModels()

for model in models:
    print(model)

