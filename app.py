from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from quiz import Quiz
from web_search import get_official_documentation
import os
import logging
from threading import Thread
from queue import Queue

app = Flask(__name__)
app.secret_key = os.urandom(24)
logging.basicConfig(level=logging.DEBUG)

question_queue = Queue()

def serialize_quiz(quiz):
    return {
        'num_questions': quiz.num_questions,
        'difficulty': quiz.difficulty,
        'topic': quiz.topic,
        'score': quiz.score,
        'current_question': quiz.current_question,
        'user_performance': quiz.user_performance,
        'questions': quiz.questions
    }

def deserialize_quiz(data):
    quiz = Quiz(data['num_questions'], data['difficulty'], data['topic'])
    quiz.score = data['score']
    quiz.current_question = data['current_question']
    quiz.user_performance = data['user_performance']
    quiz.questions = data['questions']
    return quiz

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        num_questions = int(request.form['num_questions'])
        difficulty = request.form['difficulty']
        topic = request.form['topic']
        quiz = Quiz(num_questions, difficulty, topic)
        session['quiz'] = serialize_quiz(quiz)
        return redirect(url_for('question'))
    return render_template('index.html')

def generate_next_question(quiz):
    new_question = quiz.generate_next_question()
    if new_question:
        question_queue.put(new_question)

@app.route('/question', methods=['GET', 'POST'])
def question():
    if 'quiz' not in session:
        return redirect(url_for('index'))
    
    quiz = deserialize_quiz(session['quiz'])
    
    if request.method == 'POST':
        user_answer = request.form.getlist('answer')
        user_answer = [int(ans) for ans in user_answer]
        is_correct, partially_correct = quiz.check_answer(user_answer)
        
        feedback = quiz.get_feedback()
        logging.debug(f"Raw feedback: {feedback}")
        
        search_query = f"{feedback.get('topic', '')} {feedback.get('objective', '')} {feedback.get('sub_objective', '')}"
        doc_link, doc_snippet = get_official_documentation(search_query, feedback.get('sub_objective', ''))
        
        feedback_data = {
            'is_correct': is_correct,
            'partially_correct': partially_correct,
            'correct_answer': feedback['correct_answer'],
            'explanation': feedback['explanation'],
            'doc_link': doc_link,
            'doc_snippet': doc_snippet
        }
        
        logging.debug(f"Prepared feedback data: {feedback_data}")
        
        quiz.current_question += 1
        session['quiz'] = serialize_quiz(quiz)
        
        return jsonify({
            'feedback': feedback_data,
            'is_last_question': quiz.current_question >= quiz.num_questions,
            'result_url': url_for('result') if quiz.current_question >= quiz.num_questions else None
        })
    
    # GET request
    if not quiz.questions or quiz.current_question >= len(quiz.questions):
        # Generate a new question if needed
        new_question = quiz.generate_next_question()
        if new_question:
            quiz.questions.append(new_question)
            session['quiz'] = serialize_quiz(quiz)
    
    question_data = quiz.get_current_question()
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'question': question_data})
    else:
        return render_template('question.html', quiz=quiz, question=question_data, chr=chr)

@app.route('/next_question', methods=['GET'])
def next_question():
    if 'quiz' not in session:
        return redirect(url_for('index'))
    
    quiz = deserialize_quiz(session['quiz'])
    
    if quiz.current_question >= quiz.num_questions:
        return jsonify({'redirect': url_for('result')})
    
    if not quiz.questions or quiz.current_question >= len(quiz.questions):
        new_question = quiz.generate_next_question()
        if new_question:
            quiz.questions.append(new_question)
            session['quiz'] = serialize_quiz(quiz)
    
    question_data = quiz.get_current_question()
    return jsonify({'question': question_data})

@app.route('/result')
def result():
    if 'quiz' not in session:
        return redirect(url_for('index'))
    
    quiz = deserialize_quiz(session['quiz'])
    
    return render_template('result.html', quiz=quiz)

if __name__ == '__main__':
    app.run(debug=True)