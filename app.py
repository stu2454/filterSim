from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

# Load dataset (ensure this matches your file name)
df = pd.read_excel("dummyData-all.xlsx")

# Define benchmark for filtering (using median as an example benchmark)
benchmark = df["PmtAmt"].median()

def apply_benchmark_filtering(data):
    """Applies benchmark-based filtering (10%-180% of benchmark)."""
    lower_bound = 0.1 * benchmark
    upper_bound = 1.8 * benchmark
    return data[(data['PmtAmt'] >= lower_bound) & (data['PmtAmt'] <= upper_bound)]

def apply_percentile_filtering(data, lower_percentile, upper_percentile):
    """Applies percentile-based filtering (customizable percentiles)."""
    lower_bound, upper_bound = np.percentile(data['PmtAmt'], [lower_percentile, upper_percentile])
    return data[(data['PmtAmt'] >= lower_bound) & (data['PmtAmt'] <= upper_bound)]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/filter', methods=['POST'])
def filter_data():
    method = request.json.get('method')
    lower_percentile = int(request.json.get('lower_percentile', 10))
    upper_percentile = int(request.json.get('upper_percentile', 85))
    
    if method == "benchmark":
        filtered_data = apply_benchmark_filtering(df)
    elif method == "percentile":
        filtered_data = apply_percentile_filtering(df, lower_percentile, upper_percentile)
    else:
        return jsonify({"error": "Invalid filtering method."}), 400

    # Create histogram for visualization
    fig = px.histogram(filtered_data, x="PmtAmt", nbins=50, title=f"Filtered Distribution ({method.capitalize()} Approach)")
    graph_html = pio.to_html(fig, full_html=False)
    
    return jsonify({"graph": graph_html, "count": len(filtered_data)})

@app.route('/compare', methods=['POST'])
def compare_filters():
    lower_percentile = int(request.json.get('lower_percentile', 10))
    upper_percentile = int(request.json.get('upper_percentile', 85))
    
    benchmark_filtered = apply_benchmark_filtering(df)
    percentile_filtered = apply_percentile_filtering(df, lower_percentile, upper_percentile)
    
    # Create separate histograms for unfiltered, benchmark-filtered, and percentile-filtered datasets
    fig_original = px.histogram(df, x="PmtAmt", nbins=50, title="Unfiltered Distribution")
    fig_benchmark = px.histogram(benchmark_filtered, x="PmtAmt", nbins=50, title="Benchmark-Based Filtering (10%-180%)")
    fig_percentile = px.histogram(percentile_filtered, x="PmtAmt", nbins=50, title=f"Percentile-Based Filtering ({lower_percentile}-{upper_percentile})")
    
    graph_html_original = pio.to_html(fig_original, full_html=False)
    graph_html_benchmark = pio.to_html(fig_benchmark, full_html=False)
    graph_html_percentile = pio.to_html(fig_percentile, full_html=False)
    
    return jsonify({
        "graph_original": graph_html_original,
        "graph_benchmark": graph_html_benchmark,
        "graph_percentile": graph_html_percentile,
        "benchmark_count": len(benchmark_filtered),
        "percentile_count": len(percentile_filtered),
        "lower_percentile": lower_percentile,
        "upper_percentile": upper_percentile
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

