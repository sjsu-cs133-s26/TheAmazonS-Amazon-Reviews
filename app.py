from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px

app = Dash(__name__)
app.title = "Amazon Book Reviews Dashboard"

# -----------------------------
# Data Loading
# -----------------------------
DATA_PATH = "Books_rating.csv"

df = pd.read_csv(DATA_PATH)

df = df.dropna(subset=["Title", "review/score"])
df["review/score"] = pd.to_numeric(df["review/score"], errors="coerce")
df = df.dropna(subset=["review/score"])

book_summary = (
    df.groupby("Title")
    .agg(
        review_count=("review/score", "count"),
        average_rating=("review/score", "mean")
    )
    .reset_index()
)

max_reviews = int(book_summary["review_count"].max())

# -----------------------------
# Layout
# -----------------------------
app.layout = html.Div(
    id="container",
    children=[
        html.Div(
            id="left-container",
            children=[
                html.H1("Amazon Book Reviews Dashboard"),
                html.P(
                    "Interactive dashboard for exploring book review engagement "
                    "and rating behavior."
                ),

                html.Label("Select review score:", className="dropdown-labels"),
                dcc.Dropdown(
                    id="score-dropdown",
                    options=[
                        {"label": f"{int(score)} Star", "value": score}
                        for score in sorted(df["review/score"].unique())
                    ],
                    value=sorted(df["review/score"].unique()),
                    multi=True,
                    clearable=False
                ),

                html.Label("Top N books:", className="other-labels"),
                dcc.Slider(
                    id="top-n-slider",
                    min=5,
                    max=30,
                    step=5,
                    value=10,
                    marks={i: str(i) for i in range(5, 31, 5)}
                ),

                html.Label("Minimum reviews per book:", className="other-labels"),
                dcc.Slider(
                    id="min-review-slider",
                    min=1,
                    max=min(max_reviews, 5000),
                    step=50,
                    value=100,
                    marks={
                        1: "1",
                        1000: "1K",
                        2500: "2.5K",
                        5000: "5K"
                    }
                ),

                html.Div(
                    id="summary-box",
                    children=[
                        html.H3("Dashboard Purpose"),
                        html.P(
                            "Use the filters to explore which books receive the "
                            "most reviews and how rating patterns change."
                        )
                    ]
                )
            ]
        ),

        html.Div(
            id="right-container",
            children=[
                html.Div(
                    id="kpi-row",
                    children=[
                        html.Div(id="total-reviews-card", className="kpi-card"),
                        html.Div(id="total-books-card", className="kpi-card"),
                        html.Div(id="avg-rating-card", className="kpi-card")
                    ]
                ),

                dcc.Graph(id="top-books-chart"),

dcc.Graph(id="rating-distribution-chart"),

dcc.Graph(id="popularity-rating-chart"),

html.Div(

    id="key-insight-box",

    children=[

        html.H3("Key Insight"),

        html.P(

            "Reader engagement is highly concentrated among a small number of books, "

            "and review scores are strongly skewed toward positive ratings, especially 5-star reviews."

        )

    ]

)
            ]
        )
    ]
)

# -----------------------------
# Callback
# -----------------------------
@app.callback(
    [
        Output("top-books-chart", "figure"),
        Output("rating-distribution-chart", "figure"),
        Output("popularity-rating-chart", "figure"),
        Output("total-reviews-card", "children"),
        Output("total-books-card", "children"),
        Output("avg-rating-card", "children"),
    ],
    [
        Input("score-dropdown", "value"),
        Input("top-n-slider", "value"),
        Input("min-review-slider", "value"),
    ]
)
def update_dashboard(selected_scores, top_n, min_reviews):
    if not selected_scores:
        selected_scores = sorted(df["review/score"].unique())

    filtered_df = df[df["review/score"].isin(selected_scores)]

    filtered_books = (
        filtered_df.groupby("Title")
        .agg(
            review_count=("review/score", "count"),
            average_rating=("review/score", "mean")
        )
        .reset_index()
    )

    filtered_books = filtered_books[filtered_books["review_count"] >= min_reviews]

    top_books = (
        filtered_books.sort_values("review_count", ascending=False)
        .head(top_n)
    )

    # Chart 1: Top books
    fig_top_books = px.bar(
        top_books,
        x="review_count",
        y="Title",
        orientation="h",
        title=f"Top {top_n} Most-Reviewed Books",
        labels={
            "review_count": "Number of Reviews",
            "Title": "Book Title"
        },
        hover_data=["average_rating"]
    )

    fig_top_books.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=550,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    # Chart 2: Rating distribution
    fig_rating_dist = px.histogram(
        filtered_df,
        x="review/score",
        nbins=5,
        title="Distribution of Review Scores: 5-Star Reviews Dominate",
        labels={"review/score": "Review Score"}
    )

    fig_rating_dist.update_layout(
        height=400,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    # Chart 3: Review count vs average rating
    scatter_sample = filtered_books.sort_values("review_count", ascending=False).head(1000)

    fig_scatter = px.scatter(
        scatter_sample,
        x="review_count",
        y="average_rating",
        hover_name="Title",
        title="Popularity vs Average Rating",
        labels={
            "review_count": "Number of Reviews",
            "average_rating": "Average Rating"
        },
        render_mode="svg"
    )

    fig_scatter.update_layout(
        height=450,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    fig_scatter.update_layout(
        height=450,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    total_reviews_card = [
        html.H3(f"{len(filtered_df):,}"),
        html.P("Total Reviews")
    ]

    total_books_card = [
        html.H3(f"{filtered_books['Title'].nunique():,}"),
        html.P("Books After Filter")
    ]

    avg_rating = filtered_df["review/score"].mean()
    avg_rating_card = [
        html.H3(f"{avg_rating:.2f}"),
        html.P("Average Rating")
    ]

    return (
        fig_top_books,
        fig_rating_dist,
        fig_scatter,
        total_reviews_card,
        total_books_card,
        avg_rating_card
    )

if __name__ == "__main__":
    app.run(debug=True)