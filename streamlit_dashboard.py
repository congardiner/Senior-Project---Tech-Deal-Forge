"""
Simple Streamlit Dashboard for the 'Tech Deal Forge'

My intent with this project has been to streamline the process of keeping things organized, basic, and informative with the data that I've collected.

Hope you enjoy using this Streamlit dashboard and free service for the Tech Deal Forge!

"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from pathlib import Path

# NOTE: Issue resolved with path not being resolved. (Local Instance)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "output" / "deals.db"


st.set_page_config(
    page_title="Deal Forge",           
    page_icon="",                     # NOTE: NEED to add an image path / icon
    layout="wide",                     
    initial_sidebar_state="expanded"    
)



st.title("The Tech Deal Forge")               
st.subheader("Empowering Data-Driven Decisions for Tech-Related Deals")    

# Text elements for my page - still a work in progress!
st.markdown("**Welcome to Deal Forge!**")  
st.caption("The data for this website is compiled from various sources with the intent to streamline the process of being informed while purchasing into various tech deals. Provision of Deal Insights are provided as a free service.")  # Small gray text


# NOTE: something that I learned, st.cache_data is the way to go for making streamlit super fast to use!
# @st.cache_data decorator prevents reloading data on every interaction
# This makes your app MUCH faster

# Initialize database for cloud deployment (if needed)
if not DB_PATH.exists():
    st.warning("🔧 Initializing database with sample data for demonstration...")
    try:
        from init_cloud_db import init_cloud_database
        init_cloud_database()
        st.success("✅ Database initialized!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Failed to initialize database: {e}")
        st.info("💡 For production: Run scrapers locally or use a remote database")
        st.stop()

@st.cache_data(ttl=60)
def load_deals_data():
    """Load data from SQLite database with caching"""
    
    # SQLite connection - LOCAL
    conn = sqlite3.connect(str(DB_PATH))
    
    # EX: Simple SQL query
    query = "SELECT * FROM deals ORDER BY scraped_at DESC"
    df = pd.read_sql_query(query, conn)
    
    # NOTE: this ensures that the connection is closed; security vulnerability otherwise
    conn.close()
    
    # Conversion of the Timestamp Column from my Database.
    if 'scraped_at' in df.columns:
        df['scraped_at'] = pd.to_datetime(df['scraped_at'])
    
    return df

# Loads the data from my database.
df = load_deals_data()




if df.empty:
    st.error("No data found! Run your scraper first:")
    st.code("python scraper_with_pipeline.py --format database")
    st.stop()  # Stop execution here if no data



### COLUMN Section(s) for the Mapping of my Streamlit Site ###

# Create columns for side-by-side layout
col1, col2, col3, col4 = st.columns(4)  # 4 equal-width columns

# Put metrics in each column
with col1:
    st.metric("Total Deals", len(df))

with col2:
    deals_with_prices = df['price_numeric'].notna().sum()
    st.metric("With Prices", deals_with_prices)

with col3:
    avg_price = df['price_numeric'].mean()
    if pd.notna(avg_price):
        st.metric("Avg Price", f"${avg_price:.2f}")
    else:
        st.metric("Avg Price", "N/A")

with col4:
    # Show latest scrape time
    if 'scraped_at' in df.columns:
        latest = df['scraped_at'].max()
        st.metric("Last Update", latest.strftime("%m/%d %H:%M"))
        # Optional: also show DB file modified time for debugging
        try:
            db_mtime = datetime.fromtimestamp(os.path.getmtime(DB_PATH))
            st.caption(f"DB file mtime: {db_mtime.strftime('%m/%d %H:%M:%S')}")
        except Exception:
            pass

###
# SIDEBAR SECTION: SIDEBAR FOR CONTROLS
###

# Sidebar is perfect for filters and controls
st.sidebar.header("🔧 System Controls")

# Text input for search
search_query = st.sidebar.text_input(
    "Search deals:",
    placeholder="Enter keywords...",
    help="Search in deal titles"  # Tooltip text
)

# Number inputs for price range
st.sidebar.subheader("💰 Price Range")

# Get min/max prices from data
if df['price_numeric'].notna().any():
    min_price_data = float(df['price_numeric'].min())
    max_price_data = float(df['price_numeric'].max())
    
    # Number input widgets
    min_price = st.sidebar.number_input(
        "Minimum Price ($)",
        min_value=0.0,
        max_value=max_price_data,
        value=0.0,
        step=10.0
    )
    
    max_price = st.sidebar.number_input(
        "Maximum Price ($)", 
        min_value=min_price,
        max_value=max_price_data * 1.1,  # Allow slightly higher than max
        value=max_price_data,
        step=10.0
    )
else:
    min_price = max_price = 0
    st.sidebar.info("No price data available")

# Multiselect for categories
categories = df['category'].unique().tolist()
selected_categories = st.sidebar.multiselect(
    "Categories:",
    options=categories,
    default=categories[:5] if len(categories) > 5 else categories,
    help="Select one or more categories"
)

# Checkbox for auto-refresh
auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)")

# Button to clear cache and refresh data
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()  # Clear all cached data
    st.rerun()  # Restart the app


# DATA FILTERING SECTION


# Start with all data
filtered_df = df.copy()

# Apply text search filter
if search_query:
    # Case-insensitive search in title column
    mask = filtered_df['title'].str.contains(search_query, case=False, na=False)
    filtered_df = filtered_df[mask]

# Apply price filters
if min_price > 0:
    price_mask = (filtered_df['price_numeric'] >= min_price) | (filtered_df['price_numeric'].isna())
    filtered_df = filtered_df[price_mask]

if max_price < max_price_data:
    price_mask = (filtered_df['price_numeric'] <= max_price) | (filtered_df['price_numeric'].isna())
    filtered_df = filtered_df[price_mask]

# Apply category filter
if selected_categories:
    filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

###
# DATA QUALITY DASHBOARD SECTION 
###


st.header("🧹 Data Quality Check")

col1, col2, col3, col4 = st.columns(4)

with col1:
    missing_prices = df['price_numeric'].isna().sum()
    st.metric("Missing Prices", f"{missing_prices} ({missing_prices/len(df)*100:.1f}%)")

with col2:
    missing_titles = df['title'].isna().sum()
    st.metric("Missing Titles", missing_titles)

with col3:
    duplicate_links = df['link'].duplicated().sum()
    st.metric("Historical Entries", duplicate_links)

with col4:
    unique_deals = df['link'].nunique()
    st.metric("Unique Deals", unique_deals)



###
# CHARTS WITH PLOTLY (STILL A WORK IN PROGRESS)
###

st.header("Charts & Analytics")

# Create tabs for different chart views
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "💰 Price History", 
    "📊 Deal vs Average", 
    "🔥 Price Drops",
    "📈 Price Distribution", 
    "📊 Categories", 
    "📅 Timeline",
    "🤖 AI Predictions"
])

with tab1:
    st.subheader("💰 Price History Tracker")
    st.caption("Track individual deal prices over time to identify the best buying opportunities")
    
    # Get deals with multiple price entries (historical tracking)
    conn = sqlite3.connect(str(DB_PATH))
    
    deal_history_query = """
        SELECT link, title, COUNT(*) as entry_count
        FROM deals 
        WHERE price_numeric IS NOT NULL AND link IS NOT NULL
        GROUP BY link
        HAVING COUNT(*) > 1
        ORDER BY COUNT(*) DESC
        LIMIT 50
    """
    
    popular_deals = pd.read_sql(deal_history_query, conn)
    
    if not popular_deals.empty:
        # Let user select a deal to track
        selected_deal_title = st.selectbox(
            "Select a deal to view price history:",
            options=popular_deals['title'].tolist(),
            help="Shows deals that have been scraped multiple times",
            key="price_history_selectbox"
        )
        
        # Get full history for selected deal
        deal_link = popular_deals[popular_deals['title'] == selected_deal_title]['link'].iloc[0]
        
        history_query = """
            SELECT scraped_at, price_numeric, title, price_text, website
            FROM deals
            WHERE link = ?
            ORDER BY scraped_at ASC
        """
        
        deal_timeline = pd.read_sql(history_query, conn, params=[deal_link])
        deal_timeline['scraped_at'] = pd.to_datetime(deal_timeline['scraped_at'])
        
        conn.close()
        
        # Create line chart showing price over time
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=deal_timeline['scraped_at'],
            y=deal_timeline['price_numeric'],
            mode='lines+markers',
            name='Price',
            line=dict(color='#FF4B4B', width=3),
            marker=dict(size=10, symbol='circle'),
            hovertemplate='<b>Date:</b> %{x}<br><b>Price:</b> $%{y:.2f}<extra></extra>'
        ))
        
        # Add min/max price annotations
        min_price_idx = deal_timeline['price_numeric'].idxmin()
        max_price_idx = deal_timeline['price_numeric'].idxmax()
        
        fig.add_annotation(
            x=deal_timeline.loc[min_price_idx, 'scraped_at'],
            y=deal_timeline.loc[min_price_idx, 'price_numeric'],
            text=f"Lowest: ${deal_timeline.loc[min_price_idx, 'price_numeric']:.2f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor='green',
            bgcolor='green',
            font=dict(color='white')
        )
        
        fig.add_annotation(
            x=deal_timeline.loc[max_price_idx, 'scraped_at'],
            y=deal_timeline.loc[max_price_idx, 'price_numeric'],
            text=f"Highest: ${deal_timeline.loc[max_price_idx, 'price_numeric']:.2f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor='red',
            bgcolor='red',
            font=dict(color='white')
        )
        
        # Calculate price change
        if len(deal_timeline) > 1:
            price_change = deal_timeline['price_numeric'].iloc[-1] - deal_timeline['price_numeric'].iloc[0]
            price_change_pct = (price_change / deal_timeline['price_numeric'].iloc[0]) * 100
            
            change_color = "green" if price_change < 0 else "red"
            change_symbol = "📉" if price_change < 0 else "📈"
            
            fig.add_annotation(
                text=f"{change_symbol} Overall Change: ${price_change:.2f} ({price_change_pct:+.1f}%)",
                xref="paper", yref="paper",
                x=0.5, y=1.1,
                showarrow=False,
                font=dict(size=16, color=change_color),
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor=change_color,
                borderwidth=2
            )
        
        fig.update_layout(
            title=f"Price History: {selected_deal_title[:60]}...",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            height=450,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0.05)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show price statistics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            current_price = deal_timeline['price_numeric'].iloc[-1]
            st.metric("Current Price", f"${current_price:.2f}")
        
        with col2:
            starting_price = deal_timeline['price_numeric'].iloc[0]
            st.metric("Starting Price", f"${starting_price:.2f}")
        
        with col3:
            lowest = deal_timeline['price_numeric'].min()
            st.metric("Lowest Price", f"${lowest:.2f}", 
                     delta=f"{((lowest - current_price) / current_price * 100):.1f}%")
        
        with col4:
            highest = deal_timeline['price_numeric'].max()
            st.metric("Highest Price", f"${highest:.2f}",
                     delta=f"{((highest - current_price) / current_price * 100):.1f}%")
        
        with col5:
            avg_price = deal_timeline['price_numeric'].mean()
            st.metric("Average Price", f"${avg_price:.2f}")
        
        # Show recent price history table
        st.subheader("📋 Recent Price Changes")
        recent_data = deal_timeline[['scraped_at', 'price_text', 'price_numeric', 'website']].tail(10).sort_values('scraped_at', ascending=False)
        recent_data['scraped_at'] = recent_data['scraped_at'].dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(recent_data, use_container_width=True, hide_index=True)
        
    else:
        st.info("📊 No historical price data yet. Run your scrapers multiple times to track price changes over time!")
        st.markdown("""
        **How to build price history:**
        1. Run scrapers daily: `run_all_scrapers.bat`
        2. Same deals will be tracked over time
        3. Come back to see price trends!
        """)

with tab2:
    st.subheader("📈 Deal vs Category Average")
    st.caption("Compare individual deal prices to their category average")
    
    # Calculate category averages
    category_avg = df[df['price_numeric'].notna()].groupby('category')['price_numeric'].agg(['mean', 'count']).reset_index()
    category_avg.columns = ['category', 'avg_price', 'deal_count']
    category_avg = category_avg[category_avg['deal_count'] >= 3]  # Only categories with 3+ deals
    
    if not category_avg.empty:
        # Select a category
        selected_cat = st.selectbox(
            "Select Category:",
            options=sorted(category_avg['category'].unique()),
            help="Only showing categories with 3+ deals",
            key="deal_vs_avg_selectbox"
        )
        
        # Get deals in this category
        cat_deals = df[(df['category'] == selected_cat) & (df['price_numeric'].notna())].copy()
        cat_avg_price = category_avg[category_avg['category'] == selected_cat]['avg_price'].iloc[0]
        
        # Sort by date
        cat_deals = cat_deals.sort_values('scraped_at')
        
        # Create comparison chart
        fig = go.Figure()
        
        # Plot individual deals
        fig.add_trace(go.Scatter(
            x=cat_deals['scraped_at'],
            y=cat_deals['price_numeric'],
            mode='markers',
            name='Individual Deals',
            marker=dict(
                size=10, 
                color=cat_deals['price_numeric'],
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="Price ($)"),
                line=dict(width=1, color='white')
            ),
            text=cat_deals['title'].str[:50],
            hovertemplate='<b>%{text}...</b><br>Price: $%{y:.2f}<br>Date: %{x}<extra></extra>'
        ))
        
        # Add average line
        fig.add_hline(
            y=cat_avg_price,
            line_dash="dash",
            line_color="red",
            line_width=3,
            annotation_text=f"Category Avg: ${cat_avg_price:.2f}",
            annotation_position="right",
            annotation=dict(font=dict(size=14, color="red"))
        )
        
        # Add shaded region for "good deals" (below average)
        fig.add_hrect(
            y0=cat_deals['price_numeric'].min() * 0.95,
            y1=cat_avg_price,
            fillcolor="green",
            opacity=0.1,
            annotation_text="Below Average (Good Deals)",
            annotation_position="left"
        )
        
        fig.update_layout(
            title=f"{selected_cat} - Deals vs Category Average",
            xaxis_title="Date Scraped",
            yaxis_title="Price ($)",
            height=450,
            hovermode='closest',
            plot_bgcolor='rgba(0,0,0,0.05)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show statistics
        below_avg = cat_deals[cat_deals['price_numeric'] < cat_avg_price]
        above_avg = cat_deals[cat_deals['price_numeric'] >= cat_avg_price]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Deals", len(cat_deals))
        
        with col2:
            st.success(f"🎉 {len(below_avg)} deals below average ({len(below_avg)/len(cat_deals)*100:.1f}%)")
        
        with col3:
            st.warning(f"📊 {len(above_avg)} deals above average ({len(above_avg)/len(cat_deals)*100:.1f}%)")
        
        # Show best deals (below average)
        if not below_avg.empty:
            st.subheader("🏆 Best Deals (Below Average)")
            best_deals = below_avg.nsmallest(5, 'price_numeric')[['title', 'price_numeric', 'website', 'scraped_at']]
            best_deals['scraped_at'] = best_deals['scraped_at'].dt.strftime('%Y-%m-%d')
            best_deals['price_numeric'] = best_deals['price_numeric'].apply(lambda x: f"${x:.2f}")
            st.dataframe(best_deals, use_container_width=True, hide_index=True)
    else:
        st.info("Not enough data for category comparison. Need at least 3 deals per category.")

with tab3:
    st.subheader("🔥 Biggest Price Drops")
    st.caption("Deals that have decreased in price since first scraped")
    
    # Find deals with price history
    conn = sqlite3.connect(str(DB_PATH))
    
    price_drops_query = """
        SELECT 
            d1.title,
            d1.link,
            d1.price_numeric as current_price,
            MIN(d2.price_numeric) as original_price,
            d1.category,
            d1.website,
            (MIN(d2.price_numeric) - d1.price_numeric) as price_drop,
            ((MIN(d2.price_numeric) - d1.price_numeric) / MIN(d2.price_numeric) * 100) as drop_percent,
            d1.scraped_at as last_seen
        FROM deals d1
        INNER JOIN deals d2 ON d1.link = d2.link
        WHERE d1.scraped_at = (SELECT MAX(scraped_at) FROM deals WHERE link = d1.link)
            AND d2.scraped_at < d1.scraped_at
            AND d1.price_numeric IS NOT NULL
            AND d2.price_numeric IS NOT NULL
        GROUP BY d1.link
        HAVING price_drop > 0
        ORDER BY drop_percent DESC
        LIMIT 20
    """
    
    drops = pd.read_sql(price_drops_query, conn)
    conn.close()
    
    if not drops.empty:
        # Create bar chart of price drops
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=drops['drop_percent'],
            y=drops['title'].str[:40] + "...",
            orientation='h',
            marker=dict(
                color=drops['drop_percent'],
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Discount %")
            ),
            text=drops['drop_percent'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Discount: %{x:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title="Top 20 Price Drops (Discount %)",
            xaxis_title="Discount Percentage",
            yaxis_title="",
            height=600,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0.05)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show detailed price drop table
        st.subheader("📋 Price Drop Details")
        
        for idx, row in drops.head(10).iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{row['title'][:60]}...**")
                    st.caption(f"🏪 {row['website']} | 📂 {row['category']}")
                
                with col2:
                    st.metric(
                        "Current Price",
                        f"${row['current_price']:.2f}",
                        delta=f"-${row['price_drop']:.2f}",
                        delta_color="inverse"
                    )
                
                with col3:
                    st.metric(
                        "Discount",
                        f"{row['drop_percent']:.1f}%",
                        delta=f"Was ${row['original_price']:.2f}"
                    )
                
                st.markdown("---")
    else:
        st.info("📊 No price drops detected yet. Run scrapers multiple times to track price changes!")
        st.markdown("""
        **To see price drops:**
        1. Run `run_all_scrapers.bat` daily
        2. Same deals will be tracked over time
        3. Price decreases will appear here!
        """)

with tab4:
    st.subheader("Deal Price Distribution")
    
    # Filter data for chart
    chart_data = filtered_df[filtered_df['price_numeric'].notna() & (filtered_df['price_numeric'] > 0)]
    
    if not chart_data.empty:
        # Create histogram with Plotly
        fig = px.histogram(
            chart_data,
            x='price_numeric',
            nbins=20,
            title="How Many Deals at Each Price Range",
            labels={'price_numeric': 'Price ($)', 'count': 'Number of Deals'}
        )
        
        # Customize the chart
        fig.update_layout(
            xaxis_title="Price ($)",
            yaxis_title="Number of Deals",
            showlegend=False,
            height=400
        )
        
        # Display the chart (use_container_width makes it responsive)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show summary statistics
        st.write("**Price Statistics:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cheapest", f"${chart_data['price_numeric'].min():.2f}")
        with col2:
            st.metric("Most Expensive", f"${chart_data['price_numeric'].max():.2f}")
        with col3:
            st.metric("Median", f"${chart_data['price_numeric'].median():.2f}")
    else:
        st.info("No price data available for the selected filters")

with tab4:
    st.subheader("Deal Price Distribution")
    
    # Filter data for chart
    chart_data = filtered_df[filtered_df['price_numeric'].notna() & (filtered_df['price_numeric'] > 0)]
    
    if not chart_data.empty:
        # Create histogram with Plotly
        fig = px.histogram(
            chart_data,
            x='price_numeric',
            nbins=30,
            title="How Many Deals at Each Price Range",
            labels={'price_numeric': 'Price ($)', 'count': 'Number of Deals'},
            color_discrete_sequence=['#FF4B4B']
        )
        
        # Customize the chart
        fig.update_layout(
            xaxis_title="Price ($)",
            yaxis_title="Number of Deals",
            showlegend=False,
            height=400,
            plot_bgcolor='rgba(0,0,0,0.05)'
        )
        
        # Add vertical line for average
        avg_price = chart_data['price_numeric'].mean()
        fig.add_vline(
            x=avg_price,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Avg: ${avg_price:.2f}",
            annotation_position="top"
        )
        
        # Display the chart (use_container_width makes it responsive)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show summary statistics
        st.write("**Price Statistics:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Cheapest", f"${chart_data['price_numeric'].min():.2f}")
        with col2:
            st.metric("Most Expensive", f"${chart_data['price_numeric'].max():.2f}")
        with col3:
            st.metric("Median", f"${chart_data['price_numeric'].median():.2f}")
        with col4:
            st.metric("Average", f"${avg_price:.2f}")
    else:
        st.info("No price data available for the selected filters")

with tab5:
    st.subheader("Deals by Category")
    
    # Count deals per category
    category_counts = filtered_df['category'].value_counts().head(15)
    
    if not category_counts.empty:
        # Create horizontal bar chart
        fig = px.bar(
            x=category_counts.values,
            y=category_counts.index,
            orientation='h',
            title="Top 15 Categories by Deal Count",
            labels={'x': 'Number of Deals', 'y': 'Category'},
            color=category_counts.values,
            color_continuous_scale='Blues'
        )
        
        # Sort bars by value
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=500,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0.05)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show website comparison
        st.subheader("🏪 Website Price Comparison")
        
        # Calculate average prices by website
        website_stats = df[df['price_numeric'].notna()].groupby('website').agg({
            'price_numeric': ['mean', 'median', 'count'],
            'link': 'nunique'
        }).round(2)
        
        website_stats.columns = ['Avg Price', 'Median Price', 'Total Deals', 'Unique Deals']
        website_stats = website_stats.sort_values('Avg Price')
        
        if not website_stats.empty:
            # Create comparison bar chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Average Price',
                x=website_stats.index,
                y=website_stats['Avg Price'],
                marker_color='lightblue',
                text=website_stats['Avg Price'].apply(lambda x: f'${x:.2f}'),
                textposition='outside'
            ))
            
            fig.add_trace(go.Bar(
                name='Median Price',
                x=website_stats.index,
                y=website_stats['Median Price'],
                marker_color='darkblue',
                text=website_stats['Median Price'].apply(lambda x: f'${x:.2f}'),
                textposition='outside'
            ))
            
            fig.update_layout(
                title="Average vs Median Prices by Website",
                xaxis_title="Website",
                yaxis_title="Price ($)",
                barmode='group',
                height=400,
                plot_bgcolor='rgba(0,0,0,0.05)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category data available")

with tab6:
    st.subheader("Deals Over Time")
    
    if 'scraped_at' in filtered_df.columns:
        # Group by date
        timeline_df = filtered_df.copy()
        timeline_df['date'] = timeline_df['scraped_at'].dt.date
        
        # Daily counts
        daily_counts = timeline_df.groupby('date').size().reset_index(name='deal_count')
        
        # Create area chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_counts['date'],
            y=daily_counts['deal_count'],
            mode='lines',
            name='Daily Deals',
            fill='tozeroy',
            line=dict(color='#FF4B4B', width=2),
            fillcolor='rgba(255, 75, 75, 0.3)'
        ))
        
        fig.update_layout(
            title="Daily Deal Count Over Time",
            xaxis_title="Date",
            yaxis_title="Number of Deals",
            height=400,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0.05)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show deals by day of week
        st.subheader("📅 Best Days for Deals")
        
        timeline_df['day_of_week'] = timeline_df['scraped_at'].dt.day_name()
        day_counts = timeline_df['day_of_week'].value_counts()
        
        # Reorder by actual day order
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = day_counts.reindex([d for d in day_order if d in day_counts.index])
        
        fig = px.bar(
            x=day_counts.index,
            y=day_counts.values,
            title="Deals by Day of Week",
            labels={'x': 'Day', 'y': 'Number of Deals'},
            color=day_counts.values,
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            showlegend=False,
            height=350,
            plot_bgcolor='rgba(0,0,0,0.05)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show hourly pattern if available
        if timeline_df['scraped_at'].dt.hour.nunique() > 1:
            st.subheader("🕐 Hourly Deal Pattern")
            
            timeline_df['hour'] = timeline_df['scraped_at'].dt.hour
            hourly_counts = timeline_df['hour'].value_counts().sort_index()
            
            fig = px.line(
                x=hourly_counts.index,
                y=hourly_counts.values,
                title="Deals by Hour of Day",
                labels={'x': 'Hour (24h)', 'y': 'Number of Deals'},
                markers=True
            )
            
            fig.update_layout(
                height=300,
                plot_bgcolor='rgba(0,0,0,0.05)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No timestamp data available")

with tab7:
    st.subheader("🤖 AI-Powered Deal Predictions")
    st.caption("Machine learning model predicts deal quality based on price, rating, reviews, and more")
    
    # ML Helper Functions
    def load_ml_model(model_path):
        """Load trained model from file"""
        import joblib
        import os
        try:
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                return model, None
            else:
                return None, f"Model file not found: {model_path}"
        except Exception as e:
            return None, f"Error loading model: {str(e)}"
    
    def prepare_deal_features(deal_row):
        """Prepare features for a single deal - MUST MATCH training script"""
        features = {}
        
        # Basic features
        features['price_numeric'] = float(deal_row.get('price_numeric', 0))
        features['discount_percent'] = float(deal_row.get('discount_percent', 0))
        features['rating'] = float(deal_row.get('rating', 0))
        features['reviews_count'] = int(deal_row.get('reviews_count', 0))
        
        # Website encoding
        website = str(deal_row.get('website', '')).lower()
        features['website_bestbuy'] = 1 if 'bestbuy' in website else 0
        features['website_slickdeals'] = 1 if 'slickdeals' in website else 0
        
        # Category encoding
        category = str(deal_row.get('category', '')).lower()
        features['category_gaming'] = 1 if 'gaming' in category or 'game' in category else 0
        features['category_laptop'] = 1 if 'laptop' in category or 'notebook' in category else 0
        features['category_monitor'] = 1 if 'monitor' in category or 'display' in category else 0
        
        # Temporal features
        if 'scraped_at' in deal_row:
            scraped_at = pd.to_datetime(deal_row['scraped_at'])
            features['day_of_week'] = scraped_at.dayofweek
            features['month'] = scraped_at.month
            features['is_weekend'] = 1 if scraped_at.dayofweek >= 5 else 0
        else:
            features['day_of_week'] = 0
            features['month'] = 1
            features['is_weekend'] = 0
        
        # Historical features (simple defaults)
        features['price_vs_avg'] = 1.0
        features['price_vs_min'] = 1.0
        features['times_seen'] = 1
        features['price_std'] = 0
        features['recent_trend'] = 0
        
        # Create DataFrame with exact feature order
        feature_cols = [
            'price_numeric', 'discount_percent', 'rating', 'reviews_count',
            'website_bestbuy', 'website_slickdeals',
            'category_gaming', 'category_laptop', 'category_monitor',
            'day_of_week', 'month', 'is_weekend',
            'price_vs_avg', 'price_vs_min', 'times_seen', 'price_std', 'recent_trend'
        ]
        
        return pd.DataFrame([[features[col] for col in feature_cols]], columns=feature_cols)
    
    def predict_deal_quality(model, deal_row):
        """Predict deal quality score (0-100)"""
        try:
            X = prepare_deal_features(deal_row)
            score = model.predict(X)[0]
            
            # Classify the deal
            if score >= 75:
                label = "🔥 Excellent Deal"
                color = "success"
            elif score >= 60:
                label = "👍 Good Deal"
                color = "info"
            elif score >= 40:
                label = "👌 Fair Deal"
                color = "warning"
            else:
                label = "❌ Poor Deal"
                color = "error"
            
            return {
                'score': score,
                'label': label,
                'color': color,
                'error': None
            }
        except Exception as e:
            return {
                'score': 0,
                'label': 'Error',
                'color': 'error',
                'error': str(e)
            }
    
    # Model path input
    model_path = st.text_input(
        "Model file path:",
        value="deal_predictor_model.joblib",
        help="Path to your trained model file (download from Google Colab)"
    )
    
    # Try to load model
    model, error = load_ml_model(model_path)
    
    if error:
        st.error(error)
        st.info("👉 Train your model using `colab_training_script.py` in Google Colab")
        
        with st.expander("📚 How to Train Your Model"):
            st.markdown("""
            **Steps to get your ML model:**
            
            1. **Export your data:**
               ```bash
               python prepare_ml_data.py
               ```
               This creates `output/ml_data/ml_features_*.csv`
            
            2. **Upload to Google Colab:**
               - Open `colab_training_script.py` in Google Colab
               - Upload your CSV file when prompted
               - Run all cells
            
            3. **Download the model:**
               - Download the `.joblib` file from Colab
               - Place it in your project folder
               - Enter the filename above
            
            4. **Start predicting!** 🎉
            """)
            
            st.code("""
