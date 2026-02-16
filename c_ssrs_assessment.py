"""
C-SSRS (Columbia-Suicide Severity Rating Scale) Assessment Module
Implements suicide risk assessment for Healing Space UK
"""

class CSSRSAssessment:
    """
    Columbia-Suicide Severity Rating Scale (C-SSRS) Assessment
    
    6-question core assessment for suicide risk evaluation
    Scoring: Each question 0-5 (0=No, 1=Rare, 2=Infrequent, 3=Frequent, 4=Very Frequent, 5=Frequent/Every Day)
    
    Risk Categories:
    - LOW (0-2): No or rare suicidal thoughts without intent/plan
    - HIGH (3-4): Frequent thoughts or plan/intent without frequency
    - CRITICAL (5+): Daily thoughts with intent + plan + behavior OR intent + plan + behavior present
    """
    
    # Question definitions
    QUESTIONS = [
        {
            "id": 1,
            "text": "Have you had any actual thoughts of killing yourself?",
            "category": "ideation",
            "weight": 1
        },
        {
            "id": 2,
            "text": "How many days in the past month have you had these thoughts?",
            "category": "frequency",
            "weight": 1
        },
        {
            "id": 3,
            "text": "How long do these thoughts typically last when you have them?",
            "category": "duration",
            "weight": 1
        },
        {
            "id": 4,
            "text": "Have you thought about how you might do this?",
            "category": "planning",
            "weight": 2
        },
        {
            "id": 5,
            "text": "Do you intend to act on these thoughts?",
            "category": "intent",
            "weight": 2
        },
        {
            "id": 6,
            "text": "Have you done anything to prepare to end your life?",
            "category": "behavior",
            "weight": 3
        }
    ]
    
    ANSWER_OPTIONS = {
        0: "No",
        1: "Rare (1 day/month)",
        2: "Infrequent (2-5 days/month)",
        3: "Frequent (6+ days/month)",
        4: "Almost every day",
        5: "Every day or multiple times daily"
    }
    
    @staticmethod
    def calculate_risk_score(responses):
        """
        Calculate risk score and level from C-SSRS responses
        
        Args:
            responses (dict): {question_id: score} mapping (0-5 for each)
        
        Returns:
            dict: {
                'total_score': int,
                'risk_level': str ('low', 'high', 'critical'),
                'risk_category_score': int,
                'has_planning': bool,
                'has_intent': bool,
                'has_behavior': bool,
                'reasoning': str
            }
        """
        
        # Validate responses
        if not responses or len(responses) != 6:
            raise ValueError("All 6 C-SSRS questions must be answered")
        
        # Extract specific responses
        ideation_score = responses.get(1, 0)  # Q1: Thoughts
        frequency_score = responses.get(2, 0)  # Q2: Frequency
        planning_score = responses.get(4, 0)   # Q4: Planning
        intent_score = responses.get(5, 0)     # Q5: Intent
        behavior_score = responses.get(6, 0)   # Q6: Behavior
        
        # Calculate composite scores
        has_planning = planning_score > 0
        has_intent = intent_score > 0
        has_behavior = behavior_score > 0
        
        # Determine risk level based on clinical algorithm
        # CRITICAL: Intent + Plan + Behavior (regardless of score) OR Score 5 with ideation
        if (has_intent and has_planning and has_behavior):
            risk_level = "critical"
            risk_category_score = 5
            reasoning = "Suicidal intent + planning + preparatory behavior"
        elif ideation_score == 5 and (has_planning or has_intent):
            risk_level = "critical"
            risk_category_score = 5
            reasoning = "Daily suicidal thoughts with intent and/or planning"
        # HIGH: Frequent thoughts (3-4) OR Planning/Intent present
        elif ideation_score >= 3 or (has_planning and has_intent):
            risk_level = "high"
            risk_category_score = 4
            reasoning = "Frequent suicidal thoughts and/or active planning/intent"
        # MEDIUM: Moderate frequency (1-2) with some concern
        elif ideation_score >= 1:
            risk_level = "moderate"
            risk_category_score = 2
            reasoning = "Rare to infrequent suicidal thoughts present"
        # LOW: No ideation
        else:
            risk_level = "low"
            risk_category_score = 0
            reasoning = "No suicidal ideation detected"
        
        # Total score (simple sum for tracking)
        total_score = sum(responses.values())
        
        return {
            "total_score": total_score,
            "risk_level": risk_level,
            "risk_category_score": risk_category_score,
            "has_planning": has_planning,
            "has_intent": has_intent,
            "has_behavior": has_behavior,
            "ideation_score": ideation_score,
            "frequency_score": frequency_score,
            "planning_score": planning_score,
            "intent_score": intent_score,
            "behavior_score": behavior_score,
            "reasoning": reasoning
        }
    
    @staticmethod
    def get_alert_threshold(risk_level):
        """
        Get alert configuration for risk level
        
        Returns:
            dict: {
                'should_alert': bool,
                'urgency': str ('immediate', 'urgent', 'routine', None),
                'response_time_minutes': int,
                'escalation_time_minutes': int,
                'requires_safety_plan': bool
            }
        """
        thresholds = {
            "critical": {
                "should_alert": True,
                "urgency": "immediate",
                "response_time_minutes": 10,
                "escalation_time_minutes": 10,
                "requires_safety_plan": True,
                "notify_channels": ["email", "sms", "in-app"],
                "escalation_contacts": ["primary_clinician", "supervisor", "on-call"]
            },
            "high": {
                "should_alert": True,
                "urgency": "urgent",
                "response_time_minutes": 30,
                "escalation_time_minutes": 60,
                "requires_safety_plan": True,
                "notify_channels": ["email", "in-app"],
                "escalation_contacts": ["primary_clinician", "supervisor"]
            },
            "moderate": {
                "should_alert": False,
                "urgency": "routine",
                "response_time_minutes": None,
                "escalation_time_minutes": None,
                "requires_safety_plan": False,
                "notify_channels": [],
                "escalation_contacts": []
            },
            "low": {
                "should_alert": False,
                "urgency": None,
                "response_time_minutes": None,
                "escalation_time_minutes": None,
                "requires_safety_plan": False,
                "notify_channels": [],
                "escalation_contacts": []
            }
        }
        
        return thresholds.get(risk_level, {
            "should_alert": False,
            "urgency": None,
            "requires_safety_plan": False
        })
    
    @staticmethod
    def format_for_clinician(assessment):
        """Format assessment for clinician review"""
        return {
            "assessment_id": assessment.get("id"),
            "patient": assessment.get("patient_username"),
            "risk_level": assessment.get("risk_level"),
            "risk_score": assessment.get("total_score"),
            "reasoning": assessment.get("reasoning"),
            "responses": assessment.get("responses"),
            "assessment_time": assessment.get("created_at"),
            "requires_immediate_action": assessment.get("risk_level") in ["critical", "high"],
            "safety_plan_required": assessment.get("risk_level") in ["critical", "high"]
        }
    
    @staticmethod
    def format_for_patient(assessment, risk_level_message=True):
        """Format assessment for patient feedback"""
        messages = {
            "critical": "⚠️ You may be at immediate risk of suicide. Please contact your clinician immediately or call 999 if in danger.",
            "high": "Your responses indicate elevated suicide risk. Your clinician will review this urgently.",
            "moderate": "Your responses show some concerns that your clinician should review.",
            "low": "Your responses don't indicate high suicide risk at this time."
        }
        
        return {
            "risk_level": assessment.get("risk_level"),
            "message": messages.get(assessment.get("risk_level"), "Assessment complete"),
            "next_steps": {
                "critical": [
                    "Contact your clinician immediately",
                    "Call Samaritans: 116 123",
                    "Call emergency: 999",
                    "You will need to complete a safety plan"
                ],
                "high": [
                    "Your clinician will contact you soon",
                    "You will need to complete a safety plan",
                    "Emergency: 999 if in immediate danger"
                ],
                "moderate": [
                    "Routine clinician follow-up",
                    "Emergency: 999 if in immediate danger"
                ],
                "low": [
                    "No immediate action needed",
                    "Emergency: 999 if in immediate danger"
                ]
            }.get(assessment.get("risk_level"), []),
            "emergency_contacts": {
                "samaritans": "116 123 (24/7, free)",
                "emergency": "999 (immediate danger)",
                "clinician": "[Clinician contact will be provided]"
            }
        }


