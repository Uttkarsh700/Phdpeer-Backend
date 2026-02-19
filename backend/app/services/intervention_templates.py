"""Intervention templates for fallback when LLM is unavailable."""
from typing import Dict, Any, List


# =============================================================================
# Intervention Types
# =============================================================================

INTERVENTION_TYPES = [
    "notification",
    "email_suggestion",
    "milestone_restructure",
    "check_in_schedule",
    "resource_recommendation",
]


# =============================================================================
# Risk Level Templates
# =============================================================================

# Templates organized by risk trigger
DROPOUT_RISK_TEMPLATES = {
    "high": {
        "title": "Immediate Support Recommended",
        "message": "Your recent activity patterns suggest you may be experiencing significant challenges. We strongly encourage you to connect with your support network.",
        "actions": [
            "Schedule a meeting with your supervisor to discuss current challenges",
            "Consider connecting with your institution's counseling services",
            "Review your timeline and identify milestones that can be adjusted",
            "Reach out to peer support groups or fellow PhD students",
        ],
        "urgency": "high",
    },
    "moderate": {
        "title": "Check-In Recommended",
        "message": "We've noticed some indicators that suggest you might benefit from additional support. Consider reaching out to your advisor.",
        "actions": [
            "Schedule a check-in with your supervisor",
            "Review your current workload and priorities",
            "Take time to assess your progress and well-being",
        ],
        "urgency": "medium",
    },
    "low": {
        "title": "Maintain Your Momentum",
        "message": "You're doing well! Keep up the good work and maintain your current routines.",
        "actions": [
            "Continue with your current schedule",
            "Celebrate your recent achievements",
        ],
        "urgency": "low",
    },
}

ENGAGEMENT_TEMPLATES = {
    "low": {
        "title": "Re-Engage with Your Research",
        "message": "Your engagement with the platform has decreased recently. Small steps can help rebuild momentum.",
        "actions": [
            "Set a small, achievable goal for this week",
            "Log any progress, no matter how minor",
            "Review your milestones and celebrate completed ones",
            "Connect with peers for motivation",
        ],
        "urgency": "medium",
    },
    "declining": {
        "title": "Engagement Declining",
        "message": "We've noticed a decline in your engagement. This is common during challenging phases of the PhD journey.",
        "actions": [
            "Reflect on what might be causing the decline",
            "Consider adjusting your timeline if needed",
            "Reach out to your supervisor for guidance",
        ],
        "urgency": "medium",
    },
}

CONTINUITY_TEMPLATES = {
    "poor": {
        "title": "Timeline Continuity Alert",
        "message": "Your timeline has significant gaps that may affect your progress. Consider restructuring your milestones.",
        "actions": [
            "Review and update your timeline",
            "Break large milestones into smaller tasks",
            "Identify and remove blockers",
            "Schedule regular progress check-ins",
        ],
        "urgency": "high",
    },
    "moderate": {
        "title": "Timeline Review Suggested",
        "message": "Your timeline could benefit from some adjustments to improve continuity.",
        "actions": [
            "Review milestone dependencies",
            "Consider adding buffer time for complex tasks",
            "Update estimated durations based on your experience",
        ],
        "urgency": "medium",
    },
}


# =============================================================================
# Dimension-Specific Templates
# =============================================================================

