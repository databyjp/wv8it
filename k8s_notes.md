## Get started

Update helm chart

```shell
helm repo update weaviate
```

Start a small cluster with Minikube:

```shell
minikube config set memory 2048
minikube start --nodes 3
```

Install Weaviate helm chart:

```shell
helm repo add weaviate https://weaviate.github.io/weaviate-helm
```

Get the default values:

```shell
helm show values weaviate/weaviate > values.yaml
```

Edit the values.yaml file to your needs.

Install Weaviate:

```shell
kubectl create namespace weaviate
helm upgrade --install "weaviate" weaviate/weaviate --namespace "weaviate" --values ./values.yaml
```

Check the status:

```shell
kubectl get pods -n weaviate
```

Run a tunnel to access the Weaviate cluster:

```shell
minikube tunnel
```

Check the Weaviate root endpoint:

```shell
curl http://localhost:80/v1/meta | jq
```

### Running additional services

To forward additional ports, create them and add them through kubectl:

```shell
kubectl apply -f ollama-service.yaml
kubectl apply -f pprof-service.yaml
kubectl port-forward service/weaviate-ollama -n weaviate 11434:11434
```

Check memory usage

```shell
go tool pprof -top http://localhost:6060/debug/pprof/heap
```

Remove the service:

```shell
kubectl delete -f ollama-service.yaml
```
