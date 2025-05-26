from typing import List, Dict, Any
from config.db_config import get_db_connection

class DatabaseOperationsBlindTest:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def get_blind_test_sessions(self) -> List[Dict]:
        """Get all blind test sessions"""
        try:
            self.cursor.execute("""
                SELECT id, parameters, created_at, mail
                FROM blind_test_session
                ORDER BY created_at DESC
            """)
            return [
                {
                    'id': row[0],
                    'parameters': row[1],
                    'created_at': row[2],
                    'mail': row[3]
                }
                for row in self.cursor.fetchall()
            ]
        except Exception as e:
            print(f"Error getting blind test sessions: {e}")
            return []

    def get_session_details(self, session_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific blind test session"""
        try:
            # Get session info
            self.cursor.execute("""
                SELECT id, parameters, created_at, mail
                FROM blind_test_session
                WHERE id = %s
            """, (session_id,))
            
            session_row = self.cursor.fetchone()
            if not session_row:
                return {}
                
            session_info = {
                'id': session_row[0],
                'parameters': session_row[1],
                'created_at': session_row[2],
                'mail': session_row[3]
            }
            
            # Get recommendations for this session
            self.cursor.execute("""
                SELECT 
                    algorithm_name, 
                    COUNT(*) as total_recommendations,
                    SUM(CASE WHEN is_selected = TRUE THEN 1 ELSE 0 END) as selected_count,
                    SUM(CASE WHEN bad_recommendation = TRUE THEN 1 ELSE 0 END) as bad_recommendations_count
                FROM blind_test_recommendations
                WHERE blind_test_session_id = %s
                GROUP BY algorithm_name
            """, (session_id,))
            
            algorithm_stats = []
            for row in self.cursor.fetchall():
                algorithm_name = row[0]
                total_recommendations = row[1]
                selected_count = row[2]
                bad_recommendations_count = row[3]
                selection_rate = (selected_count / total_recommendations) * 100 if total_recommendations > 0 else 0
                bad_recommendation_rate = (bad_recommendations_count / total_recommendations) * 100 if total_recommendations > 0 else 0
                
                algorithm_stats.append({
                    'algorithm_name': algorithm_name,
                    'total_recommendations': total_recommendations,
                    'selected_count': selected_count,
                    'selection_rate': selection_rate,
                    'bad_recommendations_count': bad_recommendations_count,
                    'bad_recommendation_rate': bad_recommendation_rate
                })
            
            # Get product details for recommendations
            self.cursor.execute("""
                SELECT 
                    btr.algorithm_name,
                    btr.is_selected,
                    btr.recommended_order,
                    btr.bad_recommendation,
                    p.id as product_id,
                    p.product_name,
                    p.price,
                    p.site
                FROM blind_test_recommendations btr
                JOIN product p ON btr.recommended_product_id = p.id
                WHERE btr.blind_test_session_id = %s
                ORDER BY btr.algorithm_name, btr.recommended_order
            """, (session_id,))
            
            recommendations = []
            for row in self.cursor.fetchall():
                recommendations.append({
                    'algorithm_name': row[0],
                    'is_selected': row[1],
                    'recommended_order': row[2],
                    'bad_recommendation': row[3],
                    'product_id': row[4],
                    'product_name': row[5],
                    'price': row[6],
                    'site': row[7]
                })
            
            return {
                'session_info': session_info,
                'algorithm_stats': algorithm_stats,
                'recommendations': recommendations
            }
        except Exception as e:
            print(f"Error getting session details: {e}")
            return {}

    def get_algorithm_performance_summary(self, email: str = None) -> List[Dict]:
        """Get overall performance summary of all algorithms across all sessions"""
        try:
            query = """
                SELECT 
                    btr.algorithm_name, 
                    COUNT(DISTINCT btr.blind_test_session_id) as total_sessions,
                    COUNT(*) as total_recommendations,
                    SUM(CASE WHEN btr.is_selected = TRUE THEN 1 ELSE 0 END) as selected_count,
                    SUM(CASE WHEN btr.bad_recommendation = TRUE THEN 1 ELSE 0 END) as bad_recommendations_count
                FROM blind_test_recommendations btr
            """
            
            params = []
            if email:
                query += """
                    JOIN blind_test_session bts ON btr.blind_test_session_id = bts.id
                    WHERE bts.mail = %s
                """
                params.append(email)
                
            query += """
                GROUP BY btr.algorithm_name
                ORDER BY SUM(CASE WHEN btr.is_selected = TRUE THEN 1 ELSE 0 END) DESC
            """
            
            self.cursor.execute(query, params)
            
            return [
                {
                    'algorithm_name': row[0],
                    'total_sessions': row[1],
                    'total_recommendations': row[2],
                    'selected_count': row[3],
                    'selection_rate': (row[3] / row[2]) * 100 if row[2] > 0 else 0,
                    'bad_recommendations_count': row[4],
                    'bad_recommendation_rate': (row[4] / row[2]) * 100 if row[2] > 0 else 0
                }
                for row in self.cursor.fetchall()
            ]
        except Exception as e:
            print(f"Error getting algorithm performance summary: {e}")
            return []

    def get_session_user_email(self, session_id: int) -> str:
        """Get the user email associated with a blind test session"""
        try:
            # Get the mail column from the blind_test_session table
            self.cursor.execute("""
                SELECT mail
                FROM blind_test_session
                WHERE id = %s
            """, (session_id,))
            
            row = self.cursor.fetchone()
            if row and row[0]:
                return row[0]
            
            return "Unknown user"
        except Exception as e:
            print(f"Error getting session user email: {e}")
            return "Unknown user"

    def get_all_recommendations(self, email: str = None) -> List[Dict]:
        """
        Get all recommendations for scoring algorithms.
        Optionally filter by user email.
        """
        try:
            query = """
                SELECT 
                    btr.algorithm_name,
                    btr.is_selected,
                    btr.recommended_order,
                    btr.bad_recommendation,
                    btr.recommended_product_id
                FROM blind_test_recommendations btr
            """
            
            params = []
            if email:
                query += """
                    JOIN blind_test_session bts ON btr.blind_test_session_id = bts.id
                    WHERE bts.mail = %s
                """
                params.append(email)
                
            query += """
                ORDER BY btr.algorithm_name, btr.recommended_order
            """
            
            self.cursor.execute(query, params)
            
            return [
                {
                    'algorithm_name': row[0],
                    'is_selected': row[1],
                    'recommended_order': row[2],
                    'bad_recommendation': row[3],
                    'product_id': row[4]
                }
                for row in self.cursor.fetchall()
            ]
        except Exception as e:
            print(f"Error getting all recommendations: {e}")
            return [] 