# main.py
from quiz import Quiz
from web_search import test_documentation_retrieval

def main():
    print("Welcome to the MS-900 Quiz!")
    num_questions = int(input("How many questions would you like to answer? "))
    difficulty = input("Select difficulty level (easy, medium, hard): ").lower()
    
    # List of topics
    topics = [
        'Describe cloud concepts',
        'Describe Microsoft 365 apps and services',
        'Describe security, compliance, privacy, and trust in Microsoft 365',
        'Describe Microsoft 365 pricing, licensing, and support',
        'All Topics'
    ]
    
    # Display topics to the user
    print("\nSelect a topic:")
    for idx, topic in enumerate(topics, 1):
        print(f"{idx}. {topic}")
    
    # Get user selection
    topic_choice = int(input("Enter the number corresponding to your choice: "))
    
    # Validate input
    if 1 <= topic_choice <= len(topics):
        selected_topic = topics[topic_choice - 1]
    else:
        print("Invalid selection. Defaulting to 'All Topics'.")
        selected_topic = 'All Topics'
    
    quiz = Quiz(num_questions, difficulty, selected_topic)
    quiz.start()

if __name__ == "__main__":
    main()