class SafetyPlan:
    """Safety Planning for high-risk patients"""
    
    PLAN_SECTIONS = [
        {
            "id": "warning_signs",
            "title": "Warning Signs",
            "description": "What signs tell you that a crisis is developing?",
            "hint": "e.g., inability to sleep, increased substance use, social withdrawal"
        },
        {
            "id": "internal_coping",
            "title": "Internal Coping Strategies",
            "description": "What can you do on your own when you feel suicidal?",
            "hint": "e.g., distraction, mindfulness, exercise, journaling"
        },
        {
            "id": "distraction_people",
            "title": "People & Places for Distraction",
            "description": "Who and where can help distract you from suicidal thoughts?",
            "hint": "e.g., trusted friends, family, support groups, safe places"
        },
        {
            "id": "people_for_help",
            "title": "People to Contact for Help",
            "description": "Who can you call when in crisis?",
            "hint": "Include names, relationships, phone numbers"
        },
        {
            "id": "professionals",
            "title": "Professional Resources & Services",
            "description": "Emergency and professional contacts",
            "default": {
                "Samaritans": "116 123",
                "Emergency Services": "999",
                "Your Clinician": "[To be provided]"
            }
        },
        {
            "id": "means_safety",
            "title": "Making Your Environment Safer",
            "description": "Ways to make your environment safer right now",
            "hint": "e.g., secure medications, remove sharp objects, tell someone where you are"
        }
    ]
    
    @staticmethod
    def create_blank_plan(username):
        """Create blank safety plan template"""
        return {
            "username": username,
            "plan": {section["id"]: "" for section in SafetyPlan.PLAN_SECTIONS},
            "created_at": None,
            "last_reviewed": None,
            "clinician_reviewed": False
        }
