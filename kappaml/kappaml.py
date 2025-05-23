import os
import time
from typing import Dict, Optional, Union, Any
import httpx
import asyncio


class KappaMLError(Exception):
    """Base exception for KappaML SDK errors."""
    pass


class ModelNotFoundError(KappaMLError):
    """Raised when a model is not found."""
    pass


class ModelDeploymentError(KappaMLError):
    """Raised when model deployment fails."""
    pass


class KappaML:
    """KappaML Client SDK for interacting with the KappaML platform.
    
    Example:
        ```python
        client = KappaML(api_key="your_api_key")
        
        # Create and deploy a model
        model_id = await client.create_model(
            "my-model", 
            "regression"
        )
        
        # Make predictions
        predictions = await client.predict(
            model_id, 
            {"feature1": 1, "feature2": 2}
        )
        
        # Get model metrics
        metrics = await client.get_metrics(model_id)
        ```
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the KappaML client.
        
        Args:
            api_key: Your KappaML API key. If not provided, will look for 
                KAPPAML_API_KEY env variable.
        """
        self.api_key = api_key or os.getenv("KAPPAML_API_KEY")
        if not self.api_key:
            msg = "API key must be provided or set as KAPPAML_API_KEY env var"
            raise KappaMLError(msg)
            
        self.base_url = "https://api.kappaml.com/v1"
        self.client = httpx.AsyncClient(
            headers={"X-API-Key": self.api_key},
            timeout=30.0
        )
    
    async def create_model(
        self, 
        name: str, 
        ml_type: str,
        wait_for_deployment: bool = True,
        timeout: int = 60
    ) -> str:
        """Create a new model on KappaML.
        
        Args:
            name: Name of the model
            ml_type: Type of ML task ('regression' or 'classification')
            wait_for_deployment: Whether to wait for model deployment to 
                complete
            timeout: Maximum time to wait for deployment in seconds
            
        Returns:
            str: The model ID
            
        Raises:
            ModelDeploymentError: If model deployment fails or times out
        """
        model_data = {
            "name": name,
            "ml_type": ml_type
        }
        
        response = await self.client.post(
            f"{self.base_url}/models", 
            json=model_data
        )
        if response.status_code != 201:
            raise KappaMLError(f"Failed to create model: {response.text}")
            
        model_id = response.json()["id"]
        
        if wait_for_deployment:
            await self._wait_for_deployment(model_id, timeout)
            
        return model_id
    
    async def _wait_for_deployment(self, model_id: str, timeout: int) -> None:
        """Wait for model deployment to complete."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = await self.get_model_status(model_id)
            if status == "Deployed":
                return
            elif status == "Failed":
                raise ModelDeploymentError(f"Model {model_id} deployment failed")
            await asyncio.sleep(5)
            
        raise ModelDeploymentError(f"Model {model_id} deployment timed out")
    
    async def get_model_status(self, model_id: str) -> str:
        """Get the current status of a model.
        
        Args:
            model_id: The model ID
            
        Returns:
            str: Model status
        """
        response = await self.client.get(f"{self.base_url}/models/{model_id}")
        if response.status_code == 404:
            raise ModelNotFoundError(f"Model {model_id} not found")
        elif response.status_code != 200:
            raise KappaMLError(f"Failed to get model status: {response.text}")
            
        return response.json()["status"]
    
    async def learn(
        self, 
        model_id: str, 
        features: Dict[str, Any], 
        target: Union[float, int, str]
    ) -> Dict[str, Any]:
        """Learn from a new data point.
        
        Args:
            model_id: The model ID
            features: Dictionary of feature names and values
            target: The target value to learn from
            
        Returns:
            dict: Response from the learning API
        """
        data = {
            "features": features,
            "target": target
        }
        
        url = f"{self.base_url}/models/{model_id}/learn"
        response = await self.client.post(url, json=data)
        
        if response.status_code == 404:
            raise ModelNotFoundError(f"Model {model_id} not found")
        elif response.status_code != 200:
            raise KappaMLError(f"Failed to learn: {response.text}")
            
        return response.json()
    
    async def predict(
        self, 
        model_id: str, 
        features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make predictions using a model.
        
        Args:
            model_id: The model ID
            features: Dictionary of feature names and values
            
        Returns:
            dict: Model predictions
        """
        url = f"{self.base_url}/models/{model_id}/predict"
        response = await self.client.post(url, json={"features": features})
        
        if response.status_code == 404:
            raise ModelNotFoundError(f"Model {model_id} not found")
        elif response.status_code != 200:
            raise KappaMLError(f"Failed to get prediction: {response.text}")
            
        return response.json()["prediction"]
    
    async def get_metrics(self, model_id: str) -> Dict[str, Any]:
        """Get current metrics for a model.
        
        Args:
            model_id: The model ID
            
        Returns:
            dict: Model metrics
        """
        url = f"{self.base_url}/models/{model_id}/metrics"
        response = await self.client.get(url)
        
        if response.status_code == 404:
            raise ModelNotFoundError(f"Model {model_id} not found")
        elif response.status_code != 200:
            raise KappaMLError(f"Failed to get metrics: {response.text}")
            
        return response.json()
    
    async def delete_model(self, model_id: str) -> None:
        """Delete a model.
        
        Args:
            model_id: The model ID to delete
        """
        response = await self.client.delete(f"{self.base_url}/models/{model_id}")
        if response.status_code == 404:
            raise ModelNotFoundError(f"Model {model_id} not found")
        elif response.status_code != 200:
            raise KappaMLError(f"Failed to delete model: {response.text}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose() 