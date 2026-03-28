# CLI Reference for AKS

```bash
# List AKS clusters
az aks list --output table

# Show cluster details
az aks show --name <cluster-name> --resource-group <resource-group>

# Get available Kubernetes versions
az aks get-versions --location <location> --output table

# Create AKS Automatic cluster
az aks create --name <cluster-name> --resource-group <resource-group> --sku automatic \
  --network-plugin azure --network-plugin-mode overlay \
  --enable-oidc-issuer --enable-workload-identity

# Create AKS Standard cluster
az aks create --name <cluster-name> --resource-group <resource-group> \
  --node-count 3 --zones 1 2 3 \
  --network-plugin azure --network-plugin-mode overlay \
  --enable-cluster-autoscaler --min-count 1 --max-count 10 \
  --enable-oidc-issuer --enable-workload-identity

# Get credentials
az aks get-credentials --name <cluster-name> --resource-group <resource-group>

# List node pools
az aks nodepool list --cluster-name <cluster-name> --resource-group <resource-group> --output table

# Enable monitoring
az aks enable-addons --name <cluster-name> --resource-group <resource-group> \
  --addons monitoring --workspace-resource-id <workspace-resource-id>
```
