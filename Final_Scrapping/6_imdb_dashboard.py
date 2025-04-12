import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Load your IMDb CSV
df = pd.read_csv("new_cleaned_merged5_imdb_2024.csv")

st.set_page_config(page_title="IMDb Movie Insights", layout="wide")
st.title("🎬 IMDb Movie Insights Dashboard")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Movies")
genres = st.sidebar.multiselect("Genre", df["Genre"].unique(), default=df["Genre"].unique())
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 0.0)
min_votes = st.sidebar.number_input("Minimum Votes", min_value=0, value=0)
duration_option = st.sidebar.radio("Duration", ["All", "< 2 hrs", "2–3 hrs", "> 3 hrs"])

filtered_df = df[df["Genre"].isin(genres)]
filtered_df = filtered_df[filtered_df["Rating"] >= min_rating]
filtered_df = filtered_df[filtered_df["Votes"] >= min_votes]

if duration_option == "< 2 hrs":
    filtered_df = filtered_df[filtered_df["Duration"] < 120]
elif duration_option == "2–3 hrs":
    filtered_df = filtered_df[(filtered_df["Duration"] >= 120) & (filtered_df["Duration"] <= 180)]
elif duration_option == "> 3 hrs":
    filtered_df = filtered_df[filtered_df["Duration"] > 180]

# --- Filtered Results Table ---
st.subheader("🎯 Filtered Results")
st.dataframe(filtered_df)

# --- Top 10 Movies by Rating and Votes ---
st.subheader("⭐ Top 10 Movies by Rating & Votes")
top_movies = df[df["Votes"] > 1000].sort_values(by=["Rating", "Votes"], ascending=False).head(10)
st.dataframe(top_movies)

# --- Genre Distribution ---
st.subheader("📊 Genre Distribution")
genre_count = df["Genre"].value_counts()
fig1 = px.bar(x=genre_count.index, y=genre_count.values, labels={"x": "Genre", "y": "Count"})
st.plotly_chart(fig1, use_container_width=True)

# --- Average Duration by Genre ---
st.subheader("⏱️ Average Duration by Genre")
avg_duration = df.groupby("Genre")["Duration"].mean().sort_values()
fig2 = px.bar(x=avg_duration.values, y=avg_duration.index, orientation='h',
              labels={"x": "Avg Duration (min)", "y": "Genre"})
st.plotly_chart(fig2, use_container_width=True)

# --- Voting Trends by Genre ---
st.subheader("🗳️ Average Voting Counts by Genre")
avg_votes = df.groupby("Genre")["Votes"].mean().sort_values()
fig3 = px.bar(x=avg_votes.index, y=avg_votes.values, labels={"x": "Genre", "y": "Average Votes"})
st.plotly_chart(fig3, use_container_width=True)

# --- Rating Distribution ---
st.subheader("📉 Rating Distribution")
fig4 = px.histogram(df, x="Rating", nbins=20, title="IMDb Ratings")
st.plotly_chart(fig4, use_container_width=True)

# --- Genre-Based Rating Leaders ---
st.subheader("🏆 Top-Rated Movies by Genre")
top_by_genre = df.loc[df.groupby("Genre")["Rating"].idxmax()]
st.dataframe(top_by_genre[["Title", "Genre", "Rating", "Votes", "Duration"]])

# --- Most Popular Genres by Voting (Pie Chart) ---
st.subheader("🔥 Most Popular Genres by Total Votes")
genre_votes = df.groupby("Genre")["Votes"].sum().sort_values(ascending=False)
fig5 = px.pie(values=genre_votes.values, names=genre_votes.index)
st.plotly_chart(fig5, use_container_width=True)

# --- Duration Extremes ---
st.subheader("📏 Duration Extremes")
shortest = df.loc[df["Duration"].idxmin()]
longest = df.loc[df["Duration"].idxmax()]
col1, col2 = st.columns(2)
with col1:
    st.metric("Shortest Movie", f"{shortest['Title']}", f"{shortest['Duration']} min")
with col2:
    st.metric("Longest Movie", f"{longest['Title']}", f"{longest['Duration']} min")

# --- Ratings by Genre (Heatmap) ---
st.subheader("🌡️ Average Ratings by Genre (Heatmap)")
heatmap_data = df.pivot_table(values="Rating", index="Genre", aggfunc="mean")
fig6, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
st.pyplot(fig6)

# --- Correlation Analysis ---
st.subheader("🔗 Correlation: Ratings vs Votes")
fig7 = px.scatter(df, x="Votes", y="Rating", hover_data=["Title", "Genre"], trendline="ols")
st.plotly_chart(fig7, use_container_width=True)
