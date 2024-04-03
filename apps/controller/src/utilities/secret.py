import base64

from kubernetes import client, config
from kubernetes.client.rest import ApiException


def get_secret(name, namespace='video'):
    """
    Fetches the username and password from a Kubernetes secret.
    """
    v1 = client.CoreV1Api()
    try:
        secret = v1.read_namespaced_secret(name, namespace)
        username = base64.b64decode(secret.data['username']).decode('utf-8')
        password = base64.b64decode(secret.data['password']).decode('utf-8')
        return username, password
    except ApiException as e:
        if e.status ==  404:
            # Secret not found, return None for username and password
            return None, None
        else:
            # Unexpected error occurred
            raise

if __name__ == "__main__":
    """
    HIK Vision cameras will have a secret in AWS which gets applied to the global cluster for the cameras username and password.
    This is due to the limitaiton that HIK Vision prevent anonymous viewing of their camera feeds.
    Create the secret with the respsective username and password fields and then apply it to the cluster using the following command:


    aws secretsmanager get-secret-value --secret-id <your-arn-goes-here> --query SecretString --output text \
    > ~/.kube/test-hik.yaml \
    && kubectl apply -f ~/.kube/test-hik.yaml \
    && rm ~/.kube/test-hik.yaml
    """
    config.load_kube_config()
    print(get_secret('test-hik'))