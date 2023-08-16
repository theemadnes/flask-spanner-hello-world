# flask-spanner-hello-world
a basic  `get` API against a Spanner instance using Flask, instrumented with OTEL tracing

### setting up Spanner & GKE

```
gcloud config set project spanner-reporter-01
gcloud config set compute/region us-central1

# create GKE Autopilot cluster
gcloud container --project spanner-reporter-01 clusters create-auto flask-spanner-hello-world --region us-central1 --release-channel rapid

# just setting up a demo instance called `flask-spanner-hello-world` in the same region as the GKE cluster `us-central1`
gcloud spanner instances create flask-spanner-hello-world --config=regional-us-central1 --description="Flask Spanner Hello World" --nodes=1
# create table
gcloud spanner databases create flask-spanner-hello-world \
  --instance=flask-spanner-hello-world \
  --ddl="CREATE TABLE Example (
    id INT64 NOT NULL,
    message STRING(1024) NOT NULL
  ) PRIMARY KEY (id)"

# create record
gcloud spanner databases execute-sql flask-spanner-hello-world --instance=flask-spanner-hello-world \
    --sql="INSERT Example (id, message) VALUES (1, 'Hello World')"


```