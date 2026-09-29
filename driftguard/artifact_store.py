import os
import joblib
from urllib.parse import urlparse

class ArtifactStore:
    def exists(self, project_id: str, model_id: str, version: str) -> bool:
        raise NotImplementedError

    def load(self, project_id: str, model_id: str, version: str):
        raise NotImplementedError

    def save(self, obj, project_id: str, model_id: str, version: str):
        raise NotImplementedError

class LocalArtifactStore(ArtifactStore):
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def _get_path(self, project_id: str, model_id: str, version: str) -> str:
        return os.path.join(self.root_dir, str(project_id), str(model_id), f"version_{version}.pkl")

    def exists(self, project_id: str, model_id: str, version: str) -> bool:
        return os.path.exists(self._get_path(project_id, model_id, version))

    def load(self, project_id: str, model_id: str, version: str):
        return joblib.load(self._get_path(project_id, model_id, version))

    def save(self, obj, project_id: str, model_id: str, version: str):
        path = self._get_path(project_id, model_id, version)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(obj, path)

class S3ArtifactStore(ArtifactStore):
    def __init__(self, s3_uri: str):
        parsed = urlparse(s3_uri)
        self.bucket = parsed.netloc
        self.prefix = parsed.path.lstrip('/')
        import boto3
        # Use default credentials from IAM role or environment
        self.s3_client = boto3.client('s3')

    def _get_key(self, project_id: str, model_id: str, version: str) -> str:
        return f"{self.prefix}/{project_id}/{model_id}/version_{version}.pkl".strip('/')

    def exists(self, project_id: str, model_id: str, version: str) -> bool:
        key = self._get_key(project_id, model_id, version)
        import botocore
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=key)
            return True
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    def load(self, project_id: str, model_id: str, version: str):
        key = self._get_key(project_id, model_id, version)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp:
            tmp_path = tmp.name
        try:
            self.s3_client.download_file(self.bucket, key, tmp_path)
            return joblib.load(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def save(self, obj, project_id: str, model_id: str, version: str):
        key = self._get_key(project_id, model_id, version)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp:
            tmp_path = tmp.name
        try:
            joblib.dump(obj, tmp_path)
            self.s3_client.upload_file(tmp_path, self.bucket, key)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

def get_artifact_store(root_uri: str) -> ArtifactStore:
    if root_uri.startswith("s3://"):
        return S3ArtifactStore(root_uri)
    return LocalArtifactStore(root_uri)
