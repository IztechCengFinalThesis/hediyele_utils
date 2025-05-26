import streamlit as st
import pandas as pd
import altair as alt
import json
from db_operations.dbop_blind_test import DatabaseOperationsBlindTest

def calculate_algorithm_score(recommendations):
    """
    Calculate a score for an algorithm based on recommendation position
    and selection status. Bad recommendations are no longer considered.
    
    Score is from 0-100 where:
    - Selected recommendations in earlier positions contribute more points
    - Algorithms with higher selection rates generally score better
    
    Returns 0 if no recommendations exist.
    """
    if not recommendations:
        return 0
    
    total_recs = len(recommendations)
    if total_recs == 0:
        return 0
    
    # Filter out bad recommendations if they exist
    valid_recs = [r for r in recommendations if not r.get('bad_recommendation', False)]
    if not valid_recs:
        return 0
        
    total_recs = len(valid_recs)
    
    # Find the maximum order/position across all recommendations
    max_position = max([r['recommended_order'] or 0 for r in valid_recs], default=0) or 1
    
    # Base score starts at 0
    score = 0
    total_selected = sum(1 for r in valid_recs if r['is_selected'])
    
    # If nothing was selected, return a low base score
    if total_selected == 0:
        return 20
    
    # Calculate weighted position score for selected items
    # Earlier positions (lower numbers) are worth more
    position_scores = []
    for rec in valid_recs:
        if rec['is_selected']:
            position = rec['recommended_order'] or max_position
            
            # Position weight - first position is worth the most
            # Exponential decay for later positions (0.8^0=1, 0.8^1=0.8, 0.8^2=0.64, etc.)
            position_weight = 0.8 ** (position - 1)
            position_scores.append(position_weight)
    
    # Average position score (0-1 range)
    avg_position_score = sum(position_scores) / len(position_scores) if position_scores else 0
    
    # Selection rate as a percentage of total recommendations (0-1 range)
    selection_rate = total_selected / total_recs
    
    # Final score calculation with more weight to position
    # - 70% based on position scores (earlier = better)
    # - 30% based on selection rate (higher = better)
    final_score = (avg_position_score * 70) + (selection_rate * 30)
    
    # Ensure score is within 0-100 range
    return max(0, min(100, final_score))

