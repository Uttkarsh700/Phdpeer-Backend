"""
Hardcoded fallback templates for cold start timeline generation.

Provides discipline-specific PhD timeline templates when LLM is unavailable.
"""
from typing import Dict, List, Any, Optional
from difflib import SequenceMatcher


# =============================================================================
# Template Definitions
# =============================================================================

TEMPLATES: Dict[str, Dict[str, Any]] = {
    "computer_science": {
        "discipline": "Computer Science",
        "total_duration_months": 60,
        "stages": [
            {
                "title": "Coursework and Foundations",
                "stage_type": "coursework",
                "description": "Complete required PhD coursework in core CS areas and research methods",
                "order_hint": 1,
                "duration_months": 12,
                "confidence": 0.9
            },
            {
                "title": "Literature Review and Problem Definition",
                "stage_type": "literature_review",
                "description": "Comprehensive survey of existing research, identify research gaps, and define problem statement",
                "order_hint": 2,
                "duration_months": 8,
                "confidence": 0.85
            },
            {
                "title": "Methodology and System Design",
                "stage_type": "methodology",
                "description": "Design research methodology, system architecture, and experimental framework",
                "order_hint": 3,
                "duration_months": 6,
                "confidence": 0.8
            },
            {
                "title": "Implementation and Experiments",
                "stage_type": "data_collection",
                "description": "Implement proposed system/algorithm, run experiments, collect benchmark results",
                "order_hint": 4,
                "duration_months": 14,
                "confidence": 0.75
            },
            {
                "title": "Analysis and Evaluation",
                "stage_type": "analysis",
                "description": "Analyze experimental results, compare with baselines, validate hypotheses",
                "order_hint": 5,
                "duration_months": 8,
                "confidence": 0.8
            },
            {
                "title": "Dissertation Writing and Defense",
                "stage_type": "writing",
                "description": "Write dissertation chapters, defend thesis, final revisions",
                "order_hint": 6,
                "duration_months": 12,
                "confidence": 0.85
            }
        ],
        "milestones": [
            {"name": "Complete Core Coursework", "stage": "Coursework and Foundations", "is_critical": True, "milestone_type": "academic"},
            {"name": "Pass Qualifying Examination", "stage": "Coursework and Foundations", "is_critical": True, "milestone_type": "examination"},
            {"name": "Complete Literature Survey", "stage": "Literature Review and Problem Definition", "is_critical": False, "milestone_type": "deliverable"},
            {"name": "Define Research Problem", "stage": "Literature Review and Problem Definition", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Submit First Paper", "stage": "Methodology and System Design", "is_critical": False, "milestone_type": "publication"},
            {"name": "Proposal Defense", "stage": "Methodology and System Design", "is_critical": True, "milestone_type": "examination"},
            {"name": "Complete System Implementation", "stage": "Implementation and Experiments", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Run Primary Experiments", "stage": "Implementation and Experiments", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Submit Conference Paper", "stage": "Analysis and Evaluation", "is_critical": False, "milestone_type": "publication"},
            {"name": "Complete Results Analysis", "stage": "Analysis and Evaluation", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Submit Dissertation Draft", "stage": "Dissertation Writing and Defense", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Final Dissertation Defense", "stage": "Dissertation Writing and Defense", "is_critical": True, "milestone_type": "examination"}
        ],
        "dependencies": [
            {"dependent": "Pass Qualifying Examination", "depends_on": "Complete Core Coursework", "type": "finish_to_start"},
            {"dependent": "Define Research Problem", "depends_on": "Complete Literature Survey", "type": "finish_to_start"},
            {"dependent": "Proposal Defense", "depends_on": "Define Research Problem", "type": "finish_to_start"},
            {"dependent": "Complete System Implementation", "depends_on": "Proposal Defense", "type": "finish_to_start"},
            {"dependent": "Run Primary Experiments", "depends_on": "Complete System Implementation", "type": "finish_to_start"},
            {"dependent": "Complete Results Analysis", "depends_on": "Run Primary Experiments", "type": "finish_to_start"},
            {"dependent": "Submit Dissertation Draft", "depends_on": "Complete Results Analysis", "type": "finish_to_start"},
            {"dependent": "Final Dissertation Defense", "depends_on": "Submit Dissertation Draft", "type": "finish_to_start"}
        ]
    },

    "biology": {
        "discipline": "Biology",
        "total_duration_months": 66,
        "stages": [
            {
                "title": "Coursework and Laboratory Training",
                "stage_type": "coursework",
                "description": "Complete required coursework, laboratory safety training, and technique acquisition",
                "order_hint": 1,
                "duration_months": 12,
                "confidence": 0.9
            },
            {
                "title": "Literature Review and Hypothesis Development",
                "stage_type": "literature_review",
                "description": "Review existing research, develop research hypotheses, and design experimental approach",
                "order_hint": 2,
                "duration_months": 6,
                "confidence": 0.85
            },
            {
                "title": "IRB/IACUC Approval and Protocol Development",
                "stage_type": "methodology",
                "description": "Obtain ethics approvals, develop experimental protocols, establish collaborations",
                "order_hint": 3,
                "duration_months": 6,
                "confidence": 0.8
            },
            {
                "title": "Primary Data Collection and Experiments",
                "stage_type": "data_collection",
                "description": "Conduct wet lab experiments, collect samples, perform assays and measurements",
                "order_hint": 4,
                "duration_months": 20,
                "confidence": 0.7
            },
            {
                "title": "Data Analysis and Validation",
                "stage_type": "analysis",
                "description": "Analyze experimental data, validate findings, conduct follow-up experiments",
                "order_hint": 5,
                "duration_months": 10,
                "confidence": 0.75
            },
            {
                "title": "Dissertation Writing and Defense",
                "stage_type": "writing",
                "description": "Write dissertation, prepare publications, defend thesis",
                "order_hint": 6,
                "duration_months": 12,
                "confidence": 0.85
            }
        ],
        "milestones": [
            {"name": "Complete Laboratory Safety Training", "stage": "Coursework and Laboratory Training", "is_critical": True, "milestone_type": "training"},
            {"name": "Pass Qualifying Examination", "stage": "Coursework and Laboratory Training", "is_critical": True, "milestone_type": "examination"},
            {"name": "Complete Literature Review", "stage": "Literature Review and Hypothesis Development", "is_critical": False, "milestone_type": "deliverable"},
            {"name": "Obtain IRB/IACUC Approval", "stage": "IRB/IACUC Approval and Protocol Development", "is_critical": True, "milestone_type": "regulatory"},
            {"name": "Proposal Defense", "stage": "IRB/IACUC Approval and Protocol Development", "is_critical": True, "milestone_type": "examination"},
            {"name": "Complete Primary Experiments", "stage": "Primary Data Collection and Experiments", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Submit First Manuscript", "stage": "Primary Data Collection and Experiments", "is_critical": False, "milestone_type": "publication"},
            {"name": "Complete Statistical Analysis", "stage": "Data Analysis and Validation", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Submit Dissertation Draft", "stage": "Dissertation Writing and Defense", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Final Dissertation Defense", "stage": "Dissertation Writing and Defense", "is_critical": True, "milestone_type": "examination"}
        ],
        "dependencies": [
            {"dependent": "Pass Qualifying Examination", "depends_on": "Complete Laboratory Safety Training", "type": "finish_to_start"},
            {"dependent": "Obtain IRB/IACUC Approval", "depends_on": "Complete Literature Review", "type": "finish_to_start"},
            {"dependent": "Proposal Defense", "depends_on": "Obtain IRB/IACUC Approval", "type": "finish_to_start"},
            {"dependent": "Complete Primary Experiments", "depends_on": "Proposal Defense", "type": "finish_to_start"},
            {"dependent": "Complete Statistical Analysis", "depends_on": "Complete Primary Experiments", "type": "finish_to_start"},
            {"dependent": "Submit Dissertation Draft", "depends_on": "Complete Statistical Analysis", "type": "finish_to_start"},
            {"dependent": "Final Dissertation Defense", "depends_on": "Submit Dissertation Draft", "type": "finish_to_start"}
        ]
    },

    "psychology": {
        "discipline": "Psychology",
        "total_duration_months": 60,
        "stages": [
            {
                "title": "Coursework and Research Methods Training",
                "stage_type": "coursework",
                "description": "Complete required coursework in psychology theory, statistics, and research methods",
                "order_hint": 1,
                "duration_months": 12,
                "confidence": 0.9
            },
            {
                "title": "Literature Review and Theory Development",
                "stage_type": "literature_review",
                "description": "Comprehensive literature review, develop theoretical framework and research questions",
                "order_hint": 2,
                "duration_months": 8,
                "confidence": 0.85
            },
            {
                "title": "IRB Approval and Study Design",
                "stage_type": "methodology",
                "description": "Obtain IRB approval, design studies, develop measurement instruments",
                "order_hint": 3,
                "duration_months": 6,
                "confidence": 0.8
            },
            {
                "title": "Data Collection",
                "stage_type": "data_collection",
                "description": "Recruit participants, conduct experiments/surveys, collect behavioral data",
                "order_hint": 4,
                "duration_months": 14,
                "confidence": 0.75
            },
            {
                "title": "Data Analysis and Interpretation",
                "stage_type": "analysis",
                "description": "Statistical analysis, interpret findings, relate to theory",
                "order_hint": 5,
                "duration_months": 8,
                "confidence": 0.8
            },
            {
                "title": "Dissertation Writing and Defense",
                "stage_type": "writing",
                "description": "Write dissertation, prepare publications, defend thesis",
                "order_hint": 6,
                "duration_months": 12,
                "confidence": 0.85
            }
        ],
        "milestones": [
            {"name": "Complete Core Coursework", "stage": "Coursework and Research Methods Training", "is_critical": True, "milestone_type": "academic"},
            {"name": "Pass Comprehensive Examinations", "stage": "Coursework and Research Methods Training", "is_critical": True, "milestone_type": "examination"},
            {"name": "Complete Literature Review", "stage": "Literature Review and Theory Development", "is_critical": False, "milestone_type": "deliverable"},
            {"name": "Obtain IRB Approval", "stage": "IRB Approval and Study Design", "is_critical": True, "milestone_type": "regulatory"},
            {"name": "Proposal Defense", "stage": "IRB Approval and Study Design", "is_critical": True, "milestone_type": "examination"},
            {"name": "Complete Participant Recruitment", "stage": "Data Collection", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Complete Data Collection", "stage": "Data Collection", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Complete Statistical Analysis", "stage": "Data Analysis and Interpretation", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Submit Dissertation Draft", "stage": "Dissertation Writing and Defense", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Final Dissertation Defense", "stage": "Dissertation Writing and Defense", "is_critical": True, "milestone_type": "examination"}
        ],
        "dependencies": [
            {"dependent": "Pass Comprehensive Examinations", "depends_on": "Complete Core Coursework", "type": "finish_to_start"},
            {"dependent": "Obtain IRB Approval", "depends_on": "Complete Literature Review", "type": "finish_to_start"},
            {"dependent": "Proposal Defense", "depends_on": "Obtain IRB Approval", "type": "finish_to_start"},
            {"dependent": "Complete Participant Recruitment", "depends_on": "Proposal Defense", "type": "finish_to_start"},
            {"dependent": "Complete Data Collection", "depends_on": "Complete Participant Recruitment", "type": "finish_to_start"},
            {"dependent": "Complete Statistical Analysis", "depends_on": "Complete Data Collection", "type": "finish_to_start"},
            {"dependent": "Submit Dissertation Draft", "depends_on": "Complete Statistical Analysis", "type": "finish_to_start"},
            {"dependent": "Final Dissertation Defense", "depends_on": "Submit Dissertation Draft", "type": "finish_to_start"}
        ]
    },

    "engineering": {
        "discipline": "Engineering",
        "total_duration_months": 60,
        "stages": [
            {
                "title": "Coursework and Technical Foundations",
                "stage_type": "coursework",
                "description": "Complete required coursework in engineering fundamentals and advanced topics",
                "order_hint": 1,
                "duration_months": 12,
                "confidence": 0.9
            },
            {
                "title": "Literature Review and Problem Formulation",
                "stage_type": "literature_review",
                "description": "Review state-of-the-art, identify research gaps, formulate engineering problem",
                "order_hint": 2,
                "duration_months": 6,
                "confidence": 0.85
            },
            {
                "title": "Design and Methodology Development",
                "stage_type": "methodology",
                "description": "Design system/prototype, develop methodology, create simulation models",
                "order_hint": 3,
                "duration_months": 8,
                "confidence": 0.8
            },
            {
                "title": "Implementation and Testing",
                "stage_type": "data_collection",
                "description": "Build prototype, run simulations, conduct laboratory experiments",
                "order_hint": 4,
                "duration_months": 14,
                "confidence": 0.75
            },
            {
                "title": "Analysis and Optimization",
                "stage_type": "analysis",
                "description": "Analyze results, optimize design, validate performance metrics",
                "order_hint": 5,
                "duration_months": 8,
                "confidence": 0.8
            },
            {
                "title": "Dissertation Writing and Defense",
                "stage_type": "writing",
                "description": "Write dissertation, prepare publications and patents, defend thesis",
                "order_hint": 6,
                "duration_months": 12,
                "confidence": 0.85
            }
        ],
        "milestones": [
            {"name": "Complete Core Coursework", "stage": "Coursework and Technical Foundations", "is_critical": True, "milestone_type": "academic"},
            {"name": "Pass Qualifying Examination", "stage": "Coursework and Technical Foundations", "is_critical": True, "milestone_type": "examination"},
            {"name": "Complete Literature Review", "stage": "Literature Review and Problem Formulation", "is_critical": False, "milestone_type": "deliverable"},
            {"name": "Complete System Design", "stage": "Design and Methodology Development", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Proposal Defense", "stage": "Design and Methodology Development", "is_critical": True, "milestone_type": "examination"},
            {"name": "Complete Prototype", "stage": "Implementation and Testing", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Complete Testing", "stage": "Implementation and Testing", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Submit Patent Application", "stage": "Analysis and Optimization", "is_critical": False, "milestone_type": "deliverable"},
            {"name": "Complete Performance Analysis", "stage": "Analysis and Optimization", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Submit Dissertation Draft", "stage": "Dissertation Writing and Defense", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Final Dissertation Defense", "stage": "Dissertation Writing and Defense", "is_critical": True, "milestone_type": "examination"}
        ],
        "dependencies": [
            {"dependent": "Pass Qualifying Examination", "depends_on": "Complete Core Coursework", "type": "finish_to_start"},
            {"dependent": "Complete System Design", "depends_on": "Complete Literature Review", "type": "finish_to_start"},
            {"dependent": "Proposal Defense", "depends_on": "Complete System Design", "type": "finish_to_start"},
            {"dependent": "Complete Prototype", "depends_on": "Proposal Defense", "type": "finish_to_start"},
            {"dependent": "Complete Testing", "depends_on": "Complete Prototype", "type": "finish_to_start"},
            {"dependent": "Complete Performance Analysis", "depends_on": "Complete Testing", "type": "finish_to_start"},
            {"dependent": "Submit Dissertation Draft", "depends_on": "Complete Performance Analysis", "type": "finish_to_start"},
            {"dependent": "Final Dissertation Defense", "depends_on": "Submit Dissertation Draft", "type": "finish_to_start"}
        ]
    },

    "humanities": {
        "discipline": "Humanities",
        "total_duration_months": 72,
        "stages": [
            {
                "title": "Coursework and Language Training",
                "stage_type": "coursework",
                "description": "Complete required coursework, language requirements, and theoretical foundations",
                "order_hint": 1,
                "duration_months": 18,
                "confidence": 0.9
            },
            {
                "title": "Comprehensive Literature Review",
                "stage_type": "literature_review",
                "description": "Extensive reading and synthesis of primary and secondary sources",
                "order_hint": 2,
                "duration_months": 12,
                "confidence": 0.85
            },
            {
                "title": "Archival Research and Fieldwork",
                "stage_type": "data_collection",
                "description": "Conduct archival research, interviews, and fieldwork as needed",
                "order_hint": 3,
                "duration_months": 12,
                "confidence": 0.75
            },
            {
                "title": "Analysis and Interpretation",
                "stage_type": "analysis",
                "description": "Analyze sources, develop arguments, refine theoretical framework",
                "order_hint": 4,
                "duration_months": 10,
                "confidence": 0.8
            },
            {
                "title": "Dissertation Writing",
                "stage_type": "writing",
                "description": "Write dissertation chapters with regular advisor feedback",
                "order_hint": 5,
                "duration_months": 16,
                "confidence": 0.8
            },
            {
                "title": "Defense and Revision",
                "stage_type": "defense",
                "description": "Defend dissertation, complete revisions, prepare for publication",
                "order_hint": 6,
                "duration_months": 4,
                "confidence": 0.9
            }
        ],
        "milestones": [
            {"name": "Complete Core Coursework", "stage": "Coursework and Language Training", "is_critical": True, "milestone_type": "academic"},
            {"name": "Pass Language Examinations", "stage": "Coursework and Language Training", "is_critical": True, "milestone_type": "examination"},
            {"name": "Pass Comprehensive Examinations", "stage": "Comprehensive Literature Review", "is_critical": True, "milestone_type": "examination"},
            {"name": "Complete Prospectus", "stage": "Comprehensive Literature Review", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Complete Archival Research", "stage": "Archival Research and Fieldwork", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Complete Chapter Drafts", "stage": "Dissertation Writing", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Submit Complete Dissertation", "stage": "Dissertation Writing", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Final Dissertation Defense", "stage": "Defense and Revision", "is_critical": True, "milestone_type": "examination"}
        ],
        "dependencies": [
            {"dependent": "Pass Language Examinations", "depends_on": "Complete Core Coursework", "type": "finish_to_start"},
            {"dependent": "Pass Comprehensive Examinations", "depends_on": "Pass Language Examinations", "type": "finish_to_start"},
            {"dependent": "Complete Prospectus", "depends_on": "Pass Comprehensive Examinations", "type": "finish_to_start"},
            {"dependent": "Complete Archival Research", "depends_on": "Complete Prospectus", "type": "finish_to_start"},
            {"dependent": "Complete Chapter Drafts", "depends_on": "Complete Archival Research", "type": "finish_to_start"},
            {"dependent": "Submit Complete Dissertation", "depends_on": "Complete Chapter Drafts", "type": "finish_to_start"},
            {"dependent": "Final Dissertation Defense", "depends_on": "Submit Complete Dissertation", "type": "finish_to_start"}
        ]
    },

    "business": {
        "discipline": "Business",
        "total_duration_months": 60,
        "stages": [
            {
                "title": "Coursework and Research Methods",
                "stage_type": "coursework",
                "description": "Complete doctoral coursework in theory, statistics, and research methods",
                "order_hint": 1,
                "duration_months": 18,
                "confidence": 0.9
            },
            {
                "title": "Literature Review and Theory Development",
                "stage_type": "literature_review",
                "description": "Review management/business literature, develop theoretical framework",
                "order_hint": 2,
                "duration_months": 8,
                "confidence": 0.85
            },
            {
                "title": "Research Design and IRB Approval",
                "stage_type": "methodology",
                "description": "Design research methodology, obtain IRB approval if needed",
                "order_hint": 3,
                "duration_months": 4,
                "confidence": 0.8
            },
            {
                "title": "Data Collection",
                "stage_type": "data_collection",
                "description": "Collect data through surveys, interviews, archival sources, or experiments",
                "order_hint": 4,
                "duration_months": 12,
                "confidence": 0.75
            },
            {
                "title": "Data Analysis",
                "stage_type": "analysis",
                "description": "Analyze data using appropriate statistical/qualitative methods",
                "order_hint": 5,
                "duration_months": 8,
                "confidence": 0.8
            },
            {
                "title": "Dissertation Writing and Defense",
                "stage_type": "writing",
                "description": "Write dissertation, submit to journals, defend thesis",
                "order_hint": 6,
                "duration_months": 10,
                "confidence": 0.85
            }
        ],
        "milestones": [
            {"name": "Complete Core Coursework", "stage": "Coursework and Research Methods", "is_critical": True, "milestone_type": "academic"},
            {"name": "Pass Comprehensive Examinations", "stage": "Coursework and Research Methods", "is_critical": True, "milestone_type": "examination"},
            {"name": "Complete Literature Review", "stage": "Literature Review and Theory Development", "is_critical": False, "milestone_type": "deliverable"},
            {"name": "Proposal Defense", "stage": "Research Design and IRB Approval", "is_critical": True, "milestone_type": "examination"},
            {"name": "Complete Data Collection", "stage": "Data Collection", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Submit First Journal Paper", "stage": "Data Analysis", "is_critical": False, "milestone_type": "publication"},
            {"name": "Complete Analysis", "stage": "Data Analysis", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Submit Dissertation Draft", "stage": "Dissertation Writing and Defense", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Final Dissertation Defense", "stage": "Dissertation Writing and Defense", "is_critical": True, "milestone_type": "examination"}
        ],
        "dependencies": [
            {"dependent": "Pass Comprehensive Examinations", "depends_on": "Complete Core Coursework", "type": "finish_to_start"},
            {"dependent": "Proposal Defense", "depends_on": "Complete Literature Review", "type": "finish_to_start"},
            {"dependent": "Complete Data Collection", "depends_on": "Proposal Defense", "type": "finish_to_start"},
            {"dependent": "Complete Analysis", "depends_on": "Complete Data Collection", "type": "finish_to_start"},
            {"dependent": "Submit Dissertation Draft", "depends_on": "Complete Analysis", "type": "finish_to_start"},
            {"dependent": "Final Dissertation Defense", "depends_on": "Submit Dissertation Draft", "type": "finish_to_start"}
        ]
    },

    "medicine": {
        "discipline": "Medicine",
        "total_duration_months": 60,
        "stages": [
            {
                "title": "Coursework and Clinical Training",
                "stage_type": "coursework",
                "description": "Complete required coursework, clinical rotations, and research methods training",
                "order_hint": 1,
                "duration_months": 12,
                "confidence": 0.9
            },
            {
                "title": "Literature Review and Protocol Development",
                "stage_type": "literature_review",
                "description": "Review clinical literature, develop research protocol",
                "order_hint": 2,
                "duration_months": 6,
                "confidence": 0.85
            },
            {
                "title": "IRB Approval and Study Setup",
                "stage_type": "methodology",
                "description": "Obtain IRB approval, register clinical trial, establish recruitment sites",
                "order_hint": 3,
                "duration_months": 6,
                "confidence": 0.8
            },
            {
                "title": "Patient Recruitment and Data Collection",
                "stage_type": "data_collection",
                "description": "Recruit patients, collect clinical data, conduct interventions",
                "order_hint": 4,
                "duration_months": 18,
                "confidence": 0.7
            },
            {
                "title": "Data Analysis and Clinical Validation",
                "stage_type": "analysis",
                "description": "Analyze clinical outcomes, validate findings, assess clinical significance",
                "order_hint": 5,
                "duration_months": 8,
                "confidence": 0.8
            },
            {
                "title": "Dissertation Writing and Defense",
                "stage_type": "writing",
                "description": "Write dissertation, publish findings, defend thesis",
                "order_hint": 6,
                "duration_months": 10,
                "confidence": 0.85
            }
        ],
        "milestones": [
            {"name": "Complete Required Coursework", "stage": "Coursework and Clinical Training", "is_critical": True, "milestone_type": "academic"},
            {"name": "Pass Qualifying Examination", "stage": "Coursework and Clinical Training", "is_critical": True, "milestone_type": "examination"},
            {"name": "Complete Literature Review", "stage": "Literature Review and Protocol Development", "is_critical": False, "milestone_type": "deliverable"},
            {"name": "Obtain IRB Approval", "stage": "IRB Approval and Study Setup", "is_critical": True, "milestone_type": "regulatory"},
            {"name": "Register Clinical Trial", "stage": "IRB Approval and Study Setup", "is_critical": True, "milestone_type": "regulatory"},
            {"name": "Proposal Defense", "stage": "IRB Approval and Study Setup", "is_critical": True, "milestone_type": "examination"},
            {"name": "Complete Patient Recruitment", "stage": "Patient Recruitment and Data Collection", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Complete Data Collection", "stage": "Patient Recruitment and Data Collection", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Complete Statistical Analysis", "stage": "Data Analysis and Clinical Validation", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Submit Dissertation Draft", "stage": "Dissertation Writing and Defense", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Final Dissertation Defense", "stage": "Dissertation Writing and Defense", "is_critical": True, "milestone_type": "examination"}
        ],
        "dependencies": [
            {"dependent": "Pass Qualifying Examination", "depends_on": "Complete Required Coursework", "type": "finish_to_start"},
            {"dependent": "Obtain IRB Approval", "depends_on": "Complete Literature Review", "type": "finish_to_start"},
            {"dependent": "Register Clinical Trial", "depends_on": "Obtain IRB Approval", "type": "finish_to_start"},
            {"dependent": "Proposal Defense", "depends_on": "Register Clinical Trial", "type": "finish_to_start"},
            {"dependent": "Complete Patient Recruitment", "depends_on": "Proposal Defense", "type": "finish_to_start"},
            {"dependent": "Complete Data Collection", "depends_on": "Complete Patient Recruitment", "type": "finish_to_start"},
            {"dependent": "Complete Statistical Analysis", "depends_on": "Complete Data Collection", "type": "finish_to_start"},
            {"dependent": "Submit Dissertation Draft", "depends_on": "Complete Statistical Analysis", "type": "finish_to_start"},
            {"dependent": "Final Dissertation Defense", "depends_on": "Submit Dissertation Draft", "type": "finish_to_start"}
        ]
    },

    "generic": {
        "discipline": "Generic PhD",
        "total_duration_months": 60,
        "stages": [
            {
                "title": "Coursework",
                "stage_type": "coursework",
                "description": "Complete required doctoral coursework",
                "order_hint": 1,
                "duration_months": 12,
                "confidence": 0.9
            },
            {
                "title": "Literature Review",
                "stage_type": "literature_review",
                "description": "Comprehensive review of existing research in the field",
                "order_hint": 2,
                "duration_months": 8,
                "confidence": 0.85
            },
            {
                "title": "Methodology Development",
                "stage_type": "methodology",
                "description": "Develop research methodology and obtain necessary approvals",
                "order_hint": 3,
                "duration_months": 6,
                "confidence": 0.8
            },
            {
                "title": "Data Collection",
                "stage_type": "data_collection",
                "description": "Collect primary research data",
                "order_hint": 4,
                "duration_months": 14,
                "confidence": 0.75
            },
            {
                "title": "Analysis",
                "stage_type": "analysis",
                "description": "Analyze collected data and draw conclusions",
                "order_hint": 5,
                "duration_months": 8,
                "confidence": 0.8
            },
            {
                "title": "Writing and Defense",
                "stage_type": "writing",
                "description": "Write dissertation and defend thesis",
                "order_hint": 6,
                "duration_months": 12,
                "confidence": 0.85
            }
        ],
        "milestones": [
            {"name": "Complete Coursework", "stage": "Coursework", "is_critical": True, "milestone_type": "academic"},
            {"name": "Pass Qualifying Examination", "stage": "Coursework", "is_critical": True, "milestone_type": "examination"},
            {"name": "Complete Literature Review", "stage": "Literature Review", "is_critical": False, "milestone_type": "deliverable"},
            {"name": "Proposal Defense", "stage": "Methodology Development", "is_critical": True, "milestone_type": "examination"},
            {"name": "Complete Data Collection", "stage": "Data Collection", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Complete Analysis", "stage": "Analysis", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Submit Dissertation Draft", "stage": "Writing and Defense", "is_critical": True, "milestone_type": "deliverable"},
            {"name": "Final Dissertation Defense", "stage": "Writing and Defense", "is_critical": True, "milestone_type": "examination"}
        ],
        "dependencies": [
            {"dependent": "Pass Qualifying Examination", "depends_on": "Complete Coursework", "type": "finish_to_start"},
            {"dependent": "Proposal Defense", "depends_on": "Complete Literature Review", "type": "finish_to_start"},
            {"dependent": "Complete Data Collection", "depends_on": "Proposal Defense", "type": "finish_to_start"},
            {"dependent": "Complete Analysis", "depends_on": "Complete Data Collection", "type": "finish_to_start"},
            {"dependent": "Submit Dissertation Draft", "depends_on": "Complete Analysis", "type": "finish_to_start"},
            {"dependent": "Final Dissertation Defense", "depends_on": "Submit Dissertation Draft", "type": "finish_to_start"}
        ]
    }
}


# =============================================================================
# Discipline Aliases for Fuzzy Matching
# =============================================================================

DISCIPLINE_ALIASES: Dict[str, str] = {
    # Computer Science
    "computer science": "computer_science",
    "cs": "computer_science",
    "computing": "computer_science",
    "informatics": "computer_science",
    "software engineering": "computer_science",
    "artificial intelligence": "computer_science",
    "machine learning": "computer_science",
    "data science": "computer_science",
    "computer engineering": "computer_science",

    # Biology
    "biology": "biology",
    "biological sciences": "biology",
    "biochemistry": "biology",
    "molecular biology": "biology",
    "genetics": "biology",
    "microbiology": "biology",
    "neuroscience": "biology",
    "biomedical sciences": "biology",
    "cell biology": "biology",
    "ecology": "biology",
    "evolutionary biology": "biology",

    # Psychology
    "psychology": "psychology",
    "cognitive psychology": "psychology",
    "clinical psychology": "psychology",
    "developmental psychology": "psychology",
    "social psychology": "psychology",
    "behavioral science": "psychology",
    "neuroscience": "psychology",

    # Engineering
    "engineering": "engineering",
    "mechanical engineering": "engineering",
    "electrical engineering": "engineering",
    "civil engineering": "engineering",
    "chemical engineering": "engineering",
    "aerospace engineering": "engineering",
    "materials science": "engineering",
    "biomedical engineering": "engineering",
    "environmental engineering": "engineering",

    # Humanities
    "humanities": "humanities",
    "history": "humanities",
    "philosophy": "humanities",
    "english": "humanities",
    "literature": "humanities",
    "linguistics": "humanities",
    "classics": "humanities",
    "art history": "humanities",
    "religious studies": "humanities",
    "cultural studies": "humanities",
    "anthropology": "humanities",

    # Business
    "business": "business",
    "business administration": "business",
    "management": "business",
    "marketing": "business",
    "finance": "business",
    "accounting": "business",
    "economics": "business",
    "organizational behavior": "business",
    "operations management": "business",
    "mba": "business",

    # Medicine
    "medicine": "medicine",
    "medical sciences": "medicine",
    "clinical research": "medicine",
    "public health": "medicine",
    "epidemiology": "medicine",
    "health sciences": "medicine",
    "nursing": "medicine",
    "pharmacy": "medicine",
    "dentistry": "medicine",
}


# =============================================================================
# Public Functions
# =============================================================================

def get_template(discipline: str) -> Dict[str, Any]:
    """
    Get a timeline template for the given discipline.

    Uses fuzzy matching to find the closest matching template.
    Falls back to generic template if no good match found.

    Args:
        discipline: Field of study (e.g., "Computer Science", "biology", "History")

    Returns:
        Template dictionary with stages, milestones, durations, dependencies
    """
    if not discipline:
        return TEMPLATES["generic"].copy()

    discipline_lower = discipline.lower().strip()

    # Direct alias lookup
    if discipline_lower in DISCIPLINE_ALIASES:
        template_key = DISCIPLINE_ALIASES[discipline_lower]
        return TEMPLATES[template_key].copy()

    # Fuzzy matching against aliases
    best_match = None
    best_score = 0.0

    for alias, template_key in DISCIPLINE_ALIASES.items():
        # Check substring containment
        if alias in discipline_lower or discipline_lower in alias:
            return TEMPLATES[template_key].copy()

        # Check word overlap
        alias_words = set(alias.split())
        discipline_words = set(discipline_lower.split())
        overlap = len(alias_words & discipline_words)
        if overlap > 0:
            score = overlap / max(len(alias_words), len(discipline_words))
            if score > best_score:
                best_score = score
                best_match = template_key

        # Sequence matching
        ratio = SequenceMatcher(None, discipline_lower, alias).ratio()
        if ratio > best_score:
            best_score = ratio
            best_match = template_key

    # Require at least 40% match
    if best_match and best_score >= 0.4:
        return TEMPLATES[best_match].copy()

    # Fallback to generic
    return TEMPLATES["generic"].copy()


def get_all_disciplines() -> List[str]:
    """
    Get list of all available discipline templates.

    Returns:
        List of discipline names
    """
    return [t["discipline"] for t in TEMPLATES.values()]


def get_template_by_key(key: str) -> Optional[Dict[str, Any]]:
    """
    Get a template by its exact key.

    Args:
        key: Template key (e.g., "computer_science", "biology")

    Returns:
        Template dictionary or None if not found
    """
    return TEMPLATES.get(key, {}).copy() if key in TEMPLATES else None