HEALTH_DIMENSION_TEMPLATES = {
    "mental_wellbeing": {
        "critical": {
            "title": "Mental Well-being Support",
            "message": "Your mental well-being scores indicate you may benefit from additional support. Please consider reaching out to professional services.",
            "actions": [
                "Contact your university's counseling center",
                "Speak with a trusted friend, family member, or mentor",
                "Practice self-care activities daily",
                "Consider temporary adjustments to your workload",
            ],
            "urgency": "high",
            "resources": [
                {"name": "University Counseling Services", "type": "service"},
                {"name": "Graduate Student Wellness Resources", "type": "guide"},
            ],
        },
        "concerning": {
            "title": "Well-being Check-In",
            "message": "Your well-being indicators suggest some areas need attention. Small changes can make a big difference.",
            "actions": [
                "Schedule regular breaks throughout your day",
                "Connect with supportive peers",
                "Consider stress management techniques",
            ],
            "urgency": "medium",
            "resources": [
                {"name": "Stress Management for Grad Students", "type": "guide"},
            ],
        },
    },
    "research_progress": {
        "critical": {
            "title": "Research Progress Alert",
            "message": "Your research progress has stalled. Immediate action is recommended to get back on track.",
            "actions": [
                "Schedule an urgent meeting with your supervisor",
                "Identify the main blockers to your progress",
                "Consider seeking additional expertise or resources",
                "Break down your next milestone into smaller tasks",
            ],
            "urgency": "high",
        },
        "concerning": {
            "title": "Research Progress Review",
            "message": "Your research progress could use some attention. Consider reviewing your approach.",
            "actions": [
                "Review your research methodology",
                "Seek feedback from your committee",
                "Adjust your timeline if needed",
            ],
            "urgency": "medium",
        },
    },
    "supervisor_relationship": {
        "critical": {
            "title": "Supervisor Relationship Attention",
            "message": "Communication with your supervisor appears to need attention. This is a key relationship for PhD success.",
            "actions": [
                "Request a dedicated meeting to discuss expectations",
                "Consider involving a third party mediator if needed",
                "Document your concerns and desired outcomes",
                "Explore graduate ombudsman services",
            ],
            "urgency": "high",
        },
        "concerning": {
            "title": "Improve Supervisor Communication",
            "message": "Consider strengthening your supervisor relationship through better communication.",
            "actions": [
                "Schedule regular check-in meetings",
                "Prepare agendas for meetings",
                "Share progress updates proactively",
            ],
            "urgency": "medium",
        },
    },
    "work_life_balance": {
        "critical": {
            "title": "Work-Life Balance Alert",
            "message": "Your work-life balance indicators suggest burnout risk. Taking action now is important.",
            "actions": [
                "Set firm boundaries on work hours",
                "Schedule non-negotiable personal time",
                "Consider temporarily reducing commitments",
                "Speak with your supervisor about workload",
            ],
            "urgency": "high",
        },
        "concerning": {
            "title": "Balance Check-In",
            "message": "Your work-life balance could use some attention.",
            "actions": [
                "Identify activities outside of research",
                "Set boundaries for work hours",
                "Practice saying no to extra commitments",
            ],
            "urgency": "medium",
        },
    },
    "motivation": {
        "critical": {
            "title": "Motivation Support",
            "message": "Your motivation levels are low. This is common but important to address.",
            "actions": [
                "Reconnect with your original research passion",
                "Set small, achievable daily goals",
                "Celebrate any progress, no matter how small",
                "Connect with inspiring peers or mentors",
            ],
            "urgency": "high",
        },
        "concerning": {
            "title": "Motivation Boost",
            "message": "Consider activities to boost your motivation.",
            "actions": [
                "Review your research purpose",
                "Set rewarding milestones",
                "Take breaks to prevent burnout",
            ],
            "urgency": "medium",
        },
    },
    "time_management": {
        "critical": {
            "title": "Time Management Restructure",
            "message": "Your time management needs significant attention. Consider restructuring your approach.",
            "actions": [
                "Implement time-blocking techniques",
                "Use productivity tools to track time",
                "Eliminate or delegate non-essential tasks",
                "Create a weekly planning routine",
            ],
            "urgency": "high",
        },
        "concerning": {
            "title": "Time Management Tips",
            "message": "Some time management improvements could help your productivity.",
            "actions": [
                "Prioritize tasks using a framework",
                "Minimize distractions during focus time",
                "Review your schedule weekly",
            ],
            "urgency": "medium",
        },
    },
    "academic_confidence": {
        "critical": {
            "title": "Building Academic Confidence",
            "message": "Your academic confidence scores are low. Remember, imposter syndrome is common in PhD programs.",
            "actions": [
                "Document your achievements and skills",
                "Seek supportive peer groups",
                "Consider speaking with a counselor about imposter syndrome",
                "Request specific positive feedback from your supervisor",
            ],
            "urgency": "high",
        },
        "concerning": {
            "title": "Confidence Building",
            "message": "Consider activities to build your academic confidence.",
            "actions": [
                "Celebrate your achievements",
                "Seek constructive feedback",
                "Connect with supportive peers",
            ],
            "urgency": "medium",
        },
    },
    "support_network": {
        "critical": {
            "title": "Build Your Support Network",
            "message": "Your support network appears limited. Building connections is important for PhD success.",
            "actions": [
                "Join PhD student groups or communities",
                "Attend departmental events",
                "Reach out to peers in your field",
                "Maintain relationships outside academia",
            ],
            "urgency": "high",
        },
        "concerning": {
            "title": "Strengthen Connections",
            "message": "Consider expanding your professional and personal support network.",
            "actions": [
                "Attend networking events",
                "Join online academic communities",
                "Schedule regular social activities",
            ],
            "urgency": "medium",
        },
    },
}


