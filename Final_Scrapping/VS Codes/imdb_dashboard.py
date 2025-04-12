import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# 1. Connect to MySQL Workbench
@st.cache_resource
def load_data():
    connection = mysql.connector.connect(
        host='localhost',
        user='your_username',
        password='your_password',
        database='project1_imdb'
    )
    query = "SELECT * FROM imdb_2024_movies"
    df = pd.read_sql(query, connection)
    connection.close()
    return df

df = load_data()

st.title("🎬 IMDb 2024 Movie Analysis Dashboard")

# -------------------------------------
# FILTERS
# -------------------------------------
st.sidebar.header("🔎 Filter Movies")
genres = st.sidebar.multiselect("Select Genres", options=df['Genre'].unique(), default=df['Genre'].unique())
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 0.0, 0.1)
min_votes = st.sidebar.number_input("Minimum Voting Count", value=0)
duration_option = st.sidebar.selectbox("Duration (Hours)", ["All", "< 2 hrs", "2–3 hrs", "> 3 hrs"])

# Convert duration string (e.g. "120 min") to int
df["Duration_Min"] = df["Duration"].str.extract("(\d+)").astype(float)

# Apply filters
filtered_df = df[
    (df['Genre'].isin(genres)) &
    (df['Rating'] >= min_rating) &
    (df['Votes'] >= min_votes)
]

if duration_option == "< 2 hrs":
    filtered_df = filtered_df[filtered_df["Duration_Min"] < 120]
elif duration_option == "2–3 hrs":
    filtered_df = filtered_df[(filtered_df["Duration_Min"] >= 120) & (filtered_df["Duration_Min"] <= 180)]
elif duration_option == "> 3 hrs":
    filtered_df = filtered_df[filtered_df["Duration_Min"] > 180]

st.subheader("🎯 Filtered Movie Results")
st.dataframe(filtered_df)

# -------------------------------------
# VISUALIZATIONS
# -------------------------------------

# 1. Top 10 Movies by Rating and Voting Count
st.subheader("⭐ Top 10 Movies by Rating and Votes")
top_movies = df[df["Votes"] > 1000].sort_values(by=["Rating", "Votes"], ascending=False).head(10)
st.table(top_movies[["Title", "Genre", "Rating", "Votes"]])

# 2. Genre Distribution
st.subheader("📊 Genre Distribution")
genre_counts = df['Genre'].value_counts()
st.bar_chart(genre_counts)

# 3. Average Duration by Genre
st.subheader("⏱️ Average Duration by Genre")
avg_duration = df.groupby("Genre")["Duration_Min"].mean().sort_values()
st.bar_chart(avg_duration)

# 4. Voting Trends by Genre
st.subheader("🗳️ Voting Trends by Genre")
avg_votes = df.groupby("Genre")["Votes"].mean().sort_values(ascending=False)
st.bar_chart(avg_votes)

# 5. Rating Distribution
st.subheader("📉 Rating Distribution")
fig1, ax1 = plt.subplots()
sns.histplot(df["Rating"], bins=20, kde=True, ax=ax1)
st.pyplot(fig1)

# 6. Genre-Based Rating Leaders
st.subheader("🏆 Top-Rated Movie per Genre")
idx = df.groupby('Genre')['Rating'].idxmax()
genre_leaders = df.loc[idx, ['Genre', 'Title', 'Rating']]
st.table(genre_leaders.sort_values(by="Rating", ascending=False))

# 7. Most Popular Genres by Voting
st.subheader("📈 Most Popular Genres (by Total Votes)")
votes_by_genre = df.groupby("Genre")["Votes"].sum().sort_values(ascending=False)
fig2 = px.pie(names=votes_by_genre.index, values=votes_by_genre.values, title="Voting Popularity by Genre")
st.plotly_chart(fig2)

# 8. Duration Extremes
st.subheader("⏳ Duration Extremes")
min_duration = df.loc[df["Duration_Min"].idxmin()]
max_duration = df.loc[df["Duration_Min"].idxmax()]
col1, col2 = st.columns(2)
with col1:
    st.metric("Shortest Movie", f"{min_duration['Title']}", f"{min_duration['Duration']}")
with col2:
    st.metric("Longest Movie", f"{max_duration['Title']}", f"{max_duration['Duration']}")

# 9. Ratings by Genre (Heatmap)
st.subheader("🔥 Ratings by Genre (Heatmap)")
pivot_data = df.pivot_table(values='Rating', index='Genre', aggfunc='mean')
fig3, ax3 = plt.subplots()
sns.heatmap(pivot_data, annot=True, cmap='coolwarm', linewidths=.5, ax=ax3)
st.pyplot(fig3)

# 10. Correlation: Ratings vs Votes
st.subheader("📌 Ratings vs Voting Counts")
fig4 = px.scatter(df, x="Votes", y="Rating", color="Genre", hover_data=["Title"])
st.plotly_chart(fig4)
