"""
CBT Tools Routes - PostgreSQL Backend

API endpoints for Cognitive Behavioral Therapy tools.
Routes use PostgreSQL and proper Flask conventions.
"""

from flask import Blueprint, request, jsonify, session
from .models import init_cbt_tools_schema, get_db_connection
import json

cbt_tools_bp = Blueprint('cbt_tools', __name__)


@cbt_tools_bp.route('/api/cbt-tools/save', methods=['POST'])
def save_cbt_tool():
    """Save a CBT tool entry"""
    # Validate session
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Validate input
    data = request.json
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    
    tool_type = data.get('tool_type')
    if not tool_type:
        return jsonify({'error': 'tool_type required'}), 400
    
    entry_data = json.dumps(data.get('data', {}))
    mood_rating = data.get('mood_rating')
    notes = data.get('notes', '')
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO cbt_tool_entries (username, tool_type, data, mood_rating, notes)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (username, tool_type, entry_data, mood_rating, notes))
        
        entry_id = cur.fetchone()[0]
        conn.commit()
        
        return jsonify({'success': True, 'id': entry_id}), 201
    except Exception as e:
        return jsonify({'error': f'Failed to save CBT tool entry: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()


@cbt_tools_bp.route('/api/cbt-tools/load', methods=['GET'])
def load_cbt_tool():
    """Load the most recent CBT tool entry"""
    # Validate session
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Validate input
    tool_type = request.args.get('tool_type')
    if not tool_type:
        return jsonify({'error': 'tool_type query parameter required'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, data, mood_rating, notes, created_at, updated_at
            FROM cbt_tool_entries
            WHERE username=%s AND tool_type=%s
            ORDER BY updated_at DESC
            LIMIT 1
        """, (username, tool_type))
        
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            return jsonify({
                'id': row[0],
                'data': json.loads(row[1]),
                'mood_rating': row[2],
                'notes': row[3],
                'created_at': row[4].isoformat() if row[4] else None,
                'updated_at': row[5].isoformat() if row[5] else None
            }), 200
        else:
            return jsonify({'data': None}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to load CBT tool entry: {str(e)}'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@cbt_tools_bp.route('/api/cbt-tools/list', methods=['GET'])
def list_cbt_tools():
    """List all CBT tool entries for authenticated user"""
    # Validate session
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get pagination params
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    tool_type = request.args.get('tool_type')  # Optional filter
    
    # Validate pagination
    if limit < 1 or limit > 100:
        limit = 20
    if offset < 0:
        offset = 0
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Build query based on filters
        if tool_type:
            cur.execute("""
                SELECT id, tool_type, mood_rating, notes, created_at, updated_at
                FROM cbt_tool_entries
                WHERE username=%s AND tool_type=%s
                ORDER BY updated_at DESC
                LIMIT %s OFFSET %s
            """, (username, tool_type, limit, offset))
        else:
            cur.execute("""
                SELECT id, tool_type, mood_rating, notes, created_at, updated_at
                FROM cbt_tool_entries
                WHERE username=%s
                ORDER BY updated_at DESC
                LIMIT %s OFFSET %s
            """, (username, limit, offset))
        
        rows = cur.fetchall()
        
        entries = [
            {
                'id': row[0],
                'tool_type': row[1],
                'mood_rating': row[2],
                'notes': row[3],
                'created_at': row[4].isoformat() if row[4] else None,
                'updated_at': row[5].isoformat() if row[5] else None
            }
            for row in rows
        ]
        
        cur.close()
        conn.close()
        
        return jsonify({'entries': entries, 'limit': limit, 'offset': offset}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to list CBT tools: {str(e)}'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@cbt_tools_bp.route('/api/cbt-tools/<int:entry_id>', methods=['DELETE'])
def delete_cbt_tool(entry_id):
    """Delete a CBT tool entry (soft delete recommended in production)"""
    # Validate session
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify ownership before deletion
        cur.execute(
            "SELECT id FROM cbt_tool_entries WHERE id=%s AND username=%s",
            (entry_id, username)
        )
        
        if not cur.fetchone():
            return jsonify({'error': 'Entry not found'}), 404
        
        # Delete entry
        cur.execute("DELETE FROM cbt_tool_entries WHERE id=%s", (entry_id,))
        conn.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to delete CBT tool: {str(e)}'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
