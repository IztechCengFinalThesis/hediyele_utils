import streamlit as st
import pandas as pd
import altair as alt
import json
from db_operations.dbop_blind_test import DatabaseOperationsBlindTest

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
        summary_df = pd.DataFrame(algorithm_summary)
        
        # Format the selection rate column
        summary_df['selection_rate'] = summary_df['selection_rate'].round(2).astype(str) + '%'
        summary_df['bad_recommendation_rate'] = summary_df['bad_recommendation_rate'].round(2).astype(str) + '%'
        
        # Rename columns for display
        summary_df = summary_df.rename(columns={
            'algorithm_name': 'Algorithm',
            'total_sessions': 'Sessions',
            'total_recommendations': 'Total Recommendations',
            'selected_count': 'Selected Count',
            'selection_rate': 'Selection Rate',
            'bad_recommendations_count': 'Bad Recommendations',
            'bad_recommendation_rate': 'Bad Recommendation Rate'
        })
        
        st.dataframe(summary_df, use_container_width=True)
        
        # Create a bar chart for selection rate
        chart_data = pd.DataFrame({
            'Algorithm': [row['algorithm_name'] for row in algorithm_summary],
            'Selection Rate (%)': [row['selection_rate'] for row in algorithm_summary],
            'Bad Recommendation Rate (%)': [row['bad_recommendation_rate'] for row in algorithm_summary]
        })
        
        # Create two columns for the charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Selection Rate by Algorithm")
            chart1 = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('Algorithm:N', sort='-y'),
                y=alt.Y('Selection Rate (%):Q'),
                color=alt.Color('Algorithm:N', legend=None),
                tooltip=['Algorithm', 'Selection Rate (%)']
            ).properties(
                height=400
            )
            st.altair_chart(chart1, use_container_width=True)
        
        with col2:
            st.subheader("Bad Recommendation Rate by Algorithm")
            chart2 = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('Algorithm:N', sort='-y'),
                y=alt.Y('Bad Recommendation Rate (%):Q'),
                color=alt.Color('Algorithm:N', legend=None),
                tooltip=['Algorithm', 'Bad Recommendation Rate (%)']
            ).properties(
                height=400
            )
            st.altair_chart(chart2, use_container_width=True)
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
                algo_stats_df['selection_rate'] = algo_stats_df['selection_rate'].round(2).astype(str) + '%'
                algo_stats_df['bad_recommendation_rate'] = algo_stats_df['bad_recommendation_rate'].round(2).astype(str) + '%'
                
                algo_stats_df = algo_stats_df.rename(columns={
                    'algorithm_name': 'Algorithm',
                    'total_recommendations': 'Total Recommendations',
                    'selected_count': 'Selected Count',
                    'selection_rate': 'Selection Rate',
                    'bad_recommendations_count': 'Bad Recommendations',
                    'bad_recommendation_rate': 'Bad Recommendation Rate'
                })
                
                st.dataframe(algo_stats_df, use_container_width=True)
                
                # Create a comparison chart
                chart_data = pd.DataFrame({
                    'Algorithm': [row['algorithm_name'] for row in session_details['algorithm_stats']],
                    'Selection Rate (%)': [row['selection_rate'] for row in session_details['algorithm_stats']],
                    'Bad Recommendation Rate (%)': [row['bad_recommendation_rate'] for row in session_details['algorithm_stats']]
                })
                
                # Create two columns for the charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Selection Rate")
                    chart1 = alt.Chart(chart_data).mark_bar().encode(
                        x=alt.X('Algorithm:N', sort='-y'),
                        y=alt.Y('Selection Rate (%):Q'),
                        color=alt.Color('Algorithm:N', legend=None),
                        tooltip=['Algorithm', 'Selection Rate (%)']
                    ).properties(
                        height=300
                    )
                    st.altair_chart(chart1, use_container_width=True)
                
                with col2:
                    st.subheader("Bad Recommendation Rate")
                    chart2 = alt.Chart(chart_data).mark_bar().encode(
                        x=alt.X('Algorithm:N', sort='-y'),
                        y=alt.Y('Bad Recommendation Rate (%):Q'),
                        color=alt.Color('Algorithm:N', legend=None),
                        tooltip=['Algorithm', 'Bad Recommendation Rate (%)']
                    ).properties(
                        height=300
                    )
                    st.altair_chart(chart2, use_container_width=True)
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