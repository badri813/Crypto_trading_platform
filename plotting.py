import pandas as pd
import plotly.express as px

df = pd.read_csv("rsi.csv")

fig = px.scatter(
    df,
    x="Date",
    y="RSI",
    color="RSI",
    hover_name="Ticker",
    color_continuous_scale="RdYlGn_r",
    title="RSI Heatmap Over Time",
    hover_data={"RSI":":.2f","Date":True,"Ticker":True},
    template="plotly_dark"
)

fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")

fig.update_yaxes(range=[0, 100], title="RSI")
fig.update_xaxes(title="Date")

# Save chart as HTML template
fig.write_html("templates/rsi_chart.html", full_html=True)
print("Chart saved as templates/rsi_chart.html")
