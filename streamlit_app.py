import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Add current directory to path for imports
sys.path.append('.')

from data_processor import DataProcessor
from match_predictor import MatchPredictor
from spor_toto_predictor import SporTotoPredictor

# Page config
st.set_page_config(
    page_title="🏆 Spor Toto Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1e88e5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .prediction-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1e88e5;
        margin: 1rem 0;
    }
    .value-bet {
        background-color: #e8f5e8;
        color: #2e7d32;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .confidence-high {
        color: #2e7d32;
        font-weight: bold;
    }
    .confidence-medium {
        color: #f57c00;
        font-weight: bold;
    }
    .confidence-low {
        color: #d32f2f;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_prediction_system():
    """Load the prediction system with caching"""
    try:
        # Initialize data processor
        processor = DataProcessor(data_path='csvs/')
        
        with st.spinner("Loading match data..."):
            processor.load_data()
            processor.clean_data()
        
        # Load predictor
        predictor = MatchPredictor()
        
        if os.path.exists('models/spor_toto_model_rf.joblib'):
            with st.spinner("Loading trained models..."):
                predictor.load_models('models/spor_toto_model')
        else:
            st.error("❌ No trained models found. Please run main.py first to train the models.")
            return None, None, None
        
        # Initialize Spor Toto predictor
        spor_toto = SporTotoPredictor(predictor, processor)
        
        return processor, predictor, spor_toto
    
    except Exception as e:
        st.error(f"Error loading prediction system: {e}")
        return None, None, None

def main():
    # Header
    st.markdown('<h1 class="main-header">🏆 Spor Toto Match Predictor</h1>', unsafe_allow_html=True)
    st.markdown("### 🎯 AI-Powered Football Match Predictions with Betting Odds Analysis")
    
    # Load system
    processor, predictor, spor_toto = load_prediction_system()
    
    if not all([processor, predictor, spor_toto]):
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("🎮 Prediction Settings")
        
        # Risk tolerance
        risk_level = st.selectbox(
            "🎲 Risk Tolerance",
            ["conservative", "medium", "aggressive"],
            index=1,
            help="Conservative: Higher confidence, safer picks\nMedium: Balanced approach\nAggressive: Higher risk, higher reward"
        )
        
        # League selection
        league_options = {
            "🇹🇷 Turkish Super League": "T1",
            "🇪🇸 Spanish La Liga": "SP1",
            "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League": "pl2425",
            "🇩🇪 German Bundesliga": "B1",
            "🇮🇹 Italian Serie A": "it2425",
            "🇫🇷 French Ligue 1": "F1",
            "🇵🇹 Portuguese Liga": "P1",
            "🇳🇱 Dutch Eredivisie": "N1",
            "🇬🇷 Greek Super League": "G1"
        }
        
        st.markdown("---")
        st.markdown("### 📊 Model Performance")
        
        # Show some stats about loaded data
        if hasattr(processor, 'df') and processor.df is not None:
            total_matches = len(processor.df)
            date_range = f"{processor.df['Date'].min().strftime('%Y-%m-%d')} to {processor.df['Date'].max().strftime('%Y-%m-%d')}"
            
            st.metric("Total Matches", f"{total_matches:,}")
            st.caption(f"Data Range: {date_range}")
            
            # League distribution
            league_counts = processor.df['League'].value_counts()
            st.caption("Leagues in Dataset:")
            for league, count in league_counts.head(5).items():
                st.caption(f"• {league}: {count:,} matches")
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["🔮 Single Match", "📝 Batch Prediction", "📊 Model Insights", "ℹ️ Help"])
    
    with tab1:
        st.header("🔮 Single Match Prediction")
        
        col1, col2 = st.columns(2)
        
        col1, col2 = st.columns(2)
        
        with col1:
            home_team = st.text_input("🏠 Home Team", placeholder="e.g., Galatasaray")
        
        with col2:
            away_team = st.text_input("🛣️ Away Team", placeholder="e.g., Fenerbahce")
        
        if st.button("🎯 Predict Match", type="primary"):
            if home_team and away_team:
                with st.spinner("Analyzing match..."):
                    # Prepare match data (use default league)
                    match_info = {
                        'home_team': home_team,
                        'away_team': away_team,
                        'league': "T1",  # Default to Turkish Super League
                        'date': datetime.now().strftime('%Y-%m-%d')
                    }
                    
                    # Get prediction
                    predictions = spor_toto.predict_matches([match_info], risk_level)
                    
                    if predictions:
                        prediction = predictions[0]
                        display_single_prediction(prediction)
                    else:
                        st.error("Could not generate prediction for this match.")
            else:
                st.warning("Please enter both team names.")
    
    with tab2:
        st.header("📝 Batch Match Prediction")
        
        # Upload CSV or manual entry
        upload_method = st.radio(
            "Choose input method:",
            ["📝 Manual Entry", "📄 Upload CSV"]
        )
        
        if upload_method == "📝 Manual Entry":
            st.subheader("Enter matches manually")
            
            # Dynamic match entry
            if 'matches' not in st.session_state:
                st.session_state.matches = []
            
            with st.form("add_match_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    new_home = st.text_input("Home Team")
                with col2:
                    new_away = st.text_input("Away Team")
                with col3:
                    st.write("") # Spacer
                    add_match = st.form_submit_button("➕ Add Match")
                
                if add_match and new_home and new_away:
                    st.session_state.matches.append({
                        'home_team': new_home,
                        'away_team': new_away,
                        'league': "T1"  # Default league
                    })
                    st.success(f"Added: {new_home} vs {new_away}")
            
            # Display current matches
            if st.session_state.matches:
                st.subheader(f"📋 Current Matches ({len(st.session_state.matches)})")
                
                for i, match in enumerate(st.session_state.matches):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"{i+1}. {match['home_team']} vs {match['away_team']}")
                    with col2:
                        if st.button("🗑️", key=f"remove_{i}"):
                            st.session_state.matches.pop(i)
                            st.rerun()
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔮 Predict All Matches", type="primary"):
                        predict_batch_matches(spor_toto, st.session_state.matches, risk_level)
                
                with col2:
                    if st.button("🗑️ Clear All"):
                        st.session_state.matches = []
                        st.rerun()
        
        else:  # CSV Upload
            st.subheader("Upload CSV file")
            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type="csv",
                help="CSV should have columns: home_team, away_team"
            )
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.dataframe(df.head())
                    
                    if st.button("🔮 Predict Uploaded Matches"):
                        matches = []
                        for _, row in df.iterrows():
                            match = {
                                'home_team': row['home_team'],
                                'away_team': row['away_team'],
                                'league': row.get('league', 'T1')
                            }
                            matches.append(match)
                        
                        predict_batch_matches(spor_toto, matches, risk_level)
                
                except Exception as e:
                    st.error(f"Error reading CSV: {e}")
    
    with tab3:
        st.header("📊 Model Insights")
        
        # Feature importance
        if hasattr(predictor, 'feature_importance') and predictor.feature_importance is not None:
            st.subheader("🎯 Feature Importance")
            
            fig = px.bar(
                predictor.feature_importance.head(10),
                x='avg_importance',
                y='feature',
                orientation='h',
                title="Top 10 Most Important Features"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Dataset statistics
        if hasattr(processor, 'df') and processor.df is not None:
            st.subheader("📈 Dataset Statistics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Outcome distribution
                outcome_counts = processor.df['FTR'].value_counts()
                outcome_labels = {'H': 'Home Win', 'D': 'Draw', 'A': 'Away Win'}
                
                fig = px.pie(
                    values=outcome_counts.values,
                    names=[outcome_labels.get(x, x) for x in outcome_counts.index],
                    title="Match Outcome Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # League distribution
                league_counts = processor.df['League'].value_counts().head(8)
                
                fig = px.bar(
                    x=league_counts.values,
                    y=league_counts.index,
                    orientation='h',
                    title="Matches by League"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.header("ℹ️ Help & Instructions")
        
        st.markdown("""
        ### 🚀 Quick Start Guide
        
        1. **Single Match Prediction**: Enter team names and get instant predictions
        2. **Batch Predictions**: Predict multiple matches at once
        3. **Risk Levels**: Choose your preferred risk tolerance
        
        ### 🎯 Understanding Predictions
        
        **Spor Toto Format**:
        - `m1(1)`: Strong home win prediction
        - `m2(X)`: Draw prediction
        - `m3(2)`: Away win prediction
        - `m4(1-X)`: Home win or draw
        - `m5(1-2)`: Avoid draw
        - `m6(X-2)`: Draw or away win
        
        **Confidence Levels**:
        - 🟢 **High (70%+)**: Strong single outcome prediction
        - 🟡 **Medium (50-70%)**: Two most likely outcomes
        - 🔴 **Low (<50%)**: Uncertain, broader prediction
        
        ### 🏆 AI-Powered Analysis
        
        The system uses machine learning to analyze:
        - Historical match patterns
        - Team performance statistics
        - Statistical indicators and trends
        - Advanced feature engineering
        
        ### ⚠️ Important Notes
        
        - Predictions are based on historical data and statistical models
        - Past performance does not guarantee future results
        - Always bet responsibly and within your means
        - Use predictions as guidance, not absolute truth
        """)

def display_single_prediction(prediction):
    """Display a single match prediction with formatting"""
    
    st.success(f"🎯 **{prediction['spor_toto_prediction']}**")
    
    # Confidence badge
    confidence = prediction['ml_prediction']['confidence']
    if confidence >= 70:
        confidence_class = "confidence-high"
        confidence_icon = "🟢"
    elif confidence >= 50:
        confidence_class = "confidence-medium"
        confidence_icon = "🟡"
    else:
        confidence_class = "confidence-low"
        confidence_icon = "🔴"
    
    st.markdown(f"{confidence_icon} **Confidence**: <span class='{confidence_class}'>{confidence:.1f}%</span>", 
                unsafe_allow_html=True)
    
    # Probabilities
    probs = prediction['ml_prediction']['probabilities']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏠 Home Win", f"{probs['home_win']:.1f}%")
    with col2:
        st.metric("🤝 Draw", f"{probs['draw']:.1f}%")
    with col3:
        st.metric("🛣️ Away Win", f"{probs['away_win']:.1f}%")
    
    # Probability chart
    fig = go.Figure(data=[
        go.Bar(
            x=['Home Win (1)', 'Draw (X)', 'Away Win (2)'],
            y=[probs['home_win'], probs['draw'], probs['away_win']],
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c']
        )
    ])
    fig.update_layout(
        title="Prediction Probabilities",
        yaxis_title="Probability (%)",
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Value analysis
    if prediction.get('value_analysis') and prediction['value_analysis'].get('good_bets'):
        st.markdown("### 💰 Value Betting Opportunities")
        
        for bet in prediction['value_analysis']['good_bets']:
            outcome_name = bet[0].replace('_', ' ').title()
            value = bet[1]
            confidence = bet[2]
            
            st.markdown(f"""
            <div class="value-bet">
                🎯 {outcome_name}: +{value:.1f}% value (Confidence: {confidence:.1f}%)
            </div>
            """, unsafe_allow_html=True)

def predict_batch_matches(spor_toto, matches, risk_level):
    """Predict batch of matches"""
    
    if not matches:
        st.warning("No matches to predict!")
        return
    
    with st.spinner(f"Predicting {len(matches)} matches..."):
        # Add date to matches
        for match in matches:
            if 'date' not in match:
                match['date'] = datetime.now().strftime('%Y-%m-%d')
        
        predictions = spor_toto.predict_matches(matches, risk_level)
    
    if predictions:
        st.success(f"✅ Generated predictions for {len(predictions)} matches!")
        
        # Summary table
        summary_data = []
        for pred in predictions:
            summary_data.append({
                'Match': f"{pred['home_team']} vs {pred['away_team']}",
                'Prediction': pred['spor_toto_prediction'],
                'Confidence': f"{pred['ml_prediction']['confidence']:.1f}%",
                'Home': f"{pred['ml_prediction']['probabilities']['home_win']:.1f}%",
                'Draw': f"{pred['ml_prediction']['probabilities']['draw']:.1f}%",
                'Away': f"{pred['ml_prediction']['probabilities']['away_win']:.1f}%"
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
        # Coupon format
        st.subheader("🎫 Spor Toto Coupon Format")
        coupon_text = "\n".join([pred['spor_toto_prediction'] for pred in predictions])
        st.code(coupon_text, language="text")
        
        # Statistics
        single_predictions = sum(1 for pred in predictions if '(' in pred['spor_toto_prediction'] and '-' not in pred['spor_toto_prediction'].split('(')[1])
        double_predictions = sum(1 for pred in predictions if pred['spor_toto_prediction'].count('-') == 1)
        triple_predictions = sum(1 for pred in predictions if pred['spor_toto_prediction'].count('-') == 2)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Single Outcomes", single_predictions)
        with col2:
            st.metric("Double Outcomes", double_predictions)
        with col3:
            st.metric("Triple Outcomes", triple_predictions)
        with col4:
            # Calculate combinations
            total_combinations = 1
            for pred in predictions:
                outcome_count = pred['spor_toto_prediction'].split('(')[1].count('-') + 1
                total_combinations *= outcome_count
            st.metric("Total Combinations", f"{total_combinations:,}")

if __name__ == "__main__":
    main()
