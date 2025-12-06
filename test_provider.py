from anyfunction import setProvider, getAvailableModels

provider = {
    "url": "https://api.mistral.ai/v1",
    "key": "Og84c9hxjTuh0OgfQtnv6uw1e6xIeLqU",
    "model": "mistral-large-latest",
}

setProvider(provider)

models = getAvailableModels()

for model in models:
    print(model)