# =============================================================================
# Milestone-Specific Templates
# =============================================================================

MILESTONE_TEMPLATES = {
    "overdue_critical": {
        "title": "Critical Milestone Overdue",
        "message": "A critical milestone is overdue. Immediate action is recommended.",
        "actions": [
            "Contact your supervisor immediately",
            "Assess what's blocking completion",
            "Request deadline extension if needed",
            "Create a recovery plan",
        ],
        "urgency": "high",
    },
    "overdue_regular": {
        "title": "Milestone Overdue",
        "message": "A milestone is past its target date. Consider reviewing your timeline.",
        "actions": [
            "Update the milestone target date",
            "Identify blockers to completion",
            "Break down remaining work into smaller tasks",
        ],
        "urgency": "medium",
    },
    "approaching_deadline": {
        "title": "Milestone Approaching",
        "message": "A milestone deadline is approaching. Make sure you're prepared.",
        "actions": [
            "Review remaining tasks for this milestone",
            "Prioritize milestone-related work",
            "Communicate with relevant stakeholders",
        ],
        "urgency": "low",
    },
    "multiple_overdue": {
        "title": "Multiple Milestones Overdue",
        "message": "Several milestones are overdue. A timeline review is recommended.",
        "actions": [
            "Schedule a timeline review with your supervisor",
            "Prioritize the most important milestones",
            "Consider extending less critical deadlines",
            "Identify common blockers",
        ],
        "urgency": "high",
    },
}


# =============================================================================
# Check-In Schedule Templates
# =============================================================================

CHECK_IN_TEMPLATES = {
    "weekly": {
        "frequency": "weekly",
        "title": "Weekly Check-In Scheduled",
        "message": "Based on your current status, we recommend weekly check-ins.",
        "suggested_agenda": [
            "Review progress on current milestones",
            "Discuss any blockers or challenges",
            "Adjust short-term goals as needed",
        ],
    },
    "biweekly": {
        "frequency": "biweekly",
        "title": "Bi-Weekly Check-In Suggested",
        "message": "Regular bi-weekly check-ins can help maintain momentum.",
        "suggested_agenda": [
            "Review two-week progress",
            "Update milestone status",
            "Plan for the next two weeks",
        ],
    },
    "monthly": {
        "frequency": "monthly",
        "title": "Monthly Check-In",
        "message": "A monthly check-in is recommended to stay on track.",
        "suggested_agenda": [
            "Review monthly progress",
            "Assess overall health and well-being",
            "Update long-term goals if needed",
        ],
    },
}


# =============================================================================
# Resource Recommendation Templates
# =============================================================================

