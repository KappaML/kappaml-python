[![PyPI version](https://img.shields.io/pypi/v/kappaml)](https://pypi.org/project/kappaml)
[![PyPI downloads](https://img.shields.io/pypi/dm/kappaml)](https://pypi.org/project/kappaml/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# KappaML Python Client

Python client to interact with the [KappaML](https://kappaml.com) platform 🐍

This SDK provides a simple interface for creating, training, and managing online machine learning models.

Platform: https://kappaml.com
API Keys: https://app.kappaml.com/api-keys
API Documentation: https://api.kappaml.com/docs
OpenAPI Schema: https://api.kappaml.com/openapi.json

## Installation

```bash
pip install kappaml
```

## Quick Start

```python
import asyncio
from kappaml import KappaML

async def main():
    # Initialize client with your API key
    async with KappaML(api_key="your_api_key") as client:
        # Create and deploy a model
        model_id = await client.create_model("my-model", "regression")
        
        # Make predictions
        predictions = await client.predict(
            model_id, 
            {"feature1": 1, "feature2": 2}
        )
        
        # Get model metrics
        metrics = await client.get_metrics(model_id)
        
        print(f"Predictions: {predictions}")
        print(f"Model metrics: {metrics}")

# Run the async function
asyncio.run(main())
```

## Authentication

The SDK requires an API key for authentication. You can provide it in two ways:

1. Directly in the constructor:
```python
client = KappaML(api_key="your_api_key")
```

2. Through environment variable:
```bash
export KAPPAML_API_KEY="your_api_key"
```
```python
client = KappaML()  # Will use KAPPAML_API_KEY env variable
```

## API Reference

### KappaML Class

#### `async with KappaML(api_key: Optional[str] = None) as client:`
Initialize a new KappaML client. Using it as an async context manager ensures proper cleanup of resources.

#### `async create_model(name: str, ml_type: str, wait_for_deployment: bool = True, timeout: int = 60) -> str`
Create a new model on the KappaML platform.
- `name`: Name of the model
- `ml_type`: Type of ML task ('regression' or 'classification')
- `wait_for_deployment`: Whether to wait for model deployment to complete
- `timeout`: Maximum time to wait for deployment in seconds
Returns the model ID.

#### `async predict(model_id: str, features: Dict[str, Any]) -> Dict[str, Any]`
Make predictions using a deployed model.
- `model_id`: The model ID
- `features`: Dictionary of feature names and values
Returns the model's predictions.

#### `async learn(model_id: str, features: Dict[str, Any], target: Union[float, int, str]) -> Dict[str, Any]`
Train the model with a new data point.
- `model_id`: The model ID
- `features`: Dictionary of feature names and values
- `target`: The target value to learn from
Returns the learning response.

#### `async get_metrics(model_id: str) -> Dict[str, Any]`
Get current metrics for a model.
- `model_id`: The model ID
Returns the model metrics.

#### `async delete_model(model_id: str) -> None`
Delete a model.
- `model_id`: The model ID to delete

## Error Handling

The SDK provides specific exceptions for different error cases:

- `KappaMLError`: Base exception for SDK errors
- `ModelNotFoundError`: Raised when a model is not found
- `ModelDeploymentError`: Raised when model deployment fails

Example:
```python
from kappaml import KappaML, ModelNotFoundError

async def main():
    async with KappaML() as client:
        try:
            metrics = await client.get_metrics("non_existent_model")
        except ModelNotFoundError:
            print("Model not found!")
```

## Requirements

- Python 3.10+

## License

MIT License

