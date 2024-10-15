# quiz_generator.py
import os
import json
import random
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Define objectives for each topic
objectives = {
    'Describe cloud concepts': [
        {
            'objective': 'Describe the different types of cloud services available',
            'sub_objectives': [
                'Describe Microsoft software as a service (SaaS), infrastructure as a service (IaaS), and platform as a service (PaaS) concepts and use cases',
                'Describe differences between Office 365 and Microsoft 365'
            ]
        },
        {
            'objective': 'Describe the benefits of and considerations for using cloud, hybrid, or on-premises services',
            'sub_objectives': [
                'Describe public, private, and hybrid cloud models',
                'Compare costs and advantages of cloud, hybrid, and on-premises services',
                'Describe the concept of hybrid work and flexible work'
            ]
        },
    ],
    'Describe Microsoft 365 apps and services': [
        {
            'objective': 'Describe productivity solutions of Microsoft 365',
            'sub_objectives': [
                'Describe the core productivity capabilities and benefits of Microsoft 365 including Microsoft Outlook and Microsoft Exchange, Microsoft 365 apps, and OneDrive',
                'Describe core Microsoft 365 Apps including Microsoft Word, Excel, PowerPoint, Outlook, and OneNote',
                'Describe work management capabilities of Microsoft 365 including Microsoft Project, Planner, Bookings, Forms, Lists, and To Do'
            ]
        },
        {
            'objective': 'Describe collaboration solutions of Microsoft 365',
            'sub_objectives': [
                'Describe the collaboration benefits and capabilities of Microsoft 365 including Microsoft Exchange, Outlook, SharePoint, OneDrive, and Stream',
                'Describe the collaboration benefits and capabilities of Microsoft Teams and Teams Phone',
                'Describe the Microsoft Viva apps',
                'Describe the ways that you can extend Microsoft Teams by using collaborative apps'
            ]
        },
        {
            'objective': 'Describe endpoint modernization, management concepts, and deployment options in Microsoft 365',
            'sub_objectives': [
                'Describe the endpoint management capabilities of Microsoft 365 including Microsoft Intune (Configuration Manager and co-management, Endpoint Analytics, and Windows Autopilot)',
                'Compare the differences between Windows 365 and Azure Virtual Desktop',
                'Describe the deployment and release models for Windows-as-a-Service (WaaS) including deployment rings',
                'Identify deployment and update channels for Microsoft 365 Apps'
            ]
        },
        {
            'objective': 'Describe analytics capabilities of Microsoft 365',
            'sub_objectives': [
                'Describe the capabilities of Viva Insights',
                'Describe the capabilities of the Microsoft 365 Admin center and Microsoft 365 user portal',
                'Describe the reports available in the Microsoft 365 Admin center and other admin centers'
            ]
        }
    ],
    'Describe security, compliance, privacy, and trust in Microsoft 365': [
        {
            'objective': 'Describe identity and access management solutions of Microsoft 365',
            'sub_objectives': [
                'Describe the identity and access management capabilities of Microsoft Entra ID',
                'Describe cloud identity, on-premises identity, and hybrid identity concepts',
                'Describe how Microsoft uses methods such as multi-factor authentication (MFA), self-service password reset (SSPR), and conditional access, to keep identities, access, and data secure'
            ]
        },
        {
            'objective': 'Describe threat protection solutions of Microsoft 365',
            'sub_objectives': [
                'Describe Microsoft Defender XDR, Defender for Endpoint, Defender for Office 365, Defender for Identity, Defender for Cloud Apps, and the Microsoft Defender Portal',
                'Describe Microsoft Secure Score benefits and capabilities',
                'Describe how Microsoft 365 addresses the most common types of threats against endpoints, applications, and identities'
            ]
        },
        {
            'objective': 'Describe trust, privacy, risk, and compliance solutions of Microsoft 365',
            'sub_objectives': [
                'Describe the Zero Trust Model',
                'Describe Microsoft Purview compliance solutions such as insider risk, auditing, and eDiscovery',
                'Describe Microsoft Purview Information Protection features such as sensitivity labels and data loss prevention',
                'Describe how Microsoft supports data residency to ensure regulatory compliance',
                'Describe the capabilities and benefits of Microsoft Priva'
            ]
        },
    ],
    'Describe Microsoft 365 pricing, licensing, and support': [
        {
            'objective': 'Identify Microsoft 365 pricing and billing management options',
            'sub_objectives': [
                'Describe the pricing model for Microsoft cloud services including enterprise agreements, cloud solution providers, and direct billing',
                'Describe available billing and bill management options including billing frequency and methods of payment'
            ]
        },
        {
            'objective': 'Identify licensing options available in Microsoft 365',
            'sub_objectives': [
                'Describe license management',
                'Describe the differences between base licensing and add-on licensing'
            ]
        },
        {
            'objective': 'Identify support options for Microsoft 365 services',
            'sub_objectives': [
                'Describe how to create a support request for Microsoft 365 services',
                'Describe support options for Microsoft 365 services',
                'Describe service-level agreements (SLAs) including service credits',
                'Determine service health status by using the Microsoft 365 admin center or the Microsoft Entra admin center'
            ]
        },
    ],
}

