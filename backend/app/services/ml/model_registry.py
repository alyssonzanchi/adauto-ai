"""
Model Registry - Manage ML model versions and metadata
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json
import joblib


class ModelRegistry:
    """
    Registry for managing ML model versions and metadata.

    Handles:
    - Model versioning
    - Model metadata storage
    - Model loading/saving
    - Model listing and discovery
    """

    def __init__(self, registry_path: str = "backend/app/ml/models"):
        """
        Initialize ModelRegistry.

        Args:
            registry_path: Path to models directory
        """
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)

        # Metadata index file
        self.index_file = self.registry_path / "model_index.json"
        self._load_index()

    def _load_index(self) -> None:
        """Load model index from disk"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {}

    def _save_index(self) -> None:
        """Save model index to disk"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def register_model(
        self,
        model_name: str,
        version: str,
        model: Any,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Register a new model version.

        Args:
            model_name: Name of the model
            version: Version string (e.g., "1.0.0")
            model: Trained model object
            metadata: Model metadata

        Returns:
            True if successful
        """
        try:
            # Create model directory
            model_dir = self.registry_path / model_name
            model_dir.mkdir(parents=True, exist_ok=True)

            # Model file path
            model_file = model_dir / f"{model_name}_{version}.pkl"

            # Add metadata
            metadata.update({
                "model_name": model_name,
                "version": version,
                "registered_at": datetime.now().isoformat(),
                "model_file": str(model_file)
            })

            # Save model
            model_data = {
                "model": model,
                "metadata": metadata
            }

            joblib.dump(model_data, model_file)

            # Update index
            if model_name not in self.index:
                self.index[model_name] = {}

            self.index[model_name][version] = {
                "registered_at": metadata["registered_at"],
                "model_file": str(model_file),
                "metadata": metadata
            }

            self._save_index()

            return True

        except Exception as e:
            print(f"Error registering model: {e}")
            return False

    def load_model(
        self,
        model_name: str,
        version: Optional[str] = None
    ) -> Optional[Any]:
        """
        Load a model from registry.

        Args:
            model_name: Name of the model
            version: Optional version (defaults to latest)

        Returns:
            Model object or None if not found
        """
        try:
            # Get version
            if version is None:
                version = self.get_latest_version(model_name)

            if version is None:
                raise ValueError(f"No versions found for model: {model_name}")

            # Get model file path from index
            if model_name not in self.index or version not in self.index[model_name]:
                raise FileNotFoundError(f"Model {model_name}:{version} not found in index")

            model_file = self.index[model_name][version]["model_file"]

            # Load model
            model_data = joblib.load(model_file)
            return model_data

        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def get_model_info(
        self,
        model_name: str,
        version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get model metadata.

        Args:
            model_name: Name of the model
            version: Optional version (defaults to latest)

        Returns:
            Model metadata or None if not found
        """
        try:
            # Get version
            if version is None:
                version = self.get_latest_version(model_name)

            if version is None:
                return None

            # Get metadata from index
            if model_name not in self.index or version not in self.index[model_name]:
                return None

            return self.index[model_name][version]["metadata"]

        except Exception as e:
            print(f"Error getting model info: {e}")
            return None

    def list_models(self) -> List[str]:
        """
        List all registered model names.

        Returns:
            List of model names
        """
        return list(self.index.keys())

    def list_versions(self, model_name: str) -> List[str]:
        """
        List all versions of a model.

        Args:
            model_name: Name of the model

        Returns:
            List of version strings
        """
        if model_name not in self.index:
            return []

        versions = list(self.index[model_name].keys())
        # Sort by version (semantic versioning)
        versions.sort(key=lambda v: [int(i) for i in v.split('.')])
        return versions

    def get_latest_version(self, model_name: str) -> Optional[str]:
        """
        Get latest version of a model.

        Args:
            model_name: Name of the model

        Returns:
            Latest version string or None if not found
        """
        versions = self.list_versions(model_name)
        if not versions:
            return None
        return versions[-1]  # Last version after sorting

    def delete_model(
        self,
        model_name: str,
        version: str
    ) -> bool:
        """
        Delete a model version.

        Args:
            model_name: Name of the model
            version: Version to delete

        Returns:
            True if successful
        """
        try:
            # Get model file
            if model_name not in self.index or version not in self.index[model_name]:
                raise FileNotFoundError(f"Model {model_name}:{version} not found")

            model_file = Path(self.index[model_name][version]["model_file"])

            # Delete file
            if model_file.exists():
                model_file.unlink()

            # Update index
            del self.index[model_name][version]

            # Clean up model name if no versions left
            if not self.index[model_name]:
                del self.index[model_name]

            self._save_index()

            return True

        except Exception as e:
            print(f"Error deleting model: {e}")
            return False

    def get_registry_info(self) -> Dict[str, Any]:
        """
        Get registry information.

        Returns:
            Registry summary
        """
        total_models = len(self.index)
        total_versions = sum(len(versions) for versions in self.index.values())

        return {
            "registry_path": str(self.registry_path),
            "total_models": total_models,
            "total_versions": total_versions,
            "models": {
                name: {
                    "versions": self.list_versions(name),
                    "latest": self.get_latest_version(name)
                }
                for name in self.index.keys()
            }
        }
