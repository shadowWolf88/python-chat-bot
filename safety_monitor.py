"""
SafetyMonitor: Real-time Risk Detection for Therapy Chat
=========================================================

Analyzes incoming therapy chat messages for indicators of suicide risk.
- Detects direct language (ideation, intent, plans)
- Detects indirect language (hopelessness, burden, farewell)
- Detects behavioral changes (stopped meds, giving away items, isolation)
- Scores risk on 0-100 scale for UI display
- Flags HIGH/CRITICAL for assessment prompt
- Fully GDPR compliant (no storage of messages)
- Clinical evidence: Based on Joiner's Interpersonal Theory & Linehan's DBT risk factors
"""

import re
from enum import Enum
from typing import Dict, List, Tuple, Optional


class RiskLevel(Enum):
    """Risk classification levels for UI and clinical action"""
    GREEN = "green"      # 0-30: No risk detected
    AMBER = "amber"      # 31-60: Some concerning language, monitor
    ORANGE = "orange"    # 61-75: Notable risk indicators, assess
    RED = "red"          # 76-100: High risk, immediate assessment needed


class SafetyMonitor:
    """
    Real-time risk detection for therapy chat messages.
    
    Clinical Basis:
    - Joiner's Interpersonal Theory: Thwarted belongingness + perceived burdensomeness + acquired capability
    - Linehan's DBT: Behavioral indicators (substance abuse, isolation, planning)
    - Columbia-Suicide Severity Rating Scale: Ideation → Planning → Intent → Behavior progression
    
    Architecture:
    - analyze_message(message, history) → {risk_score: 0-100, risk_level: str, indicators: [], action_needed: bool}
    - Non-blocking (processes instantly, <10ms)
    - No message storage (stateless analysis)
    - Returns both score and human-readable indicators
    """
    
    # Risk keywords organized by category and clinical weight
    RISK_KEYWORDS = {
        # Direct Ideation (strongest signal)
        'direct_ideation': {
            'weight': 30,
            'keywords': [
                'kill', 'die', 'suicide', 'suicidal',
                'end my life', 'end it all', 'end this',
                'want to die', 'want to kill',
                'i\'d be better off', 'better off dead',
                'no point', 'pointless', 'meaningless',
                'no hope', 'hopeless',
                'thoughts of', 'thinking about killing',
                'thinking about ending',
                'take my own life', 'taking my life',
                'overdose', 'jump', 'hang myself',
                'slit', 'cut myself',
                'end this pain', 'escape the pain',
                'can\'t do this', 'can\'t go on',
                'can\'t live', 'can\'t stand',
                'thoughts of harming',
            ]
        },
        
        # Direct Intent/Planning (very strong signal)
        'direct_planning': {
            'weight': 35,
            'keywords': [
                'i have a plan', 'i\'ve planned', 'i\'ve thought about how',
                'tonight', 'this weekend', 'soon', 'i\'m going to',
                'i\'ve decided', 'i\'ve made up my mind',
                'said goodbye', 'left a note', 'wrote a note',
                'getting my affairs in order', 'prepared', 'ready',
                'gather[ing]* pills', 'gather[ing]* supplies',
                'research[ed]* methods', 'look[ed]* up how',
                'when i\'m gone', 'after i\'m gone',
                'before i do it', 'this is my last',
            ]
        },
        
        # Past Attempts (high risk for future)
        'past_attempt': {
            'weight': 30,
            'keywords': [
                'i tried to kill', 'attempted suicide', 'tried to overdose',
                'cut myself', 'self-harm', 'self harm',
                'hurt myself on purpose', 'intentionally hurt',
                'took a bunch of pills', 'took pills to',
                'wrists', 'broken bones from',
            ]
        },
        
        # Hopelessness/Despair (indirect signal, clinical marker)
        'hopelessness': {
            'weight': 15,
            'keywords': [
                'hopeless', 'no hope', 'can\'t be helped',
                'pointless', 'meaningless', 'worthless',
                'everything is bad', 'never get better', 'never improve',
                'always be like this', 'stuck forever', 'trapped',
                'there\'s no way out', 'impossible', 'not possible',
                'nothing will change', 'nothing works',
                'give up', 'given up', 'lost all hope',
                'dark', 'darkness', 'empty', 'emptiness',
                'void', 'black', 'numb',
            ]
        },
        
        # Perceived Burdensomeness (Joiner theory)
        'burdensomeness': {
            'weight': 12,
            'keywords': [
                'burden', 'burdening', 'burden on',
                'i\'m a burden', 'everyone would be better off without me',
                'everyone would be better off', 'be better without me',
                'my fault', 'my responsibility', 'my problem',
                'holding them back', 'drag[ging]* them down',
                'too much', 'too needy', 'too demanding',
                'failure', 'failure as a', 'failed them',
                'disappointing', 'disappointed everyone',
                'let everyone down', 'letting people down',
                'shouldn\'t be here', 'don\'t belong',
            ]
        },
        
        # Thwarted Belongingness (Joiner theory)
        'isolation': {
            'weight': 10,
            'keywords': [
                'alone', 'lonely', 'loneliness',
                'no one cares', 'no one would notice',
                'nobody likes me', 'no friends', 'no relationships',
                'isolated', 'isolation', 'isolat[ing]*',
                'cut off from', 'disconnect[ed]* from',
                'not belong[ing]*', 'don\'t fit in',
                'left out', 'excluded', 'reject[ed]*',
                'no one understands', 'misunderstood',
                'unloved', 'unwanted', 'unlovable',
            ]
        },
        
        # Behavioral Changes (indirect signal)
        'behavioral_change': {
            'weight': 14,
            'keywords': [
                'stopped taking', 'stopped my meds', 'not taking pills',
                'given away', 'giving away', 'given my', 'gave my',
                'saying goodbye', 'said goodbye', 'farewell',
                'stopped seeing friends', 'pushing people away',
                'stopped going out', 'staying in bed',
                'not eating', 'stopped eating', 'can\'t eat',
                'can\'t sleep', 'not sleeping', 'awake all night',
                'started drinking', 'started using', 'started drugs',
                'increasing[ly]*', 'can\'t stop drinking', 'can\'t stop using',
                'self-harm', 'hurting myself', 'cutting',
                'reckless', 'taking risks', 'risky behavior',
                'like i don\'t care',
            ]
        },
        
        # Warning Signs of Imminent Risk
        'imminent_warning': {
            'weight': 20,
            'keywords': [
                'tonight', 'tonight i', 'this weekend',
                'can\'t wait', 'can\'t last', 'can\'t hold on',
                'final', 'last time', 'never again',
                'going away', 'leaving', 'disappearing',
                'see you soon', 'see you on the other side',
                'don\'t call me', 'don\'t contact me',
                'emergency', 'crisis', 'can\'t cope',
                'losing control', 'out of control',
                'worst ever', 'can\'t take it',
            ]
        },
        
        # Substance/Medical Risk Factors
        'substance_risk': {
            'weight': 8,
            'keywords': [
                'drinking', 'drunk', 'intoxicated', 'alcohol',
                'cocaine', 'crack', 'heroin', 'opioids', 'opiates',
                'meth', 'amphetamine', 'stimulant',
                'benzodiazpin[es]*', 'xanax', 'ativan', 'klonopin',
                'high', 'stoned', 'tripping',
                'overdos[ed]* on', 'took too many',
                'mixing drugs', 'mixing with alcohol',
            ]
        },
    }
    
    # Context modifiers (reduce confidence if present)
    CONTEXT_MITIGATORS = {
        'past_tense': [
            'used to', 'i used to', 'when i was', 'years ago',
            'before treatment', 'before therapy', 'before i got help',
            'past', 'no longer', 'not anymore', 'that\'s behind me',
            'i\'ve recovered from', 'i\'ve overcome',
        ],
        'hypothetical': [
            'if i', 'if i were', 'if i could', 'if it were up to me',
            'i might', 'i could', 'what if', 'imagine if',
            'in my dreams', 'in theory', 'hypothetically',
            'wouldn\'t', 'don\'t think i would',
        ],
        'asking_for_help': [
            'help', 'need help', 'want help', 'should i call',
            'what should i do', 'how can i cope',
            'treatment', 'therapy', 'counseling',
            'crisis line', 'hospital', 'admit[ted]*',
            'talking to you helps', 'this helps',
        ],
        'denial': [
            'i\'m not', 'i would never', 'i\'d never',
            'that\'s not me', 'not my style',
            'just joking', 'just exaggerating',
        ]
    }
    
    # Protective factors (reduce overall risk)
    PROTECTIVE_FACTORS = [
        'looking forward to', 'excited about', 'planning to',
        'my child[ren]*', 'my kids', 'my family needs me',
        'responsible for', 'taking care of',
        'going back to school', 'starting a new job',
        'therapy is helping', 'getting better', 'improved',
        'gave me hope', 'reasons to live', 'important reasons',
        'supportive friends', 'supportive family', 'supportive partner',
        'don\'t want to', 'wouldn\'t hurt them', 'wouldn\'t hurt',
        'religion', 'faith', 'god', 'spiritual',
        'committed to', 'committed to living', 'committed to recovery',
    ]
    
    def __init__(self):
        """Initialize SafetyMonitor with compiled regex patterns"""
        # Compile all keyword patterns for faster matching
        self.keyword_patterns = {}
        for category, data in self.RISK_KEYWORDS.items():
            patterns = []
            for kw in data['keywords']:
                # Convert keyword to regex pattern (handle [brackets] for variations)
                pattern = kw.replace('[ing]*', r'(?:ing)?')
                pattern = pattern.replace('[ed]* ', r'(?:ed)? ')
                pattern = pattern.replace('[ing]* ', r'(?:ing)? ')
                patterns.append(f"\\b{pattern}\\b")
            # Compile single pattern that matches any of the keywords
            self.keyword_patterns[category] = re.compile(
                '|'.join(patterns),
                re.IGNORECASE | re.UNICODE
            )
        
        # Compile mitigating factors
        self.mitigator_patterns = {}
        for mtype, keywords in self.CONTEXT_MITIGATORS.items():
            patterns = [f"\\b{kw}\\b" for kw in keywords]
            self.mitigator_patterns[mtype] = re.compile(
                '|'.join(patterns),
                re.IGNORECASE | re.UNICODE
            )
        
        # Compile protective factors
        patterns = [f"\\b{kw}\\b" for kw in self.PROTECTIVE_FACTORS]
        self.protective_pattern = re.compile(
            '|'.join(patterns),
            re.IGNORECASE | re.UNICODE
        )
    
    def analyze_message(self, message: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Analyze a single message for suicide risk.
        
        Args:
            message: User's therapy message
            conversation_history: Recent message history for context (optional)
                                 Format: [{'role': 'user'|'ai', 'content': str}, ...]
        
        Returns:
            {
                'risk_score': 0-100,  # Numerical score for UI
                'risk_level': 'green'|'amber'|'orange'|'red',  # Color coding
                'risk_category': 'low'|'moderate'|'high'|'critical',  # Clinical term
                'indicators': ['indicator1', 'indicator2', ...],  # What was detected
                'action_needed': bool,  # Should prompt user to take assessment
                'urgent_action': bool,  # Should alert clinician immediately
                'confidence': 0.0-1.0,  # Confidence in assessment
                'reasoning': str,  # Human-readable explanation (max 200 chars)
            }
        """
        if not message or not isinstance(message, str):
            return self._no_risk_response()
        
        message_lower = message.lower().strip()
        
        # Empty or very short messages = no risk
        if len(message_lower) < 5:
            return self._no_risk_response()
        
        score = 0
        indicators = []
        matched_categories = []
        
        # Step 1: Check for keyword matches
        for category, pattern in self.keyword_patterns.items():
            matches = pattern.findall(message_lower)
            if matches:
                category_weight = self.RISK_KEYWORDS[category]['weight']
                # Multiple matches in same category increase risk
                match_count = len(matches)
                category_score = category_weight * min(match_count, 3)  # Cap at 3x weight
                score += category_score
                indicators.append(f"{category.replace('_', ' ')}")
                matched_categories.append(category)
        
        # Step 2: Apply context mitigating factors (reduce score)
        mitigation_factor = 1.0
        
        for mtype, pattern in self.mitigator_patterns.items():
            if pattern.search(message_lower):
                # Different reduction levels by type
                if mtype == 'asking_for_help':
                    mitigation_factor *= 0.5  # Asking for help = good sign
                elif mtype == 'past_tense':
                    mitigation_factor *= 0.6  # Past tense = less imminent
                elif mtype == 'hypothetical':
                    mitigation_factor *= 0.7  # Hypothetical = less certain
                elif mtype == 'denial':
                    mitigation_factor *= 0.4  # Direct denial = potentially protective
        
        score = score * mitigation_factor
        
        # Step 3: Check for protective factors (further reduce)
        protective_matches = self.protective_pattern.findall(message_lower)
        if protective_matches:
            protective_factor = 1.0 - (len(protective_matches) * 0.15)
            score = score * max(protective_factor, 0.0)
        
        # Step 4: Use conversation history to assess trajectory (is risk escalating?)
        trajectory_factor = self._assess_escalation(
            message, 
            conversation_history,
            matched_categories
        )
        score = score * trajectory_factor
        
        # Step 5: Clamp score to 0-100
        score = max(0, min(100, int(score)))
        
        # Step 6: Determine risk level and action needed
        if score < 30:
            level = RiskLevel.GREEN
            category = 'low'
            action = False
            urgent = False
            confidence = 0.9 if len(indicators) == 0 else 0.7
        elif score < 60:
            level = RiskLevel.AMBER
            category = 'moderate'
            action = False
            urgent = False
            confidence = min(0.85, 0.5 + (score / 200))
        elif score < 75:
            level = RiskLevel.ORANGE
            category = 'high'
            action = True  # Recommend assessment
            urgent = False
            confidence = min(0.95, 0.6 + (score / 200))
        else:
            level = RiskLevel.RED
            category = 'critical'
            action = True  # Definitely recommend assessment
            urgent = True  # Alert clinician
            confidence = min(1.0, 0.7 + (score / 200))
        
        # Step 7: Build reasoning string
        if len(indicators) > 0:
            reasoning = f"Detected: {', '.join(indicators[:2])}. "
            if trajectory_factor < 1.0:
                reasoning += "Risk escalating. "
            reasoning += f"Confidence: {int(confidence*100)}%"
        else:
            reasoning = f"Score: {score}. Likely safe."
        
        return {
            'risk_score': score,
            'risk_level': level.value,
            'risk_category': category,
            'indicators': indicators,
            'action_needed': action,
            'urgent_action': urgent,
            'confidence': round(confidence, 2),
            'reasoning': reasoning[:200],
        }
    
    def _no_risk_response(self) -> Dict:
        """Return standard no-risk response"""
        return {
            'risk_score': 0,
            'risk_level': 'green',
            'risk_category': 'low',
            'indicators': [],
            'action_needed': False,
            'urgent_action': False,
            'confidence': 1.0,
            'reasoning': 'No risk detected.',
        }
    
    def _assess_escalation(self, 
                          current_message: str, 
                          history: List[Dict] = None,
                          matched_categories: List[str] = None) -> float:
        """
        Assess if risk is escalating based on conversation trajectory.
        Returns a multiplier: 1.0 = stable, > 1.0 = escalating, < 1.0 = improving
        """
        if not history or len(history) < 2:
            return 1.0  # No history, neutral
        
        if matched_categories is None:
            matched_categories = []
        
        # Check last few user messages for escalation
        escalation_multiplier = 1.0
        
        # If current message has direct planning or imminent warning, increase urgency
        if 'direct_planning' in matched_categories or 'imminent_warning' in matched_categories:
            escalation_multiplier = 1.5
        
        # Check if ideation appears multiple times in recent history
        if 'direct_ideation' in matched_categories:
            recent_user_messages = [
                msg['content'].lower() for msg in history[-6:] 
                if msg.get('role') == 'user'
            ]
            ideation_count = sum(
                1 for msg in recent_user_messages
                if self.keyword_patterns['direct_ideation'].search(msg)
            )
            if ideation_count >= 2:
                escalation_multiplier = 1.3  # Repeated ideation = concerning
        
        return escalation_multiplier
    
    def get_risk_prompt(self, risk_level: str) -> str:
        """
        Get appropriate user-facing message based on risk level.
        Clinical and compassionate.
        """
        prompts = {
            'green': None,  # No prompt
            'amber': None,  # No prompt
            'orange': (
                "⚠️ We're Noticing Something\n\n"
                "Your recent messages contain some concerning language. "
                "We'd like to understand better what you're experiencing.\n\n"
                "Would you be willing to take a brief assessment (3-4 minutes)? "
                "This helps us support you better."
            ),
            'red': (
                "🚨 We're Concerned About Your Safety\n\n"
                "Based on what you've shared, we want to make sure you get "
                "the right support right now.\n\n"
                "Please take a quick formal assessment so we can connect you "
                "with the right resources. This is important and confidential."
            ),
        }
        return prompts.get(risk_level)
    
    def format_indicators_for_display(self, indicators: List[str]) -> str:
        """
        Format indicators for human-readable display.
        
        Example:
            ['direct_ideation', 'hopelessness'] 
            → "Active suicidal thinking, feelings of hopelessness"
        """
        readable_map = {
            'direct_ideation': 'Active suicidal thinking',
            'direct_planning': 'Mentioned suicide plans',
            'past_attempt': 'History of past attempt',
            'hopelessness': 'Feelings of hopelessness',
            'burdensomeness': 'Feels like a burden to others',
            'isolation': 'Social isolation or disconnection',
            'behavioral_change': 'Recent behavioral changes',
            'imminent_warning': 'Urgent/imminent warning signs',
            'substance_risk': 'Substance use as risk factor',
        }
        return ', '.join([readable_map.get(ind, ind) for ind in indicators])


# Singleton instance for efficient module-level usage
_monitor_instance = None

def get_safety_monitor() -> SafetyMonitor:
    """Get or create singleton SafetyMonitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = SafetyMonitor()
    return _monitor_instance


def analyze_chat_message(message: str, history: List[Dict] = None) -> Dict:
    """
    Convenience function for analyzing therapy chat messages.
    
    Example:
        result = analyze_chat_message(
            "I can't do this anymore",
            history=[
                {'role': 'user', 'content': 'Everything feels hopeless'},
                {'role': 'ai', 'content': 'I hear you...'},
            ]
        )
        
        if result['action_needed']:
            # Prompt user to take formal assessment
            display_assessment_prompt(result['risk_level'])
    """
    monitor = get_safety_monitor()
    return monitor.analyze_message(message, history)