def app():
    st.title("Blind Test Analysis")
    
    db_ops = DatabaseOperationsBlindTest()
    
    # Get list of users with test sessions
    unique_emails = set()
    sessions = db_ops.get_blind_test_sessions()
    for session in sessions:
        if session['mail']:
            unique_emails.add(session['mail'])
    
    # Email filter for algorithm performance
    email_filter = st.selectbox(
        "Filter by user email (optional):",
        options=["All Users"] + sorted(list(unique_emails))
    )
    
    selected_email = None if email_filter == "All Users" else email_filter
    
    # Get overall algorithm performance
    st.header("Algorithm Performance Summary")
    algorithm_summary = db_ops.get_algorithm_performance_summary(email=selected_email)
    
    if algorithm_summary:
        # Get all recommendations to calculate scores
        all_recs = db_ops.get_all_recommendations(email=selected_email)
        
        # Calculate scores for each algorithm
        algorithm_scores = {}
        if all_recs:
            for algorithm_name in set(rec['algorithm_name'] for rec in all_recs):
                algo_recs = [rec for rec in all_recs if rec['algorithm_name'] == algorithm_name]
                algorithm_scores[algorithm_name] = calculate_algorithm_score(algo_recs)
        
        summary_df = pd.DataFrame(algorithm_summary)
        
        # Add scores to the summary dataframe
        summary_df['score'] = summary_df['algorithm_name'].map(
            lambda x: algorithm_scores.get(x, 0)
        ).round(1)
        
        # Format the selection rate column
        summary_df['selection_rate'] = summary_df['selection_rate'].round(2).astype(str) + '%'
        
        # Rename columns for display
        summary_df = summary_df.rename(columns={
            'algorithm_name': 'Algorithm',
            'total_sessions': 'Sessions',
            'total_recommendations': 'Total Recommendations',
            'selected_count': 'Selected Count',
            'selection_rate': 'Selection Rate',
            'score': 'Algorithm Score (0-100)'
        })
        
        # Sort by score in descending order
        summary_df = summary_df.sort_values('Algorithm Score (0-100)', ascending=False)
        
        st.dataframe(summary_df, use_container_width=True)
        
        # Create charts for algorithm performance metrics
        chart_data = pd.DataFrame({
            'Algorithm': [row['algorithm_name'] for row in algorithm_summary],
            'Selection Rate (%)': [row['selection_rate'] for row in algorithm_summary],
            'Algorithm Score': [algorithm_scores.get(row['algorithm_name'], 0) for row in algorithm_summary]
        })
        
        # Create columns for the charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Algorithm Score")
            chart_score = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('Algorithm:N', sort='-y'),
                y=alt.Y('Algorithm Score:Q'),
                color=alt.Color('Algorithm:N', legend=None),
                tooltip=['Algorithm', 'Algorithm Score']
            ).properties(
                height=400
            )
            st.altair_chart(chart_score, use_container_width=True)
        
        with col2:
            st.subheader("Selection Rate")
            chart1 = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('Algorithm:N', sort='-y'),
                y=alt.Y('Selection Rate (%):Q'),
                color=alt.Color('Algorithm:N', legend=None),
                tooltip=['Algorithm', 'Selection Rate (%)']
            ).properties(
                height=400
            )
            st.altair_chart(chart1, use_container_width=True)
    else:
        st.info("No algorithm performance data found.")
    
    # Get session list
    st.header("Blind Test Sessions")
    sessions = db_ops.get_blind_test_sessions()
    
    if not sessions:
        st.info("No blind test sessions found.")
        db_ops.close()
        return
    
    # Create a dropdown to select a session with user email
    session_options = {}
    for session in sessions:
        session_id = session['id']
        user_email = session['mail'] if session['mail'] else "Unknown user"
        session_options[f"Session {session_id} - {session['created_at']} - {user_email}"] = session_id
    
    selected_session_label = st.selectbox(
        "Select a blind test session to view details:",
        options=list(session_options.keys())
    )
    
    if selected_session_label:
        selected_session_id = session_options[selected_session_label]
        session_details = db_ops.get_session_details(selected_session_id)
        
        if session_details:
            # Session parameters
            st.subheader("Session Parameters")
            
            # Display the user email if available
            if session_details['session_info']['mail']:
                st.info(f"User email: {session_details['session_info']['mail']}")
            
            if session_details['session_info']['parameters']:
                try:
                    parameters = session_details['session_info']['parameters']
                    if isinstance(parameters, str):
                        parameters = json.loads(parameters)
                    
                    param_df = pd.DataFrame({"Parameter": parameters.keys(), "Value": parameters.values()})
                    st.dataframe(param_df, use_container_width=True)
                except:
                    st.json(session_details['session_info']['parameters'])
            else:
                st.info("No parameters found for this session.")
            
            # Algorithm performance for this session
            st.subheader("Algorithm Performance in This Session")
            if session_details['algorithm_stats']:
                algo_stats_df = pd.DataFrame(session_details['algorithm_stats'])
                
                # Calculate scores for each algorithm in this session
                algo_scores = {}
                for algorithm_name in set(rec['algorithm_name'] for rec in session_details['recommendations']):
                    algo_recs = [rec for rec in session_details['recommendations'] if rec['algorithm_name'] == algorithm_name]
                    algo_scores[algorithm_name] = calculate_algorithm_score(algo_recs)
                
                # Add scores to the dataframe
                algo_stats_df['score'] = algo_stats_df['algorithm_name'].map(
                    lambda x: algo_scores.get(x, 0)
                ).round(1)
                
                algo_stats_df['selection_rate'] = algo_stats_df['selection_rate'].round(2).astype(str) + '%'
                
                algo_stats_df = algo_stats_df.rename(columns={
                    'algorithm_name': 'Algorithm',
                    'total_recommendations': 'Total Recommendations',
                    'selected_count': 'Selected Count',
                    'selection_rate': 'Selection Rate',
                    'score': 'Algorithm Score (0-100)'
                })
                
                # Sort by score in descending order
                algo_stats_df = algo_stats_df.sort_values('Algorithm Score (0-100)', ascending=False)
                
                st.dataframe(algo_stats_df, use_container_width=True)
                
                # Create charts
                chart_data = pd.DataFrame({
                    'Algorithm': [row['algorithm_name'] for row in session_details['algorithm_stats']],
                    'Selection Rate (%)': [row['selection_rate'] for row in session_details['algorithm_stats']],
                    'Algorithm Score': [algo_scores.get(row['algorithm_name'], 0) for row in session_details['algorithm_stats']]
                })
                
            else:
                st.info("No algorithm statistics found for this session.")
            
            # Detailed recommendations
            st.subheader("Recommendations Details")
            if session_details['recommendations']:
                # Create a DataFrame for all recommendations
                recs_df = pd.DataFrame(session_details['recommendations'])
                
                # Calculate metrics by algorithm and selection status
                metrics_df = recs_df.groupby(['algorithm_name', 'is_selected']).size().unstack(fill_value=0)
                if True in metrics_df.columns:
                    metrics_df['total'] = metrics_df.sum(axis=1)
                    metrics_df['selection_rate'] = (metrics_df[True] / metrics_df['total'] * 100).round(2).astype(str) + '%'
                    metrics_df = metrics_df.reset_index()
                    metrics_df = metrics_df.rename(columns={
                        'algorithm_name': 'Algorithm',
                        True: 'Selected',
                        False: 'Not Selected',
                        'total': 'Total',
                        'selection_rate': 'Selection Rate'
                    })
                    st.dataframe(metrics_df, use_container_width=True)
                
                # Show all recommendations
                st.subheader("All Recommendations")
                recs_df = recs_df.rename(columns={
                    'algorithm_name': 'Algorithm',
                    'is_selected': 'Selected',
                    'recommended_order': 'Order',
                    'bad_recommendation': 'Bad Recommendation',
                    'product_id': 'Product ID',
                    'product_name': 'Product Name',
                    'price': 'Price',
                    'site': 'Site'
                })
                
                # Create tabs for different views
                tab1, tab2, tab3 = st.tabs(["All Recommendations", "Selected Only", "Bad Recommendations"])
                
                with tab1:
                    st.dataframe(recs_df, use_container_width=True)
                
                with tab2:
                    selected_df = recs_df[recs_df['Selected'] == True]
                    if not selected_df.empty:
                        st.dataframe(selected_df, use_container_width=True)
                    else:
                        st.info("No selected recommendations found.")
                
                with tab3:
                    bad_recs_df = recs_df[recs_df['Bad Recommendation'] == True]
                    if not bad_recs_df.empty:
                        st.dataframe(bad_recs_df, use_container_width=True)
                    else:
                        st.info("No bad recommendations found.")
            else:
                st.info("No recommendations found for this session.")
        else:
            st.error("Failed to retrieve session details.")
    
    db_ops.close() 