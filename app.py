from flask import Flask, request, Response, jsonify
import os
from prometheus_flask_exporter import PrometheusMetrics
# OpenTelemetry setup
os.environ["OTEL_PYTHON_FLASK_EXCLUDED_URLS"] = "healthz,metrics"  # set exclusions
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.propagate import set_global_textmap
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.propagators.cloud_trace_propagator import (
    CloudTraceFormatPropagator,
)
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
# spanner imports 
from google.cloud.spanner_dbapi.connection import connect

# set up tracing (and use 100% tracing ratio)
trace_sampling_ratio = 1.0 # modify if needed
sampler = TraceIdRatioBased(trace_sampling_ratio)
set_global_textmap(CloudTraceFormatPropagator())
tracer_provider = TracerProvider(sampler=sampler)
cloud_trace_exporter = CloudTraceSpanExporter()
tracer_provider.add_span_processor(
        # BatchSpanProcessor buffers spans and sends them in batches in a
        # background thread. The default parameters are sensible, but can be
        # tweaked to optimize your performance
        BatchSpanProcessor(cloud_trace_exporter)
    )
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# flask setup
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
metrics = PrometheusMetrics(app)  # enable Prom metrics
FlaskInstrumentor().instrument_app(app)

# spanner client setup
connection = connect("flask-spanner-hello-world", "flask-spanner-hello-world")
connection.autocommit = True

# HTTP healthcheck
@app.route('/healthz')  # healthcheck endpoint
@metrics.do_not_track()  # exclude from prom metrics
def i_am_healthy():
    return ('OK')

@app.route('/spanner-test')
def spanner_test():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Example")
    rows = cursor.fetchall()
    return (rows) # just get the first record

# default HTTP service
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    return ('OK')
    
if __name__ == '__main__':

    app.run(
            host='0.0.0.0', port=int(os.environ.get('PORT', 8080)),
            threaded=True)