# Quick start command:
python prepare_ml_data.py

# Then upload the generated CSV to Google Colab
            """, language="bash")
    else:
        st.success(f"✅ Model loaded successfully!")
        
        # Filter deals with prices for predictions
        deals_with_prices = df[df['price_numeric'].notna()].copy()
        
        if deals_with_prices.empty:
            st.warning("No deals with prices to predict on")
        else:
            # Make predictions for all deals
            st.subheader("🎯 Running AI predictions...")
            
            with st.spinner("Analyzing deals with machine learning..."):
                predictions = []
                for idx, deal in deals_with_prices.iterrows():
                    result = predict_deal_quality(model, deal)
                    predictions.append(result['score'])
                
                deals_with_prices['ml_score'] = predictions
            
            st.success(f"✅ Predicted {len(deals_with_prices)} deals!")
            
            # Show statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                excellent = len(deals_with_prices[deals_with_prices['ml_score'] >= 75])
                st.metric("🔥 Excellent Deals", excellent, 
                         delta=f"{excellent/len(deals_with_prices)*100:.1f}%")
            
            with col2:
                good = len(deals_with_prices[(deals_with_prices['ml_score'] >= 60) & (deals_with_prices['ml_score'] < 75)])
                st.metric("👍 Good Deals", good,
                         delta=f"{good/len(deals_with_prices)*100:.1f}%")
            
            with col3:
                fair = len(deals_with_prices[(deals_with_prices['ml_score'] >= 40) & (deals_with_prices['ml_score'] < 60)])
                st.metric("👌 Fair Deals", fair,
                         delta=f"{fair/len(deals_with_prices)*100:.1f}%")
            
            with col4:
                poor = len(deals_with_prices[deals_with_prices['ml_score'] < 40])
                st.metric("❌ Poor Deals", poor,
                         delta=f"{poor/len(deals_with_prices)*100:.1f}%")
            
            # Distribution chart
            st.subheader("📊 Deal Quality Distribution")
            
            fig = px.histogram(
                deals_with_prices,
                x='ml_score',
                nbins=20,
                title="Distribution of ML Scores",
                labels={'ml_score': 'ML Quality Score', 'count': 'Number of Deals'},
                color_discrete_sequence=['#FF4B4B']
            )
            
            # Add vertical lines for thresholds
            fig.add_vline(x=75, line_dash="dash", line_color="green", 
                         annotation_text="Excellent", annotation_position="top")
            fig.add_vline(x=60, line_dash="dash", line_color="blue",
                         annotation_text="Good", annotation_position="top")
            fig.add_vline(x=40, line_dash="dash", line_color="orange",
                         annotation_text="Fair", annotation_position="top")
            
            fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0.05)')
            st.plotly_chart(fig, use_container_width=True)
            
            # Show top deals
            st.subheader("🏆 Top 10 AI-Recommended Deals")
            
            top_deals = deals_with_prices.nlargest(10, 'ml_score')
            
            for idx, deal in top_deals.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{deal['title'][:80]}...**")
                        st.caption(f"🏪 {deal.get('website', 'N/A')} | 📂 {deal.get('category', 'N/A')}")
                    
                    with col2:
                        price = deal.get('price_numeric', 0)
                        discount = deal.get('discount_percent', 0)
                        st.metric("Price", f"${price:.2f}")
                        if discount > 0:
                            st.caption(f"💰 {discount:.0f}% off")
                    
                    with col3:
                        score = deal['ml_score']
                        
                        # Color-code the score
                        if score >= 75:
                            st.success(f"**Score: {score:.1f}**")
                            st.caption("🔥 Excellent!")
                        elif score >= 60:
                            st.info(f"**Score: {score:.1f}**")
                            st.caption("👍 Good")
                        elif score >= 40:
                            st.warning(f"**Score: {score:.1f}**")
                            st.caption("👌 Fair")
                        else:
                            st.error(f"**Score: {score:.1f}**")
                            st.caption("❌ Poor")
                    
                    st.markdown("---")
            
            # Interactive deal search
            st.subheader("🔍 Check Individual Deal Score")
            
            search_deals = deals_with_prices.nlargest(100, 'ml_score')  # Top 100 for dropdown
            
            selected_deal = st.selectbox(
                "Select a deal to analyze:",
                options=search_deals['title'].tolist(),
                help="Choose a deal to see detailed ML analysis",
                key="ml_deal_analysis_selectbox"
            )
            
            if selected_deal:
                deal_data = deals_with_prices[deals_with_prices['title'] == selected_deal].iloc[0]
                result = predict_deal_quality(model, deal_data)
                
                # Score display
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("🎯 ML Score", f"{result['score']:.1f} / 100")
                
                with col2:
                    # Score badge
                    if result['score'] >= 75:
                        st.success(f"**{result['label']}**")
                    elif result['score'] >= 60:
                        st.info(f"**{result['label']}**")
                    elif result['score'] >= 40:
                        st.warning(f"**{result['label']}**")
                    else:
                        st.error(f"**{result['label']}**")
                
                with col3:
                    # Recommendation
                    if result['score'] >= 70:
                        st.success("✅ **RECOMMENDED**")
                    elif result['score'] >= 50:
                        st.info("🤔 **CONSIDER**")
                    else:
                        st.warning("⏳ **WAIT FOR BETTER**")
                
                # Deal details
                st.subheader("📋 Deal Details")
                
                detail_col1, detail_col2 = st.columns(2)
                
                with detail_col1:
                    st.write("**Pricing:**")
                    st.write(f"- Current Price: ${deal_data.get('price_numeric', 0):.2f}")
                    st.write(f"- Discount: {deal_data.get('discount_percent', 0):.0f}%")
                    if deal_data.get('original_price'):
                        st.write(f"- Original: ${deal_data.get('original_price', 0):.2f}")
                
                with detail_col2:
                    st.write("**Reviews & Ratings:**")
                    rating = deal_data.get('rating', 0)
                    st.write(f"- Rating: {rating:.1f}⭐")
                    st.write(f"- Reviews: {deal_data.get('reviews_count', 0):,}")
                    st.write(f"- Website: {deal_data.get('website', 'N/A')}")
                
                # Link to deal
                if 'link' in deal_data and deal_data['link']:
                    st.markdown(f"🔗 [View Deal]({deal_data['link']})")

# ===================================
# LESSON 8: DISPLAYING DATA TABLES
# ===================================

st.header("🔍 Deal Search Results")

# Show how many results
st.write(f"**Found {len(filtered_df)} deals** (filtered from {len(df)} total)")

# Select which columns to show
display_columns = ['title', 'price', 'category', 'scraped_at']
available_columns = [col for col in display_columns if col in filtered_df.columns]

# Show data table
if not filtered_df.empty and available_columns:
    
    # Sort options
    sort_column = st.selectbox(
        "Sort by:",
        options=available_columns,
        index=len(available_columns)-1,  # Default to last column (usually timestamp)
        key="sort_column_selectbox"
    )
    
    # Sort the data
    if sort_column in filtered_df.columns:
        display_df = filtered_df[available_columns].sort_values(sort_column, ascending=False)
    else:
        display_df = filtered_df[available_columns]
    
    # Pagination - show 20 deals per page
    page_size = 20
    total_pages = len(display_df) // page_size + 1
    
    # Page selector
    page_number = st.number_input(
        f"Page (1-{total_pages}):",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1
    )
    
    # Calculate start and end indices
    start_idx = (page_number - 1) * page_size
    end_idx = start_idx + page_size
    
    # Display the data slice
    st.dataframe(
        display_df.iloc[start_idx:end_idx],
        use_container_width=True,
        hide_index=True
    )
    
    # ===================================
    # LESSON 9: FILE DOWNLOADS
    # ===================================
    
    st.subheader("📁 Directly Download Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        
        # Automatic CSV conversion
        csv_data = filtered_df.to_csv(index=False)
        

        st.download_button(
            label="📄 Download as CSV",
            data=csv_data,
            file_name=f"deals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="Download the filtered results as an Excel-Friendly CSV file"
        )
    
    with col2:
        # Convert to JSON
        json_data = filtered_df.to_json(orient='records', indent=2)
        
        st.download_button(
            label="📋 Download as JSON", 
            data=json_data,
            file_name=f"deals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            help="Download the filtered results as a JSON file"
        )

else:
    st.info("No deals found matching your current search criteria")

# ===================================
# LESSON 10: STATUS AND UPDATES
# ===================================

# Footer with status
st.markdown("---")  # Horizontal line

# Status information
col1, col2, col3 = st.columns(3)

with col1:
    st.write(f"**Database:** {DB_PATH}")

with col2:
    st.write(f"**Last Refresh:** {datetime.now().strftime('%H:%M:%S')}")

with col3:
    if auto_refresh:
        st.write("🔄 **Auto-refresh:** ON")
        # Auto-refresh every 30 seconds
        st.empty()  # Placeholder for refresh
        # Note: In a real app, you'd use st.rerun() with a timer
    else:
        st.write("⏸️ **Auto-refresh:** OFF")



if auto_refresh:
    # Wait 30 seconds and refresh
    import time
    time.sleep(30)
    # Clear cache so fresh DB reads are used after rerun
    st.cache_data.clear()
    st.rerun()