RESOURCE_TEMPLATES = {
    "mental_health": [
        {
            "name": "University Counseling Center",
            "type": "service",
            "description": "Professional mental health support services",
        },
        {
            "name": "Graduate Student Mental Health Guide",
            "type": "guide",
            "description": "Strategies for maintaining mental health during PhD",
        },
        {
            "name": "Mindfulness and Meditation Apps",
            "type": "tool",
            "description": "Digital tools for stress management",
        },
    ],
    "productivity": [
        {
            "name": "Time Management Workshop",
            "type": "workshop",
            "description": "Strategies for effective time management",
        },
        {
            "name": "Academic Writing Bootcamp",
            "type": "program",
            "description": "Intensive writing productivity program",
        },
        {
            "name": "Pomodoro Technique Guide",
            "type": "guide",
            "description": "Focus and productivity methodology",
        },
    ],
    "networking": [
        {
            "name": "PhD Student Groups",
            "type": "community",
            "description": "Connect with fellow PhD students",
        },
        {
            "name": "Academic Conferences",
            "type": "event",
            "description": "Present work and meet researchers",
        },
        {
            "name": "Online Research Communities",
            "type": "community",
            "description": "Virtual spaces for academic discussion",
        },
    ],
    "research_skills": [
        {
            "name": "Research Methods Workshop",
            "type": "workshop",
            "description": "Improve research methodology skills",
        },
        {
            "name": "Statistical Analysis Training",
            "type": "training",
            "description": "Build quantitative analysis skills",
        },
        {
            "name": "Literature Review Strategies",
            "type": "guide",
            "description": "Effective approaches to literature review",
        },
    ],
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_dropout_risk_template(risk_level: str) -> Dict[str, Any]:
    """Get dropout risk template by level."""
    return DROPOUT_RISK_TEMPLATES.get(risk_level, DROPOUT_RISK_TEMPLATES["moderate"])


def get_engagement_template(engagement_level: str) -> Dict[str, Any]:
    """Get engagement template by level."""
    return ENGAGEMENT_TEMPLATES.get(engagement_level, ENGAGEMENT_TEMPLATES["declining"])


def get_continuity_template(continuity_level: str) -> Dict[str, Any]:
    """Get continuity template by level."""
    return CONTINUITY_TEMPLATES.get(continuity_level, CONTINUITY_TEMPLATES["moderate"])


def get_health_dimension_template(
    dimension: str,
    severity: str
) -> Dict[str, Any]:
    """
    Get health dimension template.

    Args:
        dimension: Health dimension name (e.g., 'mental_wellbeing')
        severity: Severity level ('critical' or 'concerning')

    Returns:
        Template dictionary
    """
    dimension_templates = HEALTH_DIMENSION_TEMPLATES.get(dimension, {})
    return dimension_templates.get(
        severity,
        {
            "title": f"Attention Needed: {dimension.replace('_', ' ').title()}",
            "message": f"Your {dimension.replace('_', ' ')} needs attention.",
            "actions": ["Review this area with your supervisor"],
            "urgency": "medium",
        }
    )


def get_milestone_template(milestone_status: str) -> Dict[str, Any]:
    """Get milestone template by status."""
    return MILESTONE_TEMPLATES.get(
        milestone_status,
        MILESTONE_TEMPLATES["overdue_regular"]
    )


def get_check_in_template(frequency: str) -> Dict[str, Any]:
    """Get check-in template by frequency."""
    return CHECK_IN_TEMPLATES.get(frequency, CHECK_IN_TEMPLATES["biweekly"])


def get_resources_by_category(category: str) -> List[Dict[str, Any]]:
    """Get resource recommendations by category."""
    return RESOURCE_TEMPLATES.get(category, [])


def get_all_resource_categories() -> List[str]:
    """Get all available resource categories."""
    return list(RESOURCE_TEMPLATES.keys())
