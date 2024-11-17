from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Read the CSV file named "output-file1.csv"
df = pd.read_csv("output-file1.csv")

# Default threshold value
initial_threshold = 0

@app.route('/')
def index():
    return render_template('ThresholdInputForm.html')

@app.route('/dashboard')
def generate_dashboard():
    global initial_threshold

    # Get the threshold value from the query parameters
    initial_threshold = int(request.args.get('threshold', initial_threshold))

    # Count the number of red-colored values for each machine ID
    red_counts = df[df['rul'] < initial_threshold]['machine_id'].value_counts()

    # Create an HTML table with Bootstrap styling for "rul" column and display the threshold value
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{
                padding: 20px;
                background-color: #f8f9fa; /* Light gray background color */
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 20px;
            }}
            th, td {{
                border: 1px solid #dee2e6;
                padding: 8px;
                text-align: left;
            }}
            .rul-red {{
                background-color: #dc3545;
                color: white;
            }}
            .rul-green {{
                background-color: #28a745;
                color: white;
            }}
            #threshold-text {{
                font-size: 24px;
                color: blue;
            }}
            canvas {{
                margin-top: 0px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="mt-4">Machine Outage Alert Dashboard</h1>
            <div class="form-group">
                
            </div>
            <p id="threshold-text">Threshold Selected: <span id="thresholdValue">{initial_threshold}</span></p>
            
            <div class="row">
                <div class="col-md-6">
                    <canvas id="redChart" width="350" height="250"></canvas>
                </div>
                <div class="col-md-6">
                    <canvas id="pieChart" width="350" height="250"></canvas>
                </div>
            </div>

            <table class="table table-striped table-bordered">
                <thead class="thead-dark">
                    <tr>
                        <th>machine_id</th>
                        <th>Timestamp</th>
                        <th>Date</th>
                        <th>cycle</th>
                        <th>rul</th>
                    </tr>
                </thead>
                <tbody id="dataTableBody">
                    {df.apply(lambda row: f"<tr><td>{row['machine_id']}</td><td>{row['Timestamp']}</td><td>{row['Date']}</td><td>{row['cycle']}</td><td class='{'rul-green' if row['rul'] >= initial_threshold else 'rul-red'}'>{row['rul']}</td></tr>", axis=1).str.cat()}
                </tbody>
            </table>
        </div>

        <script>
            function updateThreshold() {{
                var newThreshold = document.getElementById("thresholdInput").value;
                document.getElementById("thresholdValue").innerText = newThreshold;
                updateTableColors(newThreshold);
                updateCharts();
            }}

            function updateTableColors(threshold) {{
                var rows = document.querySelectorAll("#dataTableBody tr");
                rows.forEach(function(row) {{
                    var rulCell = row.querySelector(".rul-green, .rul-red");
                    var rulValue = parseInt(rulCell.innerText);
                    if (rulValue >= threshold) {{
                        rulCell.classList.remove("rul-red");
                        rulCell.classList.add("rul-green");
                    }} else {{
                        rulCell.classList.remove("rul-green");
                        rulCell.classList.add("rul-red");
                    }}
                }});
            }}

            function updateCharts() {{
                updateRedChart();
                updatePieChart();
            }}

            function updateRedChart() {{
                var redCounts = {red_counts.to_dict()};
                var labels = Object.keys(redCounts);
                var data = Object.values(redCounts);

                var ctx = document.getElementById("redChart").getContext('2d');
                var myChart = new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: labels,
                        datasets: [{{
                            label: 'No of Outages per Machine ID',
                            data: data,
                            backgroundColor: 'rgba(220, 53, 69, 0.5)',
                            borderColor: 'rgba(220, 53, 69, 1)',
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }},
                        maintainAspectRatio: false,
                        responsive: true
                    }}
                }});
            }}

            function updatePieChart() {{
                var greenCount = {len(df[df['rul'] >= initial_threshold])};
                var redCount = {len(df[df['rul'] < initial_threshold])};

                var ctx = document.getElementById("pieChart").getContext('2d');
                // Set height and width directly on the canvas element
                ctx.canvas.height = 250;
                ctx.canvas.width = 350;
                var myChart = new Chart(ctx, {{
                    type: 'pie',
                    data: {{
                        labels: ['Available', 'Not Available'],
                        datasets: [{{
                            data: [greenCount, redCount],
                            backgroundColor: ['rgba(40, 167, 69, 0.5)', 'rgba(220, 53, 69, 0.5)'],
                            borderColor: ['rgba(40, 167, 69, 1)', 'rgba(220, 53, 69, 1)'],
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        maintainAspectRatio: false,
                        responsive: true
                    }}
                }});
            }}
            
            // Initial chart update
            updateCharts();
        </script>

        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    </body>
    </html>
    """

    return html_code

if __name__ == '__main__':
    app.run(debug=True)
