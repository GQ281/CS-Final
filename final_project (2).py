import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import folium_static


st.set_page_config(page_title="McDonald's Reviews Explorer", layout="wide")


st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(to bottom right, #f5f7fa, #c3cfe2);
        color: #000000;
    }
    .sticky-right {
        position: -webkit-sticky;
        position: sticky;
        top: 70px;
        align-self: start;
        background: rgba(255, 255, 255, 0.7);
        padding: 10px;
        border-radius: 10px;
        backdrop-filter: blur(8px);
    }
    .review-box {
        background-color: #3a3a3a;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        color: white;
    }
    .hover-name:hover {
        background-color: #e0e0e0;
        border-radius: 5px;
        padding-left: 5px;
    }
    button:hover {
        background-color: #ff4b4b !important;
        color: white !important;
        transition: 0.3s;
    }
    </style>
""", unsafe_allow_html=True)


df = pd.read_csv('McDonald_s_Reviews.csv', encoding='latin1')


review_col = 'review'
rating_col = 'rating'


df[rating_col] = df[rating_col].astype(str).str.extract(r'(\d)').astype(float)


df = df[df[review_col].notnull()]
df[review_col] = df[review_col].astype(str).str.encode('latin1', errors='ignore').str.decode('utf-8', errors='ignore')

def is_valid_review(text):
    return text.count('�') <= 2 and any(c.isalpha() for c in str(text))

df = df[df[review_col].apply(is_valid_review)]


emoji_map = {1: 'Angry', 2: 'Sad', 3: 'Neutral', 4: 'Happy', 5: 'Very Happy'}
df['Mood'] = [emoji_map.get(int(rating), '') for rating in df[rating_col]]
df['ReviewLength'] = df[review_col].astype(str).str.len()


left_col, right_col = st.columns([3, 1])


with right_col:
    with st.container():
        st.markdown('<div class="sticky-right">', unsafe_allow_html=True)

        with st.expander("📋 Menu", expanded=True):
            menu = st.radio(
                "Choose a page:",
                [
                    "🏠 Home",
                    "📊 Rating Distribution",
                    "📈 Detailed Rating View",
                    "😄 Emoji Mood Chart",
                    "🎯 Filter Reviews by Rating",
                    "🔍 Search Reviews",
                    "📏 Review Length Correlation",
                    "🗺️ McDonald's Locations Map",
                    "🗽 Times Square McDonald's",
                    "🏆 Best and Worst Locations"
                ],
                key="menu"
            )

        with st.expander("👥 Group Members", expanded=False):
            st.markdown('<div class="hover-name">Gabriel Quevedo</div>', unsafe_allow_html=True)
            st.markdown('<div class="hover-name">Giordana Perez</div>', unsafe_allow_html=True)
            st.markdown('<div class="hover-name">Widad Coriat</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


with left_col:
    if menu == "🏠 Home":
        st.markdown("<h1 style='text-align: center;'>🏠 Welcome to McDonald's Reviews Explorer</h1>",
                    unsafe_allow_html=True)
        st.image("G3No.gif", use_container_width=True)

    if menu == "📊 Rating Distribution":
        st.markdown("## 📊 Rating Distribution")
        fig, ax = plt.subplots()
        ax.bar(df[rating_col].value_counts().sort_index().index, df[rating_col].value_counts().sort_index().values, color='gold')
        ax.set_xlabel("Star Rating")
        ax.set_ylabel("Number of Reviews")
        ax.set_title("How People Rated McDonald's")
        st.pyplot(fig)
        with st.expander("Learn More"):
            st.write("Shows the distribution of star ratings left by customers.")

    if menu == "📈 Detailed Rating View":
        st.markdown("## 📈 Detailed Rating View")
        fig, ax = plt.subplots()
        sns.countplot(x=rating_col, data=df, palette='pastel', ax=ax)
        ax.set_title("Star Ratings Count")
        st.pyplot(fig)
        with st.expander("Learn More"):
            st.write("More detailed view using Seaborn for star ratings.")

    if menu == "😄 Emoji Mood Chart":
        st.markdown("## 😄 Emoji Mood Chart")
        fig, ax = plt.subplots()
        sns.countplot(x='Mood', data=df, order=['Angry', 'Sad', 'Neutral', 'Happy', 'Very Happy'], palette='coolwarm', ax=ax)
        ax.set_title("Mood Distribution")
        st.pyplot(fig)
        with st.expander("Learn More"):
            st.write("This matches rating numbers with emotional mood labels.")

    if menu == "🎯 Filter Reviews by Rating":
        st.markdown("## 🎯 Filter Reviews by Rating")
        rating_range = st.slider("Select Rating Range", int(df[rating_col].min()), int(df[rating_col].max()), (int(df[rating_col].min()), int(df[rating_col].max())))
        filtered_df = df[(df[rating_col] >= rating_range[0]) & (df[rating_col] <= rating_range[1])]
        st.write(f"Showing {len(filtered_df)} real reviews:")

        if not filtered_df.empty:
            for idx, row in filtered_df.head(5).iterrows():
                stars = int(row[rating_col])
                star_text = "Star" if stars == 1 else "Stars"
                review_text = str(row[review_col])
                st.markdown(f"""
                <div class="review-box">
                    ⭐ {stars} {star_text}<br><br>
                    {review_text}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No reviews found for this rating range.")

    if menu == "🔍 Search Reviews":
        st.markdown("## 🔍 Search Reviews")
        keyword = st.text_input("Enter a keyword to search reviews")
        if keyword:
            keyword_reviews = df[df[review_col].astype(str).str.contains(keyword, case=False, na=False)]
            st.write(f"Found {len(keyword_reviews)} reviews containing '{keyword}':")
            if not keyword_reviews.empty:
                st.dataframe(keyword_reviews[[review_col, rating_col]].head(5))

    if menu == "📏 Review Length Correlation":
        st.markdown("## 📏 Review Length vs Rating")
        fig, ax = plt.subplots()
        sns.regplot(x='ReviewLength', y=rating_col, data=df, scatter_kws={'alpha':0.5}, line_kws={'color':'red'}, ax=ax)
        ax.set_xlabel("Review Length (characters)")
        ax.set_ylabel("Rating")
        ax.set_title("Do Longer Reviews Mean Higher Ratings?")
        st.pyplot(fig)
        with st.expander("Learn More"):
            st.write("Examines if longer reviews tend to give higher or lower ratings.")

    if menu == "🗺️ McDonald's Locations Map":
        st.markdown("## 🗺️ McDonald's Locations Map")


        df_clean = df.dropna(subset=['latitude ', 'longitude', rating_col])
        location_groups = df_clean.groupby(['store_name', 'store_address', 'latitude ', 'longitude'])[
            rating_col].mean().reset_index()


        avg_lat = location_groups['latitude '].mean()
        avg_lon = location_groups['longitude'].mean()
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=4)



        def get_color(rating):
            if rating >= 4.5:
                return 'green'
            elif rating >= 3.5:
                return 'blue'
            elif rating >= 2.5:
                return 'orange'
            else:
                return 'red'



        for _, row in location_groups.iterrows():
            color = get_color(row[rating_col])
            popup_text = f"{row['store_name']}<br>{row['store_address']}<br>⭐ {row[rating_col]:.2f}"
            folium.Marker(
                location=[row['latitude '], row['longitude']],
                popup=popup_text,
                icon=folium.Icon(color=color, icon='cutlery', prefix='fa')
            ).add_to(m)

        folium_static(m)

        with st.expander("Learn More"):
            st.write("This map shows McDonald's locations with color-coded markers based on average ratings.")

    if menu == "🗽 Times Square McDonald's":
        st.markdown("## 🗽 Times Square McDonald's")
        m2 = folium.Map(location=[40.7580, -73.9855], zoom_start=16)
        folium.Marker(
            [40.7580, -73.9855],
            popup="Times Square McDonald's",
            icon=folium.Icon(color='green', icon='star', prefix='fa')
        ).add_to(m2)
        folium.CircleMarker(
            location=[40.7580, -73.9855],
            radius=50,
            color='yellow',
            fill=True,
            fill_color='yellow',
            fill_opacity=0.3,
            popup='Cool Area to Visit!'
        ).add_to(m2)
        folium_static(m2)
        with st.expander("Learn More"):
            st.write("Zoomed-in view of Times Square's McDonald's.")

    if menu == "🏆 Best and Worst Locations":
        st.markdown("## 🏆 Best and Worst Locations")
        if 'store_address' in df.columns:
            df['City'] = df['store_address'].astype(str).str.extract(r'(.*?),')[0]
            city_avg = df.groupby('City')[rating_col].mean().dropna().sort_values(ascending=False)

            best_cities = city_avg.head(5)
            worst_cities = city_avg.tail(5)

            st.write("### 🥇 Best Locations")
            st.dataframe(best_cities)

            st.write("### 🥀 Worst Locations")
            st.dataframe(worst_cities)

            m3 = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
            for city, score in best_cities.items():
                folium.Marker(
                    [39 + score/10, -98 + score/10],
                    popup=f"{city}: {score:.2f} ⭐",
                    icon=folium.Icon(color='green')
                ).add_to(m3)
            for city, score in worst_cities.items():
                folium.Marker(
                    [39 - score/10, -98 - score/10],
                    popup=f"{city}: {score:.2f} ⭐",
                    icon=folium.Icon(color='red')
                ).add_to(m3)
            folium_static(m3)
            with st.expander("Learn More"):
                st.write("Locations ranked based on customer ratings. Higher = better experience.")
        else:
            st.warning("Store address (city) information missing for Best/Worst analysis.")