# Initialize tracking dictionaries
used_objectives = {topic: set() for topic in objectives.keys()}
used_sub_objectives = {}

def select_objective(topic):
    if topic == 'All Topics':
        topic = random.choice(list(objectives.keys()))
    
    topic_objectives = objectives[topic]
    unused_objectives = [obj for idx, obj in enumerate(topic_objectives) if idx not in used_objectives[topic]]

    if not unused_objectives:
        used_objectives[topic] = set()
        unused_objectives = topic_objectives

    selected_objective = random.choice(unused_objectives)
    objective_index = topic_objectives.index(selected_objective)
    used_objectives[topic].add(objective_index)
    objective_text = selected_objective['objective']

    # Track sub-objectives
    if objective_text not in used_sub_objectives:
        used_sub_objectives[objective_text] = set()

    sub_objectives = selected_objective.get('sub_objectives', [])
    unused_sub_objectives = [mo for idx, mo in enumerate(sub_objectives) if idx not in used_sub_objectives[objective_text]]

    if not unused_sub_objectives:
        used_sub_objectives[objective_text] = set()
        unused_sub_objectives = sub_objectives

    selected_sub_objective = None
    if unused_sub_objectives:
        selected_sub_objective = random.choice(unused_sub_objectives)
        sub_objective_index = sub_objectives.index(selected_sub_objective)
        used_sub_objectives[objective_text].add(sub_objective_index)

    return topic, objective_text, selected_sub_objective

def generate_prompt(difficulty, question_type, topic, exam_code="MS-900"):
    """
    Generate a prompt for the OpenAI API based on the difficulty, question type, and topic.
    """
    # Base prompt
    base_prompt = f"Generate a {difficulty} {question_type} question for the {exam_code} exam"
    
    # Add topic, objective, and sub-objective
    selected_topic, objective_text, sub_objective = select_objective(topic)
    base_prompt += f" focusing on '{selected_topic}'"
    
    if sub_objective:
        base_prompt += f", specifically covering the objective '{objective_text}' and the subtopic '{sub_objective}'"
    else:
        base_prompt += f", specifically covering the objective '{objective_text}'"

    # Continue building the prompt based on question type
    if question_type == 'multiple-choice':
        prompt = (
            f"{base_prompt} with 4 options. Format the answer as a JSON object with these fields: "
            "'question', 'options' (a list of options), "
            "'correct_answer' (integer index starting from 1), "
            "and 'explanations' (a dict mapping option numbers to explanations)."
            "\nExample:"
            "\n{"
            "\n  'question': 'Your company is planning to migrate to Microsoft Azure and Microsoft 365. You are required to identify a cloud service that allows for website hosting. Which of the following is the model you should choose?',"
            "\n  'options': ['Software as a Service (SaaS)', 'Platform as a Service (PaaS)', 'Infrastructure as a Service (IaaS)', 'Container as a Service (CaaS)'],"
            "\n  'correct_answer': 2,"
            "\n  'explanations': {"
            "\n    '1': 'Software as a Service (SaaS) provides access to software applications over the internet, but does not typically offer direct website hosting capabilities. Examples include Microsoft 365 apps.',"
            "\n    '2': 'Platform as a Service (PaaS) is the correct choice for website hosting. It provides a platform allowing customers to develop, run, and manage applications without the complexity of building and maintaining the infrastructure. Azure App Service is an example of PaaS that supports website hosting.',"
            "\n    '3': 'Infrastructure as a Service (IaaS) provides virtualized computing resources over the internet. While it can be used for website hosting, it requires more management and configuration compared to PaaS, making it less suitable for this specific requirement.',"
            "\n    '4': 'Container as a Service (CaaS) is a cloud service model that allows users to upload, organize, run, scale, and manage containers. While it can be used for hosting websites, it's not typically the primary choice for simple website hosting scenarios.'"
            "\n  }"
            "\n}"
        )
    elif question_type == 'true/false':
        prompt = (
            f"{base_prompt}. Format the answer as a JSON object with fields: "
            "'question', 'options' (['True', 'False']), "
            "'correct_answer' (1 for True, 2 for False), "
            "and 'explanations' (dict mapping option numbers to explanations)."
            "\nExample:"
            "\n{"
            "\n  'question': 'Microsoft Planner can be used to provide customized appointments that customers can schedule on a website.',"
            "\n  'options': ['True', 'False'],"
            "\n  'correct_answer': 2,"
            "\n  'explanations': {"
            "\n    '1': 'This is incorrect. Microsoft Planner is a task management tool designed for team collaboration and project management. It does not have built-in functionality for customer appointment scheduling on websites.',"
            "\n    '2': 'This is correct. Microsoft Planner is not designed for customer appointment scheduling. For this purpose, Microsoft offers a different tool called Microsoft Bookings, which is specifically designed to allow customers to schedule appointments through a web interface.'"
            "\n  }"
            "\n}"
        )
    elif question_type == 'multi-response':
        prompt = (
            f"{base_prompt} with 4-6 options, where multiple options may be correct. Format the answer as a JSON object with fields: "
            "'question', 'options' (list of options), "
            "'correct_answers' (list of integer indices starting from 1), "
            "and 'explanations' (dict mapping option numbers to explanations). "
            "Be sure to specify that multiple options may be correct. In some cases you will specify the exact number of correct options in the question or requirements."
            "\nExample:"
            "\n{"
            "\n  'question': 'A company plans to migrate on-premises infrastructure to the cloud. What are three benefits of migrating to the cloud? Each correct answer presents a complete solution.',"
            "\n  'options': ['Reduce configuration requirements on desktop computers.', 'Reduce on-site network latency.', 'Automate data backup and disaster recovery.', 'Scale and extend applications.', 'Eliminate the cost of buying server hardware.'],"
            "\n  'correct_answers': [3, 4, 5],"
            "\n  'explanations': {"
            "\n    '1': 'This is incorrect. While cloud migration can simplify some aspects of IT management, it typically does not significantly reduce configuration requirements on desktop computers. Desktop management is often handled separately from cloud infrastructure.',"
            "\n    '2': 'This is incorrect. Migrating to the cloud does not inherently reduce on-site network latency. In fact, it may introduce additional latency for accessing cloud-based resources, depending on the network configuration and distance to the cloud data centers.',"
            "\n    '3': 'This is correct. Cloud services often provide built-in tools and features for automating data backup and disaster recovery processes, improving data protection and business continuity.',"
            "\n    '4': 'This is correct. Cloud platforms offer scalability, allowing businesses to easily scale up or down their resources based on demand. They also provide services and tools that enable the extension of applications with new features and capabilities.',"
            "\n    '5': 'This is correct. By migrating to the cloud, companies can reduce or eliminate the need to purchase and maintain physical server hardware, as the cloud provider manages the underlying infrastructure.'"
            "\n  }"
            "\n}"
        )
    else:
        prompt = ""
    return prompt, selected_topic, objective_text, sub_objective

