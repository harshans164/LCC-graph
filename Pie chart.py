import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
import pandas as pd

FILE_PATH = r"Book 4(Sheet1)1.csv"
df = pd.read_csv(FILE_PATH)

list_final = [
    "Road user cost",
    "Time cost estimate",
    "Embodied carbon emissions",
    "Initial construction cost",
    "Additional CO2 e costs due to rerouting",
    "Periodic Maintenance costs",
    "Periodic maintenance carbon emissions",
    "Annual routine inspection costs",
    "Repair and rehabilitation costs",
    "Demolition and deconstruction costs"
]

# Extract values from DataFrame
values_dict = {}
for item in list_final:
    count = 0
    for _, row in df.iterrows():
        if item in list(row):
            if count == 0:
                temp_row = list(row)
                values_dict[item] = temp_row[temp_row.index(item) + 1]
                count += 1

cost_list = [float(items) for items in values_dict.values()]
cost_list = [items / 100000 for items in cost_list]
percentage_list = [round((item / sum(cost_list)) * 100, 4) for item in cost_list]

# Clean list_final labels
for i in list_final:
    if " - " in i:
        temp = i[4:]
        list_final[list_final.index(i)] = temp.strip()
    elif "\n" in i:
        list_final[list_final.index(i)] = i.replace("\n", "").strip()

# Create modified percentages (add 1.5% to each, then normalize to 100%)
modified_percentages = [p + 1.5 for p in percentage_list]
total = sum(modified_percentages)
normalized_percentages = [round(p * 100 / total, 4) for p in modified_percentages]

# Combine for Highcharts
data_entries = [
    {"name": label, "y": modified_p, "original_y": original_p, "cost": float(cost)}
    for label, modified_p, original_p, cost in zip(list_final, normalized_percentages, percentage_list, cost_list)
]

data_js = "[" + ",".join(
    f'{{ name: "{entry["name"]}", y: {entry["y"]}, original_y: {entry["original_y"]}, cost: {entry["cost"]} }}'
    for entry in data_entries
) + "]"

colors_js = [
    "#ff9900", "#660066", "#cc0000", "#996633", "#660033",
    "#999966", "#3366cc", "#669999", "#ffff99", "#990000"
]
colors_js = "[" + ",".join(f'"{color}"' for color in colors_js) + "]"

html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Pie Chart</title>
    <style>
        body {
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f9f9f9;
        }
        #container {
            width: 960px;
            height: 500px;
        }
    </style>
</head>
<body>
    <div id="container"></div>
    <script src="https://code.highcharts.com/highcharts.js"></script>
    <script>
        const data = """ + data_js + """;
        const colors = """ + colors_js + """;

        Highcharts.chart('container', {
            chart: {
                type: 'pie',
                animation: {
                    duration: 450
                },
                events: {
                    load: function() {
                        const chart = this;
                        chart.series[0].data.forEach((point, i) => {
                            point.originalColor = point.color;
                        });
                    }
                }
            },
            title: { text: null },
            colors: colors,
            plotOptions: {
                pie: {
                    dataLabels: {
                        enabled: true,
                        distance: 50,
                        connectorWidth: 1,
                        connectorColor: '#000',
                        formatter: function () {
                            const isLeft = this.point.plotX < 0;
                            const label = this.point.name + ": " + this.point.original_y.toFixed(5) + "% ;" + this.point.cost.toLocaleString(undefined, { minimumFractionDigits: 5 }) + " Lakhs";
                            return isLeft ? "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + label : label;
                        },
                        style: {
                            fontSize: '12px',
                            fontWeight: 'normal',
                            textOutline: 'none',
                        },
                        connectorPadding: 5,
                        softConnector: true
                    },
                    showInLegend: true,
                    animation: { duration: 1100 },
                    borderWidth: 1,
                    borderColor: '#fff',
                    point: {
                        events: {
                            mouseOver: function () {
                                const chart = this.series.chart;
                                chart.series[0].data.forEach(point => {
                                    if (point !== this) {
                                        point.update({ color: '#e0e0e0' }, false);
                                    } else {
                                        point.update({ sliced: true, slicedOffset: 10 }, false);
                                    }
                                });
                                chart.redraw();
                            },
                            mouseOut: function () {
                                const chart = this.series.chart;
                                chart.series[0].data.forEach(point => {
                                    point.update({
                                        color: point.originalColor,
                                        sliced: false,
                                        slicedOffset: 0
                                    }, false);
                                });
                                chart.redraw();
                            }
                        }
                    },
                    states: {
                        hover: {
                            halo: { size: 0 },
                            brightness: 0
                        }
                    }
                }
            },
            legend: {
                align: 'right',
                verticalAlign: 'top',
                layout: 'vertical',
                itemStyle: { fontSize: '12px' },
                itemMarginTop: 5,
                itemMarginBottom: 5,
                maxHeight: 400,
                padding: 10,
                backgroundColor: '#fff',
                borderWidth: 1,
                borderColor: '#ddd',
                borderRadius: 4,
                shadow: true
            },
            tooltip: {
                pointFormat: '{point.name}: <b>{point.original_y:.5f}% ({point.cost:,.5f})</b>',
                backgroundColor: '#f4f4f4',
                borderColor: '#ddd',
                borderRadius: 4,
                borderWidth: 1,
                style: { fontSize: '12px' }
            },
            series: [{
                name: 'Life Cycle Cost',
                data: data,
                allowPointSelect: true
            }],
            responsive: {
                rules: [{
                    condition: { maxWidth: 960 },
                    chartOptions: {
                        legend: {
                            align: 'center',
                            verticalAlign: 'bottom',
                            layout: 'horizontal'
                        }
                    }
                }]
            }
        });
    </script>
</body>
</html>
"""

# Show in Qt UI
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pie Chart")
        self.setGeometry(100, 100, 1000, 700)

        view = QWebEngineView()
        view.setHtml(html_content)
        self.setCentralWidget(view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
