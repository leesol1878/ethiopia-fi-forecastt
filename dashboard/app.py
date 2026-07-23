"""
Financial Inclusion Dashboard - Ethiopia
Interactive dashboard for exploring financial inclusion data, event impacts, and forecasts
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Ethiopia Financial Inclusion Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load all required data"""
    # Load main dataset - absolute path from project root
    df = pd.read_csv('data/processed/ethiopia_fi_enriched.csv')
    
    # Load association matrix
    assoc_matrix = pd.read_csv('data/processed/association_matrix.csv', index_col=0)
    
    # Load forecasts
    forecasts = pd.read_csv('data/processed/forecast_summary.csv')
    
    # Split by type
    observations = df[df['record_type'] == 'observation']
    events = df[df['record_type'] == 'event']
    targets = df[df['record_type'] == 'target']
    impacts = df[df['record_type'] == 'impact_link']
    
    return df, observations, events, targets, impacts, assoc_matrix, forecasts# Load data
try:
    df, observations, events, targets, impacts, assoc_matrix, forecasts = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    data_loaded = False

if data_loaded:
    # Sidebar
    st.sidebar.title("📊 Navigation")
    
    # Create navigation menu
    menu_options = ["🏠 Overview", "📈 Trends", "🔮 Forecasts", "🎯 Impact Matrix", "📊 Data Explorer"]
    choice = st.sidebar.radio("Go to", menu_options)
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.info(
        """
        **About**
        This dashboard visualizes Ethiopia's financial inclusion journey.
        
        **Data Sources:**
        - Global Findex
        - GSMA Reports
        - EthSwitch
        - Ethio Telecom
        - Safaricom
        """
    )
    st.sidebar.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}")
    
    # ========== OVERVIEW PAGE ==========
    if choice == "🏠 Overview":
        st.markdown('<p class="main-header">🇪🇹 Ethiopia Financial Inclusion Dashboard</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Get latest values
        latest_acc = observations[observations['indicator_code'] == 'ACC_OWNERSHIP'].iloc[-1]['value_numeric']
        latest_mm = observations[observations['indicator_code'] == 'ACC_MM_ACCOUNT'].iloc[-1]['value_numeric']
        total_events = len(events)
        
        # Get P2P latest
        p2p_data = observations[observations['indicator_code'] == 'USG_P2P_COUNT']
        latest_p2p = p2p_data.iloc[-1]['value_numeric'] / 1e6 if len(p2p_data) > 0 else 0
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<p style="font-size:0.9rem; color:#666;">Account Ownership</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="metric-value">{latest_acc:.1f}%</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<p style="font-size:0.9rem; color:#666;">Mobile Money</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="metric-value">{latest_mm:.2f}%</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<p style="font-size:0.9rem; color:#666;">P2P Transactions</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="metric-value">{latest_p2p:.1f}M</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<p style="font-size:0.9rem; color:#666;">Total Events</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="metric-value">{total_events}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Two column layout for charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Account Ownership Trend")
            acc_data = observations[observations['indicator_code'] == 'ACC_OWNERSHIP'].copy()
            acc_data['date'] = pd.to_datetime(acc_data['observation_date'])
            acc_data = acc_data.sort_values('date')
            
            fig = px.line(acc_data, x='date', y='value_numeric', 
                          markers=True, title='Account Ownership Over Time')
            fig.update_layout(height=350, showlegend=False)
            fig.update_traces(line=dict(color='#1f77b4', width=3))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Mobile Money Penetration")
            mm_data = observations[observations['indicator_code'] == 'ACC_MM_ACCOUNT'].copy()
            mm_data['date'] = pd.to_datetime(mm_data['observation_date'])
            mm_data = mm_data.sort_values('date')
            
            fig = px.line(mm_data, x='date', y='value_numeric', 
                          markers=True, title='Mobile Money Penetration')
            fig.update_layout(height=350, showlegend=False)
            fig.update_traces(line=dict(color='#ff7f0e', width=3))
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent Events
        st.markdown("---")
        st.subheader("📋 Recent Events")
        events_display = events[['indicator', 'category', 'observation_date']].copy()
        events_display['date'] = pd.to_datetime(events_display['observation_date'])
        events_display = events_display.sort_values('date', ascending=False)
        st.dataframe(events_display.head(5), use_container_width=True)
    
    # ========== TRENDS PAGE ==========
    elif choice == "📈 Trends":
        st.markdown('<p class="main-header">📈 Trend Analysis</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Indicator selector
        indicators = observations['indicator_code'].unique()
        selected_indicators = st.multiselect(
            "Select indicators to display:",
            options=indicators,
            default=['ACC_OWNERSHIP', 'ACC_MM_ACCOUNT']
        )
        
        if selected_indicators:
            fig = go.Figure()
            
            for indicator in selected_indicators:
                data = observations[observations['indicator_code'] == indicator].copy()
                data['date'] = pd.to_datetime(data['observation_date'])
                data = data.sort_values('date')
                
                # Get indicator name
                indicator_name = data['indicator'].iloc[0] if len(data) > 0 else indicator
                
                fig.add_trace(go.Scatter(
                    x=data['date'],
                    y=data['value_numeric'],
                    mode='lines+markers',
                    name=indicator_name,
                    line=dict(width=3)
                ))
            
            fig.update_layout(
                title='Financial Inclusion Indicators Over Time',
                xaxis_title='Year',
                yaxis_title='Value',
                height=500,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show raw data
            with st.expander("View Data"):
                display_data = observations[observations['indicator_code'].isin(selected_indicators)]
                display_data = display_data[['indicator', 'value_numeric', 'observation_date', 'source_name']]
                st.dataframe(display_data, use_container_width=True)
        else:
            st.info("Please select at least one indicator")
        
        # Event Timeline overlay
        st.markdown("---")
        st.subheader("📅 Event Timeline Overlay")
        
        if st.checkbox("Show events on chart"):
            fig_events = go.Figure()
            
            # Add selected indicators
            for indicator in selected_indicators[:3]:  # Limit to 3 for clarity
                data = observations[observations['indicator_code'] == indicator].copy()
                data['date'] = pd.to_datetime(data['observation_date'])
                data = data.sort_values('date')
                
                if len(data) > 0:
                    fig_events.add_trace(go.Scatter(
                        x=data['date'],
                        y=data['value_numeric'],
                        mode='lines+markers',
                        name=data['indicator'].iloc[0],
                        line=dict(width=3)
                    ))
            
            # Add events as vertical lines
            for _, event in events.iterrows():
                event_date = pd.to_datetime(event['observation_date'])
                event_name = event['indicator']
                fig_events.add_vline(x=event_date, line_dash="dash", line_color="red", 
                                   annotation_text=event_name, annotation_position="top right")
            
            fig_events.update_layout(
                title='Indicators with Event Overlays',
                xaxis_title='Year',
                yaxis_title='Value',
                height=500
            )
            st.plotly_chart(fig_events, use_container_width=True)
    
    # ========== FORECASTS PAGE ==========
    elif choice == "🔮 Forecasts":
        st.markdown('<p class="main-header">🔮 Forecasts 2025-2027</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Scenario selector
        scenario = st.selectbox(
            "Select Scenario:",
            ['Base', 'Optimistic', 'Pessimistic']
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Account Ownership Forecast")
            
            # Get historical data
            acc_hist = observations[observations['indicator_code'] == 'ACC_OWNERSHIP'].copy()
            acc_hist['date'] = pd.to_datetime(acc_hist['observation_date'])
            acc_hist = acc_hist.sort_values('date')
            
            # Get forecast data
            forecast_data = forecasts[['Year', f'Account Ownership ({scenario})']].dropna()
            
            fig = go.Figure()
            
            # Historical
            fig.add_trace(go.Scatter(
                x=acc_hist['date'],
                y=acc_hist['value_numeric'],
                mode='lines+markers',
                name='Historical',
                line=dict(color='#1f77b4', width=3)
            ))
            
            # Forecast
            if not forecast_data.empty:
                fig.add_trace(go.Scatter(
                    x=forecast_data['Year'],
                    y=forecast_data[f'Account Ownership ({scenario})'],
                    mode='lines+markers',
                    name=f'{scenario} Forecast',
                    line=dict(color='#ff7f0e', width=3, dash='dash')
                ))
                
                # Add range (if we have multiple scenarios)
                if 'Account Ownership (Optimistic)' in forecasts.columns and 'Account Ownership (Pessimistic)' in forecasts.columns:
                    fig.add_trace(go.Scatter(
                        x=forecast_data['Year'].tolist() + forecast_data['Year'].tolist()[::-1],
                        y=forecasts[forecasts['Year'].isin(forecast_data['Year'])]['Account Ownership (Optimistic)'].tolist() + 
                          forecasts[forecasts['Year'].isin(forecast_data['Year'])]['Account Ownership (Pessimistic)'].tolist()[::-1],
                        fill='toself',
                        fillcolor='rgba(255, 165, 0, 0.2)',
                        line=dict(color='rgba(255,255,255,0)'),
                        name='Confidence Range'
                    ))
            
            fig.update_layout(
                title='Account Ownership Forecast',
                xaxis_title='Year',
                yaxis_title='Account Ownership (%)',
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 P2P Usage Forecast")
            
            # Get historical data
            p2p_hist = observations[observations['indicator_code'] == 'USG_P2P_COUNT'].copy()
            if len(p2p_hist) > 0:
                p2p_hist['date'] = pd.to_datetime(p2p_hist['observation_date'])
                p2p_hist = p2p_hist.sort_values('date')
                
                fig = go.Figure()
                
                # Historical
                fig.add_trace(go.Scatter(
                    x=p2p_hist['date'],
                    y=p2p_hist['value_numeric'] / 1e6,
                    mode='lines+markers',
                    name='Historical',
                    line=dict(color='#2ca02c', width=3)
                ))
                
                # Forecast
                if f'P2P Transactions ({scenario})' in forecasts.columns:
                    forecast_data = forecasts[['Year', f'P2P Transactions ({scenario})']].dropna()
                    
                    if not forecast_data.empty:
                        fig.add_trace(go.Scatter(
                            x=forecast_data['Year'],
                            y=forecast_data[f'P2P Transactions ({scenario})'],
                            mode='lines+markers',
                            name=f'{scenario} Forecast',
                            line=dict(color='#d62728', width=3, dash='dash')
                        ))
                        
                        # Add range
                        if 'P2P Transactions (Optimistic)' in forecasts.columns and 'P2P Transactions (Pessimistic)' in forecasts.columns:
                            fig.add_trace(go.Scatter(
                                x=forecast_data['Year'].tolist() + forecast_data['Year'].tolist()[::-1],
                                y=forecasts[forecasts['Year'].isin(forecast_data['Year'])]['P2P Transactions (Optimistic)'].tolist() + 
                                  forecasts[forecasts['Year'].isin(forecast_data['Year'])]['P2P Transactions (Pessimistic)'].tolist()[::-1],
                                fill='toself',
                                fillcolor='rgba(214, 39, 40, 0.2)',
                                line=dict(color='rgba(255,255,255,0)'),
                                name='Confidence Range'
                            ))
                
                fig.update_layout(
                    title='P2P Transactions Forecast',
                    xaxis_title='Year',
                    yaxis_title='P2P Transactions (Millions)',
                    height=400,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No P2P historical data available")
        
        # Progress toward targets
        st.markdown("---")
        st.subheader("🎯 Progress Toward Targets")
        
        if len(targets) > 0:
            target_data = targets[targets['indicator_code'] == 'ACC_OWNERSHIP']
            if len(target_data) > 0:
                target = target_data.iloc[0]['value_numeric']
                latest_acc = observations[observations['indicator_code'] == 'ACC_OWNERSHIP'].iloc[-1]['value_numeric']
                
                # Get 2027 forecast
                forecast_2027 = forecasts[forecasts['Year'] == 2027]
                if not forecast_2027.empty:
                    forecast_val = forecast_2027[f'Account Ownership ({scenario})'].iloc[0] if f'Account Ownership ({scenario})' in forecast_2027.columns else None
                else:
                    forecast_val = None
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Target", f"{target:.0f}%")
                
                with col2:
                    st.metric("Current", f"{latest_acc:.1f}%", 
                             delta=f"{latest_acc - target:.1f}% to target")
                
                with col3:
                    if forecast_val:
                        st.metric("2027 Forecast", f"{forecast_val:.1f}%",
                                 delta=f"{forecast_val - target:.1f}% to target")
        
        # Download forecast
        with st.expander("📥 Download Forecast Data"):
            st.dataframe(forecasts, use_container_width=True)
            csv = forecasts.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="financial_inclusion_forecast.csv",
                mime="text/csv"
            )
    
    # ========== IMPACT MATRIX ==========
    elif choice == "🎯 Impact Matrix":
        st.markdown('<p class="main-header">🎯 Event Impact Matrix</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("""
        This matrix shows the estimated impact of each event on key financial inclusion indicators.
        - **Positive values** = positive impact (increases inclusion)
        - **Negative values** = negative impact (may reduce inclusion)
        - **Higher magnitude** = stronger effect
        """)
        
        # Display matrix as heatmap
        fig = px.imshow(
            assoc_matrix,
            text_auto='.2f',
            aspect="auto",
            color_continuous_scale='RdBu_r',
            zmin=-0.1,
            zmax=0.1,
            title="Event-Indicator Association Matrix"
        )
        fig.update_layout(
            height=500,
            xaxis_title="Indicators",
            yaxis_title="Events"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show strongest impacts
        st.markdown("---")
        st.subheader("💪 Strongest Impacts")
        
        # Get non-zero impacts
        impact_list = []
        for event in assoc_matrix.index:
            for indicator in assoc_matrix.columns:
                val = assoc_matrix.loc[event, indicator]
                if val != 0:
                    impact_list.append({
                        'Event': event,
                        'Indicator': indicator,
                        'Impact': val
                    })
        
        if impact_list:
            impact_df = pd.DataFrame(impact_list)
            impact_df['Abs_Impact'] = abs(impact_df['Impact'])
            impact_df = impact_df.sort_values('Abs_Impact', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Top 5 Positive Impacts:**")
                positive = impact_df[impact_df['Impact'] > 0].head(5)
                for _, row in positive.iterrows():
                    st.write(f"✅ {row['Event']} → {row['Indicator']}: +{row['Impact']:.2f}")
            
            with col2:
                st.write("**Top Negative Impacts:**")
                negative = impact_df[impact_df['Impact'] < 0].head(5)
                for _, row in negative.iterrows():
                    st.write(f"❌ {row['Event']} → {row['Indicator']}: {row['Impact']:.2f}")
    
    # ========== DATA EXPLORER ==========
    elif choice == "📊 Data Explorer":
        st.markdown('<p class="main-header">📊 Data Explorer</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            record_type = st.selectbox(
                "Select Record Type:",
                ['All'] + list(df['record_type'].unique())
            )
        
        with col2:
            if 'pillar' in df.columns:
                pillar = st.selectbox(
                    "Select Pillar:",
                    ['All'] + [p for p in df['pillar'].unique() if pd.notna(p)]
                )
        
        # Filter data
        filtered_df = df.copy()
        if record_type != 'All':
            filtered_df = filtered_df[filtered_df['record_type'] == record_type]
        if pillar != 'All' and 'pillar' in df.columns:
            filtered_df = filtered_df[filtered_df['pillar'] == pillar]
        
        # Display data
        st.subheader(f"📋 Data ({len(filtered_df)} records)")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name="ethiopia_fi_data.csv",
            mime="text/csv"
        )

else:
    st.error("❌ Failed to load data. Please ensure all data files exist.")
    st.info("""
    **Required files:**
    - `data/processed/ethiopia_fi_enriched.csv`
    - `data/processed/association_matrix.csv`
    - `data/processed/forecast_summary.csv`
    """)

st.markdown("---")
st.caption("© 2026 Selam Analytics - Ethiopia Financial Inclusion Dashboard")