def generate_question(difficulty, topic, exam_code="MS-900", model = "gpt-4o", temperature=0.7):
    """
    Generate a quiz question for the MS-900 exam based on the given difficulty.
    """
    
    sys_prompt = (
        f"You are a knowledgeable assistant that understands the {exam_code} exam topics and structure. "
        f"You will act as a quiz generator for the {exam_code} exam, and your questions should closely follow the format and content of the actual exam. "
        "Ensure that the questions are varied, non-repetitive, and cover a wide range of topics within the exam scope. "
        "Pay attention to the following guidelines:\n"
        "1. Questions should be clear, concise, and unambiguous.\n"
        "2. Use appropriate terminology and concepts relevant to the exam.\n"
        "3. Ensure that incorrect options (distractors) are plausible but clearly incorrect.\n"
        "4. Provide detailed explanations for both correct and incorrect answers.\n"
        "5. Align the difficulty level with the specified requirement (easy, medium, hard).\n"
        "6. For multi-response questions, clearly indicate that multiple options may be correct.\n"
        "7. Avoid using absolute terms like 'always' or 'never' unless specifically pointing to a correct or incorrect answer.\n"
        "8. Ensure that the correct answer(s) fully address the question asked.\n"
        "9. Use real-world scenarios when appropriate to test practical understanding.\n"
        "10. Adhere strictly to the JSON format specified in the prompt."
    )
    
    # Randomly select a question type
    question_types = ['multiple-choice', 'true/false', 'multi-response']
    question_type = random.choice(question_types)
    
    # Generate the prompt and get the selected topic, objective, and sub-objective
    prompt, selected_topic, objective, sub_objective = generate_prompt(difficulty, question_type, topic, exam_code)
    
    if not prompt:
        logging.error("Invalid question type selected.")
        return None
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )

        # Get the content of the API response
        content = response.choices[0].message.content
        
        # Clean and extract JSON segment
        start = content.find('{')
        end = content.rfind('}') + 1
        cleaned_content = content[start:end].strip()
        
        # Try to parse the cleaned JSON content
        question_data = json.loads(cleaned_content)
        
        # Add topic and objective information to the question data
        question_data['topic'] = selected_topic
        question_data['objective'] = objective
        question_data['sub_objective'] = sub_objective
        
        return question_data
    
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
    except Exception as e:
        logging.error(f"Error fetching the question: {e}")
    
    return None