# backend/poseEstimation/visualizations.py
import plotly.graph_objects as go

class Visualizations:
    def __init__(self):
        pass

# Todo: Plotten mehrerer Listen in einem Plot
    def plot_angle_plotly(self, angle_list, title="Kniewinkel (live)"):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=angle_list,
            mode='lines+markers',
            marker=dict(
                color=angle_list,
                colorscale='Viridis',
                size=6,
                colorbar=dict(title='Winkel (°)')
            ),
            line=dict(color='royalblue', width=2),
            name='Kniewinkel'
        ))
        fig.update_layout(
            title=title,
            xaxis_title="Frame",
            yaxis_title="Winkel (°)",
            yaxis=dict(range=[0, 180]),
            template="plotly_white"
        )
        return fig
