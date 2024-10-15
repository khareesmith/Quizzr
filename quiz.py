# quiz.py
from quiz_generator import generate_question

class Quiz:
    def __init__(self, num_questions, difficulty, topic):
        self.num_questions = num_questions
        self.difficulty = difficulty
        self.topic = topic
        self.score = 0
        self.current_question = 0
        self.user_performance = []
        self.questions = []

    def generate_questions(self):
        if not self.questions:
            self.questions = [generate_question(self.difficulty, self.topic) for _ in range(self.num_questions)]
    
    def generate_next_question(self):
        if len(self.questions) < self.num_questions:
            question = generate_question(self.difficulty, self.topic)
            if question:
                return question
        return None

    def get_current_question(self):
        if self.current_question < len(self.questions):
            return self.questions[self.current_question]
        return None

    def check_answer(self, user_answer):
        if self.current_question >= len(self.questions):
            return False, False

        question_data = self.questions[self.current_question]
        is_correct = False
        partially_correct = False

        if 'correct_answers' in question_data:  # Multi-response question
            correct_answers = set(question_data['correct_answers'])
            user_answers = set(user_answer)
            is_correct = user_answers == correct_answers
            partially_correct = bool(user_answers & correct_answers) and not is_correct
        else:  # Single-response question
            correct_answer = question_data['correct_answer']
            is_correct = user_answer[0] == correct_answer

        if is_correct:
            self.score += 1
        elif partially_correct:
            self.score += 0.5

        self.user_performance.append({
            'question': question_data['question'],
            'user_answer': user_answer,
            'correct_answer': question_data.get('correct_answer') or question_data.get('correct_answers'),
            'is_correct': is_correct,
            'partially_correct': partially_correct
        })

        return is_correct, partially_correct

    def get_feedback(self):
        if self.current_question >= len(self.questions):
            return None

        question_data = self.questions[self.current_question]
        if 'correct_answers' in question_data:
            correct_answer = question_data['correct_answers']
            explanation = [question_data['explanations'].get(str(ans)) for ans in correct_answer]
        else:
            correct_answer = question_data['correct_answer']
            explanation = question_data['explanations'].get(str(correct_answer))

        return {
            'correct_answer': correct_answer,
            'explanation': explanation,
            'topic': question_data.get('topic', "Unknown"),
            'objective': question_data.get('objective', "Unknown"),
            'sub_objective': question_data.get('sub_objective', "Unknown")
    }

    def show_performance_summary(self):
        topic_performance = {}
        for question in self.user_performance:
            topic = question['question'].split(':')[0]  # Assuming topics are prefixed in questions
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0}
            topic_performance[topic]['total'] += 1
            if question['is_correct']:
                topic_performance[topic]['correct'] += 1

        summary = []
        for topic, performance in topic_performance.items():
            percentage = (performance['correct'] / performance['total']) * 100
            summary.append(f"{topic}: {percentage:.2f}% correct ({performance['correct']}/{performance['total']})")

        return summary

    def get_weak_areas(self):
        topic_performance = {}
        for question in self.user_performance:
            topic = question['question'].split(':')[0]  # Assuming topics are prefixed in questions
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0}
            topic_performance[topic]['total'] += 1
            if question['is_correct']:
                topic_performance[topic]['correct'] += 1

        weak_areas = [topic for topic, perf in topic_performance.items() if (perf['correct'] / perf['total']) < 0.7]
        